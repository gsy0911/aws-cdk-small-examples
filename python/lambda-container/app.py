from aws_cdk import (
    aws_lambda as lambda_,
    aws_iam as iam,
    core,
)


class LambdaContainer(core.Stack):
    """

    """

    LAMBDA_PYTHON_RUNTIME = lambda_.Runtime.PYTHON_3_8

    def __init__(self, app: core.App, _id: str):
        super().__init__(scope=app, id=_id)

        lambda_s3_access_role = iam.Role(
            scope=self,
            id=f"lambda_s3_access_role",
            role_name=f"lambda_s3_access_role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )

        # add policy to access S3
        lambda_s3_access_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=["*"],
                actions=["s3:*"]
            )
        )

        # add policy to access CloudWatch Logs
        lambda_s3_access_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[
                    "arn:aws:logs:*:*:*"
                ],
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogStreams"
                ]
            )
        )

        # lambda to put LambdaLayers.zip to S3
        _ = lambda_.Function(
            scope=self,
            id=f"lambda",
            code=lambda_.AssetCode.from_asset("lambda_script"),
            handler="lambda_handler.put_lambda_layer_to_s3",
            timeout=core.Duration.seconds(120),
            runtime=self.LAMBDA_PYTHON_RUNTIME,
            memory_size=512,
            role=lambda_s3_access_role
        )


def main():
    app = core.App()
    LambdaContainer(app, "LambdaContainer")
    app.synth()


if __name__ == "__main__":
    main()
