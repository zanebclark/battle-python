from dataclasses import dataclass


@dataclass
class MockLambdaContext:
    function_name: str = "test-func"
    memory_limit_in_mb: int = 128
    invoked_function_arn: str = (
        "arn:aws:lambda:eu-west-1:809313241234:function:test-func"
    )
    aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    def get_remaining_time_in_millis(self) -> int:
        return 1000
