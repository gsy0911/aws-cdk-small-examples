# timeのparse用
from datetime import datetime
from logging import getLogger, INFO
# インストールライブラリ
from boto3.session import Session
import click
import watchtower


# envvarで指定すると環境変数から値を取得する
@click.command()
@click.option("--time")
@click.option("--s3_bucket", envvar='S3_BUCKET')
def main(time: str, s3_bucket: str):
    if time:
        # CloudWatch Eventから実行することを想定し、時刻のparseをする
        d = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
        # 実行日付を取得
        execute_date = d.strftime("%Y-%m-%d")

    # loggerの設定
    # loggerの名前がログストリームの名前になる
    logger_name = f"{datetime.now().strftime('%Y/%m/%d')}"
    logger = getLogger(logger_name)
    logger.setLevel(INFO)
    # CloudWatch Logsのロググループの名前をここで指定
    # Sessionを渡してIAM Role経由でログを送信
    handler = watchtower.CloudWatchLogHandler(log_group="/aws/some_project", boto3_session=Session())
    logger.addHandler(handler)

    # 実行予定の処理
    # ここでは、CloudWatch Logsに実行日時を書き込むのみ
    logger.info(f"{execute_date=}")


if __name__ == "__main__":
    """
    python __init__.py 
        --time 2020-09-11T12:30:00Z
        --s3_bucket your-bucket-here
    """
    main()