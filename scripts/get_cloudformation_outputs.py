import os
import subprocess
from typing import Dict
import click
import boto3
import json


def get_formatted_output(output_obj: Dict):
    output_key = output_obj["OutputKey"]
    output_value = output_obj["OutputValue"]
    return f'{output_key.strip().upper()}="{output_value.strip()}"'


@click.command()
@click.option("--stack-name", help="The name of the Cloudformation stack")
def main(stack_name: str):
    stack_name = "battle-python-dev"
    print(f"stack name: {stack_name}")
    cf_client = boto3.client("cloudformation")
    response = cf_client.describe_stacks(StackName=stack_name)
    outputs = response["Stacks"][0]["Outputs"]

    env_vars = [get_formatted_output(output) for output in outputs]
    with open(os.getenv["GITHUB_OUTPUT"], "a") as fh:
        for env_var in env_vars:
            print(env_var)
            print(f"{env_var}", file=fh)


if __name__ == "__main__":
    main()
