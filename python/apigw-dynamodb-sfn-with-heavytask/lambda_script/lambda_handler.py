import json
import uuid
import decimal
import os
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

# set environment variable
TABLE_NAME = os.environ.get("TABLE_NAME")
STEP_FUNCTION_ARN = os.environ.get("STEP_FUNCTION_ARN")


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
    payload.update({"id": str(uuid.uuid4())})

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
            '#status':  'status'
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
    # get data from payload
    payload = _decode_payload(event=event)
    id_ = payload['id']
    step_functions.start_execution(
        stateMachineArn=STEP_FUNCTION_ARN,
        name=f"process for {id_}",
        input=json.dumps({})
    )
