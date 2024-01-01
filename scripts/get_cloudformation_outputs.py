import os
import subprocess
from typing import Dict
import click
import json


def get_formatted_output(output_obj: Dict):
    output_key = output_obj["OutputKey"]
    output_value = output_obj["OutputValue"]
    return f'{output_key.strip()}="{output_value.strip()}"'


@click.command()
@click.option("--stack-name", help="The name of the Cloudformation stack")
def main(stack_name: str):
    # print(f"stack name: {stack_name}")
    result = subprocess.run(
        [
            "sam",
            "list",
            "stack-outputs",
            "--stack-name",
            f"{stack_name}",
            "--output",
            "json",
        ],
        shell=True,
        capture_output=True,
        text=True,
    )
    if result.stderr != "":
        raise Exception(f"{result.stderr}")
    # print(f"result: {result}")
    stack_outputs = json.loads(result.stdout)
    output = "\n".join(
        [get_formatted_output(output_obj) for output_obj in stack_outputs]
    )
    # print(output)
    return output


if __name__ == "__main__":
    main()
