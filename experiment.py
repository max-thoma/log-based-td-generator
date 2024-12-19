import datetime
import logging
import os
import time
from pathlib import Path
from typing import List

import dotenv
import instructor
from openai import OpenAI
from pydantic import BaseModel

from td_generator import generate
from td_generator.mock import mock_thing_str
from td_generator.td import ThingDescription

logging.basicConfig(level=logging.INFO)
# logging.getLogger("instructor").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

# Set the experiment parameters here

RUNS_PER_TD = 10
MODEL = "gpt-4o"
# MODEL = "meta-llama-3.1-70b-instruct"
# MODEL = "llama3.1"
# MODEL = "llama3.1:70b"
# MODEL = "qwen2.5-coder:14b"
NUMBER_OF_RETRIES = 10
TEMPERATURE = 0.4


class ExperimentResult(BaseModel):
    base_td: ThingDescription
    llm_td_lst: List[ThingDescription]
    msg_log: str
    successful: int
    failed: int


class ExperimentResultList(BaseModel):
    model: str
    temperature: float
    number_of_retries: int
    number_of_loops: int
    time_elapsed: datetime.time
    results: List[ExperimentResult]


def instruct_llm(client, mqtt_log, model=MODEL, temperature=TEMPERATURE):
    # This is an example how to provide an example TD to the LLM (was not used for the paper)
    # example_file = open("example_td.json")
    # example_td = example_file.read()
    # prompt = f"This is an example Web of Things (WoT) Thing Description (TD), for AN UNRELATED(!) DEVICE: {example_td} Given the following MQTT message log. Create a Thing Description about this smart IoT device. Use the same exact topics as specified in the message log. As MQTT Broker use 'mqtt://broker.com:1883' only in the 'href'. Message log:\n{mqtt_log}"

    prompt = f"Given the following MQTT message log. Create a Thing Description about this smart IoT device. Use the same exact topics as specified in the message log. As MQTT Broker use 'mqtt://broker.com:1883' only in the 'href'. Message log:\n{mqtt_log}"

    try:
        model = client.chat.completions.create(
            model=MODEL,
            response_model=ThingDescription,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_retries=NUMBER_OF_RETRIES,
            temperature=TEMPERATURE,
        )
    except Exception as e:
        logger.error(f"Error occurred with LLM {e}")
        model = None
    return model


if __name__ == "__main__":
    start_program = time.time()

    out_path = Path("out")
    out_path.mkdir(exist_ok=True)
    # Choose an OpenAI compatible backend
    client = instructor.from_openai(
        # OpenAI(api_key="asdf", base_url="http://localhost:11434/v1"),
        OpenAI(api_key=os.environ.get("OPENAI_API_KEY")),
        mode=instructor.Mode.JSON,
    )

    things_list = generate.thing_list()
    progress_counter = 0
    number_of_steps = RUNS_PER_TD * len(things_list)

    experiment_lst = []

    for thing in things_list:
        td = thing.td()

        # each message log is random
        msg_log = mock_thing_str(td)

        llm_td_lst = []
        success_count = 0
        fail_count = 0
        for _ in range(RUNS_PER_TD):
            llm_out = instruct_llm(client, msg_log)
            if llm_out is not None:
                llm_td_lst.append(llm_out)
                success_count += 1
            else:
                logger.error("A faulty model was returned")
                fail_count += 1

            progress_counter += 1
            experiment_time = time.time() - start_program
            logger.info(
                f"Elapsed time {round(experiment_time, 2)} [s], {progress_counter} of {number_of_steps}, TD have been created. Estimated remaining time: {round(((number_of_steps - progress_counter) * (experiment_time/progress_counter))/60, 0)} [min]"
            )

        assert success_count + fail_count == RUNS_PER_TD
        experiment_lst.append(
            ExperimentResult(
                base_td=td,
                llm_td_lst=llm_td_lst,
                msg_log=msg_log,
                successful=success_count,
                failed=fail_count,
            )
        )

    experiment_time = time.time() - start_program
    logger.info(f"Elapsed time {experiment_time}")

    with open(f"out/reuslts_{datetime.datetime.now()}.json", "w") as out_file:
        experiment_results_lst = ExperimentResultList(
            model=MODEL,
            number_of_loops=RUNS_PER_TD,
            number_of_retries=NUMBER_OF_RETRIES,
            time_elapsed=experiment_time,
            temperature=TEMPERATURE,
            results=experiment_lst,
        )
        out_file.write(experiment_results_lst.model_dump_json(indent=2, by_alias=True))

    print(f"Experiment completed in : {experiment_results_lst.time_elapsed}")
