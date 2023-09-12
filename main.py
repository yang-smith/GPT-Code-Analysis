import logging

from pathlib import Path

import typer

from gpt_code_analysis.ai import AI, fallback_model
# from gpt_code_analysis.collect import collect_learnings
from gpt_code_analysis.db import DB, DBs, archive
# from gpt_code_analysis.learning import collect_consent
from gpt_code_analysis.steps import STEPS, Config as StepsConfig
from gpt_code_analysis.tree import save_structure_to_file
from gpt_code_analysis.analyze import analyze

import ast

from enum import Enum
from typing import List, Union
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from gpt_code_analysis.chat_to_files import to_files
Message = Union[AIMessage, HumanMessage, SystemMessage]


app = typer.Typer()


@app.command()
def main(
    project_path: str = typer.Argument("projects/example", help="path"),
    model: str = typer.Argument("gpt-3.5-turbo-16k", help="model id string"),
    temperature: float = 0.1,
    steps_config: StepsConfig = typer.Option(
        StepsConfig.DEFAULT, "--steps", "-s", help="decide which steps to run"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    model = fallback_model(model)
    ai = AI(
        model_name=model,
        temperature=temperature,
    )

    input_path = Path(project_path).absolute()
    memory_path = input_path / "memory"
    workspace_path = input_path / "workspace"
    archive_path = input_path / "archive"

    dbs = DBs(
        memory=DB(memory_path),
        logs=DB(memory_path / "logs"),
        input=DB(input_path),
        workspace=DB(workspace_path),
        preprompts=DB(Path(__file__).parent / "preprompts"),
        archive=DB(archive_path),
    )

    if steps_config not in [
        StepsConfig.EXECUTE_ONLY,
        StepsConfig.USE_FEEDBACK,
        StepsConfig.EVALUATE,
    ]:
        archive(dbs)
    analyze(ai, dbs, input_path)

    # steps = STEPS[steps_config]
    # for step in steps:
    #     messages = step(ai, dbs)
    #     dbs.logs[step.__name__] = AI.serialize_messages(messages)

    # if collect_consent():
    #     collect_learnings(model, temperature, steps, dbs)

    # dbs.logs["token_usage"] = ai.format_token_usage_log()


if __name__ == "__main__":
    app()
