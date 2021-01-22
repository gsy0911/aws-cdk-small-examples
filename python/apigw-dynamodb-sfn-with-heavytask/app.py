from aws_cdk import (
    core,
    aws_lambda as lambda_,
    aws_dynamodb,
    aws_apigateway as apigw_,
    aws_stepfunctions as aws_sfn,
    aws_stepfunctions_tasks as aws_sfn_tasks,
    aws_events,
    aws_events_targets,
    aws_sqs
)


class ApigwDynamodbStepFunctionStack(core.Stack):

    LAMBDA_PYTHON_RUNTIME = lambda_.Runtime.PYTHON_3_8

    def _create_lambda_function(
            self,
            function_name: str,
            environment: dict
    ):
        return lambda_.Function(
            scope=self,
            id=f"{function_name}_lambda_function",
            runtime=self.LAMBDA_PYTHON_RUNTIME,
            handler=f"lambda_handler.{function_name}",
            code=lambda_.Code.asset("./lambda_script"),
            environment=environment
        )

    def _dynamodb_update_in_sfn(
            self,
            table: aws_dynamodb.Table,
            status: str
    ):
        return aws_sfn_tasks.DynamoUpdateItem(
            scope=self,
            id=f"dynamodb_status_updated_as_{status}",
            # get id from StepFunctions state
            key={"id": aws_sfn_tasks.DynamoAttributeValue.from_string(aws_sfn.JsonPath.string_at("$.id"))},
            table=table,
            update_expression="set #status = :status",
            expression_attribute_names={
                "#status": "status"
            },
            expression_attribute_values={
                ":status": aws_sfn_tasks.DynamoAttributeValue.from_string(status)
            },
            result_path=f"$.status_{status}"
        )

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
            read_capacity=3,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        queue = aws_sqs.Queue(self, f"{id_}-SQSQueue")

        # create producer lambda function
        producer_lambda = self._create_lambda_function(
            function_name="producer",
            environment={
                "TABLE_NAME": demo_table.table_name,
                "QUEUE_URL": queue.queue_url
            }
        )
        queue.grant_send_messages(producer_lambda)

        # grant permission to lambda to write to demo table
        demo_table.grant_write_data(producer_lambda)

        # create consumer lambda function
        consumer_lambda = self._create_lambda_function(
            function_name="consumer",
            environment={"TABLE_NAME": demo_table.table_name}
        )

        # grant permission to lambda to read from demo table
        demo_table.grant_read_data(consumer_lambda)

        # api_gateway for root
        base_api = apigw_.RestApi(
            scope=self,
            id=f"{id_}-{stack_env}-apigw",
            rest_api_name=f"{id_}-{stack_env}-apigw",
            deploy_options=apigw_.StageOptions(stage_name=stack_env)
        )

        # /example entity
        api_entity = base_api.root.add_resource("example")

        # GET /example
        api_entity.add_method(
            http_method="GET",
            integration=apigw_.LambdaIntegration(
                handler=consumer_lambda,
                integration_responses=[
                    apigw_.IntegrationResponse(
                        status_code="200"
                    )
                ]
            )
        )

        # POST /example
        api_entity.add_method(
            http_method="POST",
            integration=apigw_.LambdaIntegration(
                handler=producer_lambda,
                integration_responses=[
                    apigw_.IntegrationResponse(
                        status_code="200"
                    )
                ]
            )
        )

        # ============= #
        # StepFunctions #
        # ============= #

        dynamodb_update_running_task = self._dynamodb_update_in_sfn(table=demo_table, status="running")

        wait_1_min = aws_sfn.Wait(
            scope=self,
            id="Wait one minutes as heavy task",
            time=aws_sfn.WaitTime.duration(core.Duration.minutes(1)),
        )

        dynamodb_update_complete_task = self._dynamodb_update_in_sfn(table=demo_table, status="complete")
        dynamodb_update_failure_task = self._dynamodb_update_in_sfn(table=demo_table, status="failure")

        check_task_status = aws_sfn.Choice(scope=self, id="Job Complete?")\
            .when(aws_sfn.Condition.string_equals("$.job_status", "success"), dynamodb_update_complete_task) \
            .otherwise(dynamodb_update_failure_task)

        # StepFunctions
        definition = dynamodb_update_running_task \
            .next(wait_1_min) \
            .next(check_task_status)

        sfn_process = aws_sfn.StateMachine(
            scope=self,
            id=f"{id_}-{stack_env}",
            definition=definition
        )

        # Lambda to invoke StepFunction
        sfn_invoke_lambda = self._create_lambda_function(
            function_name="invoke_step_function",
            environment={
                "STEP_FUNCTION_ARN": sfn_process.state_machine_arn,
                "QUEUE_URL": queue.queue_url
            }
        )
        # grant
        queue.grant_consume_messages(sfn_invoke_lambda)
        sfn_process.grant_start_execution(sfn_invoke_lambda)

        # ================ #
        # CloudWatch Event #
        # ================ #

        # Runs every 2 hour
        invoke_automatically = aws_events.Rule(
            scope=self,
            id=f"InvokeSFnViaLambda-{stack_env}",
            schedule=aws_events.Schedule.rate(core.Duration.hours(2))
        )
        invoke_automatically.add_target(aws_events_targets.LambdaFunction(sfn_invoke_lambda))


def main():
    app = core.App()
    ApigwDynamodbStepFunctionStack(app, "ApigwDynamodbStepFunction", "prod")
    app.synth()


if __name__ == "__main__":
    main()
