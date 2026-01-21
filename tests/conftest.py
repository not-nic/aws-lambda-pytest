import importlib
import sys

from typing import Protocol

import boto3
import pytest
import os

from moto import mock_aws

# Completely unnecessary it's just for duck-typing, so I can do m
# module = load_lambda()
# module. (and I get the IDE auto complete of lambda_handler.)
class LambdaModule(Protocol):
    def lambda_handler(self, event: dict, context: dict) -> dict:
        ...


@pytest.fixture(scope="session")
def aws_credentials():
    """
    Mocked AWS credentials for moto.
    """
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@pytest.fixture
def mock_ssm_client():
    os.environ["PARAM_NAME"] = "/test/param"
    with mock_aws():
        ssm = boto3.client("ssm", region_name="eu-west-2")
        ssm.put_parameter(
            Name="/test/param",
            Value="ssm-value",
            Type="String",
        )

        yield ssm

@pytest.fixture
def mock_s3_client():
    os.environ["BUCKET_NAME"] = "test-bucket"
    with mock_aws():
        s3 = boto3.client("s3", region_name="eu-west-2")
        s3.create_bucket(Bucket="test-bucket", CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})
        yield s3


@pytest.fixture
def load_lambda():
    """
    Pytest fixture factory to Dynamically load the lambda function modules after import time,
    call this fixture with the module name of the specified python file containing a lambda handler.

    :return:
        Callable: _load which imports the specified module.
    """
    def _load(module_name: str) -> LambdaModule:
        module_path: str = f"src.lambdas.{module_name}"
        try:
            if module_path in sys.modules:
                module = importlib.reload(sys.modules[module_path])
            else:
                module = importlib.import_module(module_path)
            return module  # type: ignore
        except ModuleNotFoundError:
            pytest.fail(f"Could not find module '{module_path}'. Check your test filename or module location.")
        except Exception as exc:
            pytest.fail(f"Failed to load module '{module_path}': {exc}")

    return _load


@pytest.fixture
def module_name(request, load_lambda):
    """
    Util method to get the python module name from the test filename.

    Example:
        tests/lambdas/test_lambda_s3_call.py -> returns 'lambda_s3_call'
    """
    test_name = request.path.stem
    return test_name[5:] if test_name.startswith("test_") else test_name

# Unsure what is actually better here, applying all the client mocks (e.g. mock_s3, mock_ssm) feels ugly af.
# And using the required mocks in the tests seems nicer, but abstracting this out to 'lambda_handler'
# feels much nicer.

# NOTE: Can actually just apply this after all other mocks, and it works, but is that a weird standard to impose?
@pytest.fixture
def lambda_handler(load_lambda, module_name):
    """
    Fixture factory to abstract the dynamic import of the lambda function to just
    provide a 'lambda_handler' for tests, with an event and context object.

    note: should be called after all other mocks within the test.
    """
    module = load_lambda(module_name)

    def handler(event, context=None):
        if context is None:
            context = {}
        return module.lambda_handler(event, context)

    return handler