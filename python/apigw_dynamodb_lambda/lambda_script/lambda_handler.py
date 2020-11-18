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

# set environment variable
TABLE_NAME = os.environ['TABLE_NAME']


def consumer(event, context):
    table = dynamodb.Table(TABLE_NAME)
    # Scan items in table
    try:
        response = table.scan()
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        # print item of the table - see CloudWatch logs
        for i in response['Items']:
            print(json.dumps(i, cls=DecimalEncoder))

    return {
        'statusCode': 200,
    }


def producer(event, context):
    table = dynamodb.Table(TABLE_NAME)
    # put item in table
    response = table.put_item(
        Item={
            'id': str(uuid.uuid4())
        }
    )

    print("PutItem succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

    return {
        'statusCode': 200,
    }
