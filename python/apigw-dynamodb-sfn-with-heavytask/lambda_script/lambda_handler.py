from datetime import datetime
import decimal
import json
import os
import random
import uuid

import boto3
from botocore.exceptions import ClientError


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


# Get the service resource.
dynamodb = boto3.resource('dynamodb')
step_functions = boto3.client("stepfunctions")
sqs = boto3.client("sqs")

# set environment variable
TABLE_NAME = os.environ.get("TABLE_NAME")
STEP_FUNCTION_ARN = os.environ.get("STEP_FUNCTION_ARN")
QUEUE_URL = os.environ.get("QUEUE_URL")


def _decode_payload(event: dict) -> dict:
    # get insert data from apigw
    if "body" in event:
        payload = json.loads(event['body'])
    elif "data" in event:
        payload = event['data']
    else:
        raise ValueError("'body' or 'data' is required.")
    return payload


def consumer(event, context):
    table = dynamodb.Table(TABLE_NAME)

    scan_data = []
    # Scan items in table
    try:
        response = table.scan()
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        scan_data = []
        # print item of the table - see CloudWatch logs
        for i in response['Items']:
            scan_data.append(i)
            print(i)

    return {
        'statusCode': 200,
        "body": json.dumps({"response": scan_data}, cls=DecimalEncoder)
    }


def producer(event, context):
    table = dynamodb.Table(TABLE_NAME)
    # get data from payload
    payload = _decode_payload(event=event)
    id_ = str(uuid.uuid4())
    payload.update({"id": id_})

    # en-queue
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=id_
    )

    # put item in table
    response = table.put_item(
        Item=payload

    )

    print(f"item to insert: {payload}")
    print("PutItem succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

    return {
        'statusCode': 200,
        "body": json.dumps({"insert": payload})
    }


def update_status(event, context):
    table = dynamodb.Table(TABLE_NAME)
    # get data from payload
    payload = _decode_payload(event=event)

    response = table.update_item(
        Key={
            "id": payload['id']
        },
        UpdateExpression="set #status = :status",
        ExpressionAttributeNames={
            '#status': 'status'
        },
        ExpressionAttributeValues={
            ':status': payload['status']
        },
        ReturnValues="UPDATED_NEW"
    )
    return {
        "statusCode": 200,
        "body": json.dumps({"update": response})
    }


def invoke_step_function(event, _):
    """
    queue message is received as
    {
        "Messages": [
            {
                "MessageId": "...",
                "ReceiptHandle": "...",
                "MD5OfBody": "...",
                "Body": "..."
            }
        ],
        "ResponseMetadata": {
            "RequestId": "...",
            "HttpStatusCode": 200,
            "HTTPHeaders": {
                "x-amzn-requestid": "...",
                "data": "Sun, 22 Nov 2020 02:15:28 GMT",
                "content-type": "text/xml",
                "content-length": 123
            },
            "RetryAttempts": 0
        }
    }
    """
    # get data from queue
    message = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        VisibilityTimeout=30
    )
    print(message)
    if "Messages" in message:
        queue_message = message['Messages'][0]
        id_ = queue_message['Body']
        step_functions.start_execution(
            stateMachineArn=STEP_FUNCTION_ARN,
            name=f"process_for_{id_}_{datetime.now().strftime('%Y%m%dT%H%M%S')}",
            input=json.dumps({
                "id": id_,
                # to choice `success` or `failure` in SFn
                "job_status": "success" if random.randint(1, 10) < 5 else "fail"
            })
        )

        # delete message
        _ = sqs.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=queue_message['ReceiptHandle']
        )
    else:
        pass
