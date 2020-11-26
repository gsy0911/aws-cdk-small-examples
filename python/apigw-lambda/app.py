from aws_cdk import (
    core,
    aws_lambda as lambda_,
    aws_apigateway as apigw_,
    aws_iam as iam
)


class ApigwLambdaStack(core.Stack):
    """

    """

    LAMBDA_PYTHON_RUNTIME = lambda_.Runtime.PYTHON_3_8

    def __init__(self, app: core.App, cfn_name: str, stack_env):
        super().__init__(scope=app, id=f"{cfn_name}-{stack_env}")

        # lambda
        lambda_function = lambda_.Function(
            scope=self,
            id=f"{cfn_name}-lambda-task",
            code=lambda_.AssetCode.from_asset("lambda_script"),
            handler="lambda_handler.lambda_task",
            timeout=core.Duration.seconds(10),
            runtime=self.LAMBDA_PYTHON_RUNTIME,
            memory_size=128
        )

        # resource policy
        whitelisted_ips = [
            "127.0.0./32"
        ]
        api_resource_policy = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["execute-api:Invoke"],
                    principals=[iam.AnyPrincipal()],
                    resources=["execute-api:/*/*/*"],
                    conditions={
                        "IpAddress": {"aws:SourceIp": whitelisted_ips}
                    }
                )
            ]
        )

        # api_gateway
        base_api = apigw_.RestApi(
            scope=self,
            id=f"{cfn_name}-{stack_env}-apigw",
            rest_api_name=f"{cfn_name}-{stack_env}-apigw",
            deploy_options=apigw_.StageOptions(stage_name=stack_env),
            policy=api_resource_policy
        )

        api_entity = base_api.root.add_resource("task")
        api_entity_lambda = apigw_.LambdaIntegration(
            handler=lambda_function,
            integration_responses=[
                apigw_.IntegrationResponse(
                    status_code="200"
                )
            ]
        )

        api_entity.add_method(
            http_method="POST",
            integration=api_entity_lambda
        )


def main():
    app = core.App()
    ApigwLambdaStack(app, "ApigwLambda", "prod")
    ApigwLambdaStack(app, "ApigwLambda", "dev")
    app.synth()


if __name__ == "__main__":
    main()
