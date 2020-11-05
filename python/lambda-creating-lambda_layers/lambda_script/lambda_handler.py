import subprocess
import zipfile
import boto3
from pathlib import Path


def put_lambda_layer_to_s3(event, _):
    # 引数の確認
    if "package_list" not in event:
        return {"error": "[package_list]が存在しません"}
    package_list = event['package_list']
    if type(package_list) is not list:
        return {"error": "[package_list]がlistではありません"}
    if "s3_bucket" not in event:
        return {"error": "[s3_bucket]が存在しません"}
    if "s3_key" not in event:
        return {"error": "[s3_key]が存在しません"}

    # pythonと言うディレクトリを作成し、そこにpackageをインストール
    mkdir_cmd = "mkdir -p /tmp/python"
    pip_install_cmd = f"pip install -t /tmp/python {' '.join(package_list)}"
    process = (subprocess.Popen(f"{mkdir_cmd} && {pip_install_cmd}", stdout=subprocess.PIPE, shell=True).communicate()[0]).decode('utf-8')
    print('commands...\n'+process)

    # Pathオブジェクトを生成
    p = Path("/tmp/python")

    # zipにinstallしたpackageを追加
    with zipfile.ZipFile('/tmp/python_lib.zip', 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
        for f in list(p.glob("**/*")):
            new_zip.write(f, arcname=str(f).replace("/tmp/", ""))

    # upload to s3
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(event['s3_bucket'])
    bucket.upload_file('/tmp/python_lib.zip', event['s3_key'])
    return {
        "success": f"s3://{event['s3_bucket']}/{event['s3_key']}に出力しました"
    }