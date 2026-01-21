"""
Python pytest module using a dynamic import of lambda_handler modules.

The lambda_handler fixture detects the module name of the file being run
and will get dynamically import the module from the src/lambdas directory
so that tests can be run against it.

This would allow code called outside the Lambda Handler to be correctly
mocked and instantiated before the lambda_function is called.
"""

def test_lambda_default(mock_s3_client, lambda_handler):
    response = lambda_handler({"key": "test.txt"})
    assert response["statusCode"] == 200

    obj = mock_s3_client.get_object(
        Bucket="test-bucket",
        Key="test.txt",
    )

    assert obj["Body"].read() == b"hello"


def test_lambda_custom_body(mock_s3_client, lambda_handler):
    response = lambda_handler({"key": "custom.txt", "body": "abc"})
    assert response["statusCode"] == 200

    obj = mock_s3_client.get_object(
        Bucket="test-bucket",
        Key="custom.txt",
    )

    assert obj["Body"].read() == b"abc"


def test_lambda_missing_key(lambda_handler):
    response = lambda_handler({})
    assert response["statusCode"] == 400
    assert "Missing 'key'" in response["message"]


def test_lambda_body_bytes(mock_s3_client, lambda_handler):
    response = lambda_handler({"key": "bytes.txt", "body": b"byte content"})
    assert response["statusCode"] == 200

    obj = mock_s3_client.get_object(
        Bucket="test-bucket",
        Key="bytes.txt",
    )
    assert obj["Body"].read() == b"byte content"

