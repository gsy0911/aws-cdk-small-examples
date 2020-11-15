from datetime import datetime


def lambda_task(event, _):
    print(event)
    time = event['time']
    dt = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
    return {"dt": datetime.strftime(dt, "%Y-%m-%d")}

