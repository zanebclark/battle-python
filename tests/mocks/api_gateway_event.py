import time

from battle_python.api import RestMethod
import json


def get_mock_api_gateway_headers() -> dict[str, str]:
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "127.0.0.1:3000",
        "Sec-Ch-Ua": '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Linux"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 "
        "Safari/537.36",
        "X-Forwarded-Port": "3000",
        "X-Forwarded-Proto": "http",
    }


def get_mock_multi_value_headers() -> dict[str, object]:
    return {
        "Accept": [
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.9 "
        ],
        "Accept-Encoding": ["gzip, deflate, br"],
        "Accept-Language": ["pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"],
        "Cache-Control": ["max-age=0"],
        "Connection": ["keep-alive"],
        "Host": ["127.0.0.1:3000"],
        "Sec-Ch-Ua": [
            '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"'
        ],
        "Sec-Ch-Ua-Mobile": ["?0"],
        "Sec-Ch-Ua-Platform": ['"Linux"'],
        "Sec-Fetch-Dest": ["document"],
        "Sec-Fetch-Mode": ["navigate"],
        "Sec-Fetch-Site": ["none"],
        "Sec-Fetch-User": ["?1"],
        "Upgrade-Insecure-Requests": ["1"],
        "User-Agent": [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        ],
        "X-Forwarded-Port": ["3000"],
        "X-Forwarded-Proto": ["http"],
    }


def get_mock_identity() -> dict[str, str]:
    return {
        "accountId": "",
        "apiKey": "",
        "caller": "",
        "cognitoAuthenticationProvider": "",
        "cognitoAuthenticationType": "",
        "cognitoIdentityPoolId": "",
        "sourceIp": "127.0.0.1",
        "user": "",
        "userAgent": "Custom User Agent String",
        "userArn": "",
    }


def get_mock_request_context(method: RestMethod, path: str):
    return {
        "accountId": "123456789012",
        "apiId": "1234567890",
        "domainName": "127.0.0.1:3000",
        "extendedRequestId": "",
        "httpMethod": method,
        "identity": get_mock_identity(),
        "path": path,
        "protocol": "HTTP/1.1",
        "requestId": "a3590457-cac2-4f10-8fc9-e47114bf7c62",
        "requestTime": "02/Feb/2023:11:45:26 +0000",
        "requestTimeEpoch": time.time_ns() // 1_000_000,
        "resourceId": "123456",
        "resourcePath": path,
        "stage": "Prod",
    }


def get_mock_api_gateway_event(method: RestMethod, path: str, body: dict | None = None):
    return {
        "body": json.dumps(body),
        "headers": get_mock_api_gateway_headers(),
        "httpMethod": method,
        "isBase64Encoded": False,
        "multiValueHeaders": get_mock_multi_value_headers(),
        "multiValueQueryStringParameters": "",
        "path": path,
        "pathParameters": "",
        "queryStringParameters": "",
        "requestContext": get_mock_request_context(method=method, path=path),
        "resource": path,
        "stageVariables": "",
        "version": "1.0",
    }
