import json
from datetime import datetime


def lambda_task(event, _):
    print(event)
    payload = json.loads(event['body'])
    time = payload['time']
    dt = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
    return {
        "statusCode": 200,
        "body": json.dumps({"dt": datetime.strftime(dt, "%Y-%m-%d")})
    }


