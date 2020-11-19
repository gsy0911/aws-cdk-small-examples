from aws_cdk import (
    core,
    aws_lambda as lambda_,
    aws_dynamodb,
    aws_apigateway as apigw_
)


class ApigwDynamodbLambdaStack(core.Stack):

    LAMBDA_PYTHON_RUNTIME = lambda_.Runtime.PYTHON_3_8

    def __init__(self, scope: core.App, id_: str, stack_env: str, **kwargs) -> None:
        super().__init__(scope, id_, **kwargs)

        # create dynamo table
        demo_table = aws_dynamodb.Table(
            scope=self,
            id="demo_table",
            partition_key=aws_dynamodb.Attribute(
                name="id",
                type=aws_dynamodb.AttributeType.STRING
            ),
            write_capacity=3,
            read_capacity=3
        )

        # create producer lambda function
        producer_lambda = lambda_.Function(
            scope=self,
            id="producer_lambda_function",
            runtime=self.LAMBDA_PYTHON_RUNTIME,
            handler="lambda_handler.producer",
            code=lambda_.Code.asset("./lambda_script"),
            environment={"TABLE_NAME": demo_table.table_name}
        )

        # grant permission to lambda to write to demo table
        demo_table.grant_write_data(producer_lambda)

        # create consumer lambda function
        consumer_lambda = lambda_.Function(
            scope=self,
            id="consumer_lambda_function",
            runtime=self.LAMBDA_PYTHON_RUNTIME,
            handler="lambda_handler.consumer",
            code=lambda_.Code.asset("./lambda_script"),
            environment={"TABLE_NAME": demo_table.table_name})

        # grant permission to lambda to read from demo table
        demo_table.grant_read_data(consumer_lambda)

        # create consumer lambda function
        update_lambda = lambda_.Function(
            scope=self,
            id="update_lambda_function",
            runtime=self.LAMBDA_PYTHON_RUNTIME,
            handler="lambda_handler.update_status",
            code=lambda_.Code.asset("./lambda_script"),
            environment={"TABLE_NAME": demo_table.table_name})

        # grant permission to lambda to read from demo table
        demo_table.grant_write_data(update_lambda)

        # api_gateway for root
        base_api = apigw_.RestApi(
            scope=self,
            id=f"{id_}-{stack_env}-apigw",
            rest_api_name=f"{id_}-{stack_env}-apigw",
            deploy_options=apigw_.StageOptions(stage_name=stack_env)
        )

        # /example entity
        api_entity = base_api.root.add_resource("example")

        # consumer
        api_entity_consumer_lambda = apigw_.LambdaIntegration(
            handler=consumer_lambda,
            integration_responses=[
                apigw_.IntegrationResponse(
                    status_code="200"
                )
            ]
        )
        # for GET
        api_entity.add_method(
            http_method="GET",
            integration=api_entity_consumer_lambda
        )

        # producer
        api_entity_producer_lambda = apigw_.LambdaIntegration(
            handler=producer_lambda,
            integration_responses=[
                apigw_.IntegrationResponse(
                    status_code="200"
                )
            ]
        )
        # for POST
        api_entity.add_method(
            http_method="POST",
            integration=api_entity_producer_lambda
        )

        # /example/update entity
        api_update_entity = api_entity.add_resource("update")
        # producer
        api_entity_update_lambda = apigw_.LambdaIntegration(
            handler=update_lambda,
            integration_responses=[
                apigw_.IntegrationResponse(
                    status_code="200"
                )
            ]
        )
        # for POST
        api_update_entity.add_method(
            http_method="POST",
            integration=api_entity_update_lambda
        )


def main():
    app = core.App()
    ApigwDynamodbLambdaStack(app, "ApigwDynamodbLambda", "prod")
    app.synth()


if __name__ == "__main__":
    main()
