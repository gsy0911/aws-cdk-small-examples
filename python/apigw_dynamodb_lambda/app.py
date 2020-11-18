from aws_cdk import (
    core,
    aws_lambda as lambda_,
    aws_dynamodb
)


class ApigwDynamodbLambdaStack(core.Stack):

    LAMBDA_PYTHON_RUNTIME = lambda_.Runtime.PYTHON_3_8

    def __init__(self, scope: core.App, id_: str, **kwargs) -> None:
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


def main():
    app = core.App()
    ApigwDynamodbLambdaStack(app, "ApigwDynamodbLambda")
    app.synth()


if __name__ == "__main__":
    main()
