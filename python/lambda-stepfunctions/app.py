from aws_cdk import (
    aws_lambda as lambda_,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
    core,
)


class LambdaStepfunctionsStack(core.Stack):
    """

    """

    LAMBDA_PYTHON_RUNTIME = lambda_.Runtime.PYTHON_3_8

    def __init__(self, app: core.App, cfn_name: str, stack_env):
        super().__init__(scope=app, id=f"{cfn_name}-{stack_env}")

        # lambda
        lambda_task = lambda_.Function(
            scope=self,
            id=f"{cfn_name}-lambda-task",
            code=lambda_.AssetCode.from_asset("lambda_script"),
            handler="lambda_handler.lambda_task",
            timeout=core.Duration.seconds(10),
            runtime=self.LAMBDA_PYTHON_RUNTIME,
            memory_size=128
        )

        # StepFunction Tasks
        sns_source = sfn.Pass(
            scope=self,
            id=f"{cfn_name}-sfn-pass",
            comment="pass example",
            input_path="$",
            result_path="$.source",
            result=sfn.Result.from_string("example"),
            output_path="$"
        )

        arguments_generation = sfn.Task(
            scope=self,
            id=f"{cfn_name}-sfn-lambda-task",
            task=sfn_tasks.RunLambdaTask(
                lambda_function=lambda_task,
                payload=sfn.TaskInput.from_object({
                    "time.$": "$.time",
                    "source.$": "$.source"
                })),
            input_path="$",
            result_path="$.arguments",
            output_path="$.arguments.Payload"
        )

        # stepfunctions
        definition = sns_source.next(arguments_generation)

        _ = sfn.StateMachine(
            scope=self,
            id=f"{cfn_name}-SFn-{stack_env}",
            definition=definition
        )


def main():
    app = core.App()
    LambdaStepfunctionsStack(app, "LambdaStepfunctions", "prod")
    app.synth()


if __name__ == "__main__":
    main()
