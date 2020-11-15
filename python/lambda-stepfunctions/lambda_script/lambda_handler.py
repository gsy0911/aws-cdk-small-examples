from datetime import datetime


def lambda_task(event, _):
    print(event)
    time = event['time']
    dt = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
    return {"dt": datetime.strftime(dt, "%Y-%m-%d")}


def lambda_fail(event, _):
    print("fail")
    return event


def lambda_success(event, _):
    print("success")
    return event
