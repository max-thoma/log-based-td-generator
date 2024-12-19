import os
import statistics
from collections import Counter
from typing import List

import dotenv
import numpy as np
from numpy import dot
from pydantic import BaseModel, RootModel, Field
from pydantic_core import from_json
from rapidfuzz import fuzz
from rouge import Rouge

from experiment import ExperimentResultList
from td_generator.td import ThingDescription

dotenv.load_dotenv()
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def get_embedding_similarity(src, dst, model="text-embedding-3-small"):
    """
    Inspired from https://platform.openai.com/docs/guides/embeddings
    """
    src = src.replace("\n", " ")
    dst = dst.replace("\n", " ")
    src_embedding = client.embeddings.create(input=[src], model=model).data[0].embedding
    dst_embedding = client.embeddings.create(input=[dst], model=model).data[0].embedding

    return dot(src_embedding, dst_embedding)


class DescriptiveEquivalenceScore(BaseModel):
    rougel_r: List[float] = Field(default_factory=list)
    rougel_p: List[float] = Field(default_factory=list)
    rougel_f: List[float] = Field(default_factory=list)
    embedding: List[float] = Field(default_factory=list)
    fuzzy_ratio: List[float] = Field(default_factory=list)

    def __add__(self, other):
        return DescriptiveEquivalenceScore(
            rougel_r=self.rougel_r + other.rougel_r,
            rougel_p=self.rougel_p + other.rougel_p,
            rougel_f=self.rougel_f + other.rougel_f,
            embedding=self.embedding + other.embedding,
            fuzzy_ratio=self.fuzzy_ratio + other.fuzzy_ratio,
        )

    def calculate_stat(self, stat_fn):
        return DescriptiveEquivalenceScore(
            rougel_r=[stat_fn(self.rougel_r)],
            rougel_p=[stat_fn(self.rougel_p)],
            rougel_f=[stat_fn(self.rougel_f)],
            embedding=[stat_fn(self.embedding)],
            fuzzy_ratio=[stat_fn(self.fuzzy_ratio)],
        )


class DescriptiveEquivalence(BaseModel):
    title: DescriptiveEquivalenceScore = DescriptiveEquivalenceScore()
    description: DescriptiveEquivalenceScore = DescriptiveEquivalenceScore()
    thing_type: DescriptiveEquivalenceScore = DescriptiveEquivalenceScore()
    affordance_name: DescriptiveEquivalenceScore = DescriptiveEquivalenceScore()
    affordance_description: DescriptiveEquivalenceScore = DescriptiveEquivalenceScore()

    def __add__(self, other):
        return DescriptiveEquivalence(
            title=self.title + other.title,
            description=self.description + other.description,
            thing_type=self.thing_type + other.thing_type,
            affordance_name=self.affordance_name + other.affordance_name,
            affordance_description=self.affordance_description
            + other.affordance_description,
        )

    def calculate_stat(self, stat_fn):
        return DescriptiveEquivalence(
            title=self.title.calculate_stat(stat_fn),
            description=self.description.calculate_stat(stat_fn),
            thing_type=self.thing_type.calculate_stat(stat_fn),
            affordance_name=self.affordance_name.calculate_stat(stat_fn),
            affordance_description=self.affordance_description.calculate_stat(stat_fn),
        )


class DescriptiveEquivalenceList(RootModel):
    root: List[DescriptiveEquivalence]


def list_to_str(lst):
    s = ""
    for element in lst:
        s += f"{element} "
    return s.removesuffix(" ")


def extract_affordance_name(td: ThingDescription):
    names = []
    names.extend(list(td.properties.keys()))
    names.extend(list(td.events.keys()))
    names.extend(list(td.actions.keys()))

    names.sort()
    return list_to_str(names)


def extract_affordance_description(td: ThingDescription):
    descriptions = []
    for affordance in [td.properties, td.events, td.actions]:
        for val in affordance.values():
            descriptions.append(val.description)

    descriptions.sort()
    return list_to_str(descriptions)


def calculate_score(
    reference_td: ThingDescription, llm_td: ThingDescription
) -> DescriptiveEquivalence:
    compare_dict = {
        "title": (reference_td.title, llm_td.title),
        "description": (reference_td.description, llm_td.description),
        "thing_type": (reference_td.type, llm_td.type),
        "affordance_name": (
            extract_affordance_name(reference_td),
            extract_affordance_name(llm_td),
        ),
        "affordance_description": (
            extract_affordance_description(reference_td),
            extract_affordance_description(llm_td),
        ),
    }
    score_dict = {}

    rouge = Rouge()
    for key, (ref, llm) in compare_dict.items():
        # print(f"'{reference_td.id}', '{key}', '{ref}', '{llm}'")
        if ref == "" or llm == "":
            DescriptiveEquivalenceScore(
                rougel_r=[0.0],
                rougel_p=[0.0],
                rougel_f=[0.0],
                embedding=[0.0],
                fuzzy_ratio=[0.0],
            )
        else:
            rouge_score = rouge.get_scores(ref, llm)[0]["rouge-l"]
            score = DescriptiveEquivalenceScore(
                rougel_r=[rouge_score["r"]],
                rougel_p=[rouge_score["p"]],
                rougel_f=[rouge_score["f"]],
                embedding=[get_embedding_similarity(ref, llm)],
                fuzzy_ratio=[fuzz.ratio(ref, llm) / 100],
            )
        score_dict[key] = score

    return DescriptiveEquivalence(**score_dict)


def calculate_scores(exp_file_name):
    with open(exp_file_name) as exp_file:
        exp_dict = from_json(exp_file.read())
    exp_list = ExperimentResultList(**exp_dict)
    score_lst = []
    for result in exp_list.results:
        for llm_td in result.llm_td_lst:
            score_lst.append(calculate_score(result.base_td, llm_td))

    with open(f"out/descriptive_{exp_file_name}", "w") as json_results:
        json_results.write(
            DescriptiveEquivalenceList(score_lst).model_dump_json(indent=2)
        )


def analyze_scores(pre_calc_file):
    with open(pre_calc_file, "r") as results:
        results_dict = from_json(results.read())
    score_lst = DescriptiveEquivalenceList(results_dict)
    score_lst = score_lst.root
    accumulated_scores = DescriptiveEquivalence()

    for score in score_lst:
        accumulated_scores += score

    print(accumulated_scores)
    print(accumulated_scores.calculate_stat(np.mean))
    print(accumulated_scores.calculate_stat(np.average))
    print(accumulated_scores.calculate_stat(statistics.harmonic_mean))
    print(accumulated_scores.calculate_stat(np.max).affordance_description)
    avg = accumulated_scores.calculate_stat(np.mean)
    plot = f"""
        % rougel prose-like from {pre_calc_file}
        \\addplot coordinates {{
            ({avg.description.rougel_f[0]},description)
            ({avg.affordance_description.rougel_f[0]},affordance description)
        }};
         
        % embedding prose-like from {pre_calc_file}
        \\addplot coordinates {{
            ({avg.description.embedding[0]},description)
            ({avg.affordance_description.embedding[0]},affordance description)
        }};
        
        % fuzzy match short and identifiers from {pre_calc_file}
        \\addplot coordinates {{
            ({avg.title.fuzzy_ratio[0]},title)
            ({avg.thing_type.fuzzy_ratio[0]},thing type)
            ({avg.affordance_name.fuzzy_ratio[0]},affordance name)
        }};
        
        % embedding short and identifiers from {pre_calc_file}
        \\addplot coordinates {{
            ({avg.title.embedding[0]},title)
            ({avg.thing_type.embedding[0]},thing type)
            ({avg.affordance_name.embedding[0]},affordance name)
        }};
"""
    print(plot)


def count_type(exp_file_name):
    with open(exp_file_name) as exp_file:
        exp_dict = from_json(exp_file.read())
    exp_list = ExperimentResultList(**exp_dict)
    count_type = Counter()
    for result in exp_list.results:
        for llm_td in result.llm_td_lst:
            count_type.update({llm_td.title})

    print(count_type)


if __name__ == "__main__":
    # calculate_scores("out/reuslts_gpt_4o_no_example_t4.json") #done
    # calculate_scores("out/reuslts_llama_no_example_t4.json") # done
    # calculate_scores("out/reuslts_gpt_4o_with_example_t4.json") # done
    calculate_scores("out/reuslts_llama_with_example_t4.json")
    analyze_scores("out/descriptive_out/reuslts_gpt_4o_no_example_t4.json")
    # analyze_scores("out/descriptive_out/reuslts_llama_no_example_t4.json")
    # analyze_scores("out/descriptive_out/reuslts_gpt_4o_with_example_t4.json")

    count_type("out/reuslts_llama_no_example_t4.json")
    count_type("out/reuslts_gpt_4o_no_example_t4.json")
