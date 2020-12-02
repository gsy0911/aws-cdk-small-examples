import pandas as pd


def lambda_handler(event, _):
    print(pd.__version__)
    return event
