import os
import click
import boto3


def get_formatted_output(output_obj: dict) -> str:
    output_key = output_obj["OutputKey"]
    output_value = output_obj["OutputValue"]
    return f"{output_key.strip().upper()}={output_value.strip()}"


def get_cloudformation_outputs(stack_name: str, aws_region: str) -> list[dict]:
    print(f"Stack Name: {stack_name}")
    print(f"AWS Region: {aws_region}")
    cf_client = boto3.client("cloudformation", region_name=aws_region)
    response = cf_client.describe_stacks(StackName=stack_name)
    outputs = response["Stacks"][0]["Outputs"]
    print(f"outputs:")
    for output in outputs:
        print(output)
    return outputs


@click.group()
def cli() -> None:
    pass


@cli.command(name="get_cloudformation_outputs")
@click.option("--stack-name", help="The name of the Cloudformation stack")
@click.option("--aws-region")
def get_cloudformation_outputs_cli(stack_name: str, aws_region: str) -> list[dict]:
    return get_cloudformation_outputs(stack_name=stack_name, aws_region=aws_region)


@cli.command()
@click.option("--stack-name", help="The name of the Cloudformation stack")
@click.option("--aws-region")
def write_cloudformation_outputs_to_github_env(
    stack_name: str, aws_region: str
) -> None:
    outputs = get_cloudformation_outputs(stack_name=stack_name, aws_region=aws_region)

    env_vars = [get_formatted_output(output) for output in outputs]
    with open(os.environ["GITHUB_ENV"], "a") as fh:
        for env_var in env_vars:
            print(env_var)
            print(env_var, file=fh)


if __name__ == "__main__":
    cli()
