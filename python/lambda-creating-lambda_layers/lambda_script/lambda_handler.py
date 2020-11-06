import subprocess
import zipfile
import boto3
from pathlib import Path


def put_lambda_layer_to_s3(event: dict, _):
    """
    
    Args:
        event: dict
            {
                "package_list": ["pandas", "requests", "cerberus"],
                "s3_bucket": "your-bucket-name",
                "s3_key": "your-key-name"
            }
    """
    # check arguments
    if "package_list" not in event:
        return {"error": "[package_list] not exist"}
    package_list = event['package_list']
    if type(package_list) is not list:
        return {"error": "[package_list] is not list"}
    if "s3_bucket" not in event:
        return {"error": "[s3_bucket] not exist"}
    if "s3_key" not in event:
        return {"error": "[s3_key] not exist"}

    # add packages to /tmp/python directory
    mkdir_cmd = "mkdir -p /tmp/python"
    pip_install_cmd = f"pip install -t /tmp/python {' '.join(package_list)}"
    process = (subprocess.Popen(f"{mkdir_cmd} && {pip_install_cmd}", stdout=subprocess.PIPE, shell=True).communicate()[0]).decode('utf-8')
    print('commands...\n'+process)

    # Path-object
    p = Path("/tmp/python")

    # zip installed package
    with zipfile.ZipFile('/tmp/python_lib.zip', 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
        for f in list(p.glob("**/*")):
            new_zip.write(f, arcname=str(f).replace("/tmp/", ""))

    # upload to s3
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(event['s3_bucket'])
    bucket.upload_file('/tmp/python_lib.zip', event['s3_key'])
    return {
        "success": f"put file to [s3://{event['s3_bucket']}/{event['s3_key']}]"
    }
