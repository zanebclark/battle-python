import pytest

from tests.mocks.MockLambdaContext import MockLambdaContext


@pytest.fixture()
def lambda_context():
    return MockLambdaContext()
