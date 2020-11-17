from aws_cdk import (
    core,
    aws_cloudfront as cloud_front,
    # aws_cloudfron_origins as origin,
    aws_s3 as s3,
    # aws_s3_deployment as s3_deploy,
    aws_s3_assets as s3_assets
)


class CloudFrontS3Stack(core.Stack):
    """

    """

    def __init__(self, app: core.App, cfn_name: str, stack_env):
        super().__init__(scope=app, id=f"{cfn_name}-{stack_env}")

        s3_bucket = s3.Bucket(
            scope=self,
            id=f"{cfn_name}-{stack_env}"
        )

        # s3_assets.AssetProps()

        cloud_front_s3 = cloud_front.Distribution(
            scope=self,
            id=f"{cfn_name}-{stack_env}",
            default_behavior=cloud_front.BehaviorOptions(
                origin=None
            )
        )


def main():
    app = core.App()
    CloudFrontS3Stack(app, "CloudFrontS3", "prod")
    app.synth()


if __name__ == "__main__":
    main()
