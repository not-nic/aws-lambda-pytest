import boto3
import os

s3 = boto3.client("s3")
BUCKET = os.environ["BUCKET_NAME"]

def lambda_handler(event, context):
    key = event.get("key")
    body = event.get("body", "hello")

    if not key:
        return {
            "statusCode": 400,
            "message": "Missing 'key' in event"
        }

    if isinstance(body, str):
        body = body.encode("utf-8")

    print(f"Putting {key} in {BUCKET}")

    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=body,
    )

    return {
        "statusCode": 200,
        "bucket": BUCKET,
        "key": key,
    }
