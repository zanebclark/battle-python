import json

from battle_python import app


def test_lambda_handler(apigw_event, lambda_context):
    ret = app.lambda_handler(apigw_event, lambda_context)
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "message" in ret["body"]
    assert data["message"] == "hello world"
