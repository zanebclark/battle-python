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
    print(f"stack name: {stack_name}")
    result = subprocess.run(
        [
            "aws",
            "cloudformation",
            "describe-stacks",
            "--stack-name",
            f"{stack_name}",
            "--query",
            "Stacks[0].Outputs",
        ],
        shell=True,
        capture_output=True,
        text=True,
    )
    if result.stderr != "":
        raise Exception(f"{result.stderr}")
    print(f"result: {result}")

    stack_outputs = json.loads(result.stdout)
    env_file = os.getenv("GITHUB_OUTPUT")
    with open(env_file, "a") as myfile:
        for output_obj in stack_outputs:
            myfile.write(get_formatted_output(output_obj))


if __name__ == "__main__":
    main()
