from collections import defaultdict
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from pydantic import BaseModel, RootModel, Field
from pydantic_core import from_json

from experiment import ExperimentResult, ExperimentResultList
from td_generator.td import ThingDescription, AffordanceType, AttributeType


class ComparisonResult(BaseModel):
    td_id: str  # only needed for easier debugging
    td_type: str  # only needed for better debugging
    name: str
    attribute_type: AttributeType
    yes: int = 0
    no: int = 0
    affordance_type: AffordanceType
    pass_at_k_score: dict = Field(default_factory=defaultdict)


class AccumulatedData(BaseModel):
    yes: int = 0
    no: int = 0
    total: int = 0
    percent: float = 0.0
    pass_at_k_scores: List[float] = Field(default_factory=list)


class ComparisonResultList(RootModel):
    root: List[ComparisonResult]


def pass_at_k(n, c, k):
    """
    form http://arxiv.org/abs/2107.03374
    :param n: total number of samples
    :param c: number of correct samples
    :param k: k in pass@$k$
    """
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))


def result_per_type(result_lst: ComparisonResultList, type_enum):
    result_lst = result_lst.root
    accumulated_data_dict = {}
    # Add a total entry for an oval statistic
    type_enum_list = [t.value for t in type_enum] + ["total"]

    for t in type_enum_list:
        accumulated_data_dict[t] = AccumulatedData()

    for r in result_lst:
        if type_enum is AffordanceType:
            t = r.affordance_type
        else:
            t = r.attribute_type

        accumulated_data_dict[t].yes += r.yes
        accumulated_data_dict[t].no += r.no
        accumulated_data_dict[t].total += r.no + r.yes

        accumulated_data_dict["total"].yes += r.yes
        accumulated_data_dict["total"].no += r.no
        accumulated_data_dict["total"].total += r.no + r.yes

    for t in type_enum_list:
        total = float(accumulated_data_dict[t].total)
        if total != 0:
            accumulated_data_dict[t].percent = (
                100.0 * accumulated_data_dict[t].yes / total
            )
        else:
            accumulated_data_dict[t].percent = 0.0

    for t in type_enum_list:
        n = accumulated_data_dict[t].total
        c = accumulated_data_dict[t].yes
        accumulated_data_dict[t].pass_at_k_scores = [
            pass_at_k(n, c, k) for k in range(1, 6)
        ]
    for t, val in accumulated_data_dict.items():
        print(f"{t}: {val.model_dump_json(indent=2)}")

    # pgf plot
    data, names = generate_pgf_data(accumulated_data_dict, type_enum_list)
    # pyplot
    # generate_pyplot(data, names)


def generate_pyplot(data, names):
    fig, ax = plt.subplots(figsize=(15, 5))
    p = ax.bar(names, data, width=0.5)
    ax.bar_label(p, label_type="center")
    ax.set_title("Passed tests per attribute type in percent")
    ax.legend()
    plt.ylim(0, 100)
    plt.show()


def generate_pgf_data(accumulated_data, names):
    data = [v.percent for v in accumulated_data.values()]

    print(f"% accuracy scores")
    print("\\addplot coordinates {")
    for name, val in zip(names, data):
        print(f"\t({name}, {int(round(val, 0))})")
    print("};")

    data_k = [v.pass_at_k_scores for v in accumulated_data.values()]
    for name, scores in zip(names, data_k):
        count = 1
        print(f"% pass@k score for {name}")
        print("\\addplot coordinates {")
        for score in scores:
            print(f"\t({count}, {score})")
            count += 1
        print("};")

    return data, names


def compare(
    comparison_td: ThingDescription,
    experiment_result: ExperimentResult,
    affordance_type: AffordanceType,
):
    results = []

    if affordance_type == AffordanceType.property:
        comparison_lst = comparison_td.properties.items()
    elif affordance_type == AffordanceType.event:
        comparison_lst = [
            (name, e.to_property()) for name, e in comparison_td.events.items()
        ]
    else:
        # Action
        comparison_lst = comparison_td.actions.items()

    for name, value in comparison_lst:
        if (
            affordance_type == AffordanceType.property
            or affordance_type == AffordanceType.event
        ):
            attribute_type = value.type
        else:
            # Action
            attribute_type = value.input.type

        comp_result = ComparisonResult(
            td_id=comparison_td.id,
            td_type=comparison_td.type,
            name=name,
            attribute_type=attribute_type,
            affordance_type=affordance_type,
            no=experiment_result.failed,  # If the LLM is unable to create a proper TD it's a fail per default.
        )

        for llm_td in experiment_result.llm_td_lst:
            if (
                affordance_type == AffordanceType.property
                or affordance_type == AffordanceType.event
            ):
                # A property in the base_td can be modeled as property or as event in the llm_td.
                # An event in the base_td can be modeled as property or as event in the llm_td.
                attribute_list = list(llm_td.properties.values())
                attribute_list.extend([e.to_property() for e in llm_td.events.values()])
            else:
                # Action
                attribute_list = list(llm_td.actions.values())

            if value in attribute_list:
                comp_result.yes += 1
            else:
                comp_result.no += 1

        total_comp = comp_result.no + comp_result.yes
        total_exp = experiment_result.failed + experiment_result.successful
        assert total_exp == total_comp
        # Calculate the pass@k metric
        for k in range(1, 6):
            comp_result.pass_at_k_score[k] = pass_at_k(total_comp, comp_result.yes, k)
        results.append(comp_result)

    return results


def analyze(file_name):
    with open(file_name) as exp_file:
        exp_dict = from_json(exp_file.read())
    exp_list = ExperimentResultList(**exp_dict)
    test_results = []
    for result in exp_list.results:
        base_td = result.base_td

        for affordance in AffordanceType:
            res = compare(
                comparison_td=base_td,
                experiment_result=result,
                affordance_type=AffordanceType(affordance),
            )
            test_results.extend(res)
    # print(ComparisonResultList(test_results).model_dump_json(indent=2))

    result_per_type(ComparisonResultList(test_results), AffordanceType)
    result_per_type(ComparisonResultList(test_results), AttributeType)

    yes_count = int()
    no_count = int()
    for result in exp_list.results:
        yes_count += result.successful
        no_count += result.failed
    print(
        f"Successfully generated: {yes_count}, failed attempts: {no_count}, Total: {yes_count + no_count}, Percent Sucessfull: {round(yes_count / (yes_count + no_count) * 100, 2)}"
    )


if __name__ == "__main__":
    # file_names = ["out/reuslts_llama.json", "out/reuslts_gpt.json"]
    file_names = ["out/reuslts_llama_with_example_t4.json"]

    for f in file_names:
        print("==============================")
        print(f)
        analyze(f)
        print("==============================")
