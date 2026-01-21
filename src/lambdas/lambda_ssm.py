import boto3
import os

ssm = boto3.client("ssm")
PARAM_NAME = os.environ["PARAM_NAME"]

PARAM_VALUE = ssm.get_parameter(
    Name=PARAM_NAME,
    WithDecryption=False,
)["Parameter"]["Value"]

def lambda_handler(event, context):
    print(f"got value from SSM: {PARAM_VALUE}")
    return {
        "statusCode": 200,
        "value": PARAM_VALUE,
    }