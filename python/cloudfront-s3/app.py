from aws_cdk import (
    core,
    aws_cloudfront as cloud_front,
    aws_cloudfront_origins as origin,
    aws_s3 as s3,
    aws_s3_deployment as s3_deploy
)


class CloudFrontS3Stack(core.Stack):
    """

    """
    ORIGIN_PATH = "web/static"

    def __init__(self, app: core.App, cfn_name: str, stack_env):
        super().__init__(scope=app, id=f"{cfn_name}-{stack_env}")

        s3_bucket = s3.Bucket(
            scope=self,
            id=f"{cfn_name}-{stack_env}-bucket",
            website_index_document="index.html"
        )

        # upload files in `./html` to the bucket defined above
        _ = s3_deploy.BucketDeployment(
            scope=self,
            id=f"{cfn_name}-{stack_env}-deployments",
            sources=[s3_deploy.Source.asset("./html")],
            destination_bucket=s3_bucket,
            destination_key_prefix=self.ORIGIN_PATH
        )

        # set S3 as origin
        s3_origin = origin.S3Origin(
            bucket=s3_bucket,
            origin_path=self.ORIGIN_PATH
        )
        # create CloudFront Distribution
        _ = cloud_front.Distribution(
            scope=self,
            id=f"{cfn_name}-{stack_env}",
            default_behavior=cloud_front.BehaviorOptions(
                # may warning here, for type mismatched.
                origin=s3_origin
            )
        )


def main():
    app = core.App()
    CloudFrontS3Stack(app, "CloudFrontS3", "prod")
    app.synth()


if __name__ == "__main__":
    main()
