from aws_cdk import (
    core,
    aws_batch,
    aws_stepfunctions as aws_sfn,
    aws_stepfunctions_tasks as aws_sfn_tasks,
    aws_events,
    aws_events_targets,
    aws_cloudformation as aws_cfn
)


class InvokeStack(aws_cfn.NestedStack):
    """
    The class creates
    * VPC
    * Batch
    * StepFunctions
    * CloudWatch Event

    """

    def __init__(
            self,
            app: core.Construct,
            stack_name: str,
            batch_job_definition: aws_batch.JobDefinition,
            batch_job_queue: aws_batch.JobQueue
    ):
        super().__init__(scope=app, id=f"{stack_name}-invoke")

        # ============= #
        # StepFunctions #
        # ============= #
        # Ref::{keyword} can be replaced with StepFunction input
        command_overrides = [
            "python", "__init__.py",
            "--time", "Ref::time"
        ]

        batch_task = aws_sfn_tasks.BatchSubmitJob(
            scope=self,
            id=f"sfn_batch_job",
            job_definition=batch_job_definition,
            job_name=f"sfn_batch_job",
            job_queue=batch_job_queue,
            container_overrides=aws_sfn_tasks.BatchContainerOverrides(
                command=command_overrides
            ),
            payload=aws_sfn.TaskInput.from_object(
                {
                    "time.$": "$.time"
                }
            )
        )

        # `one step` for StepFunctions
        definition = batch_task

        sfn_daily_process = aws_sfn.StateMachine(
            scope=self,
            id=f"step_functions",
            definition=definition
        )

        # ================ #
        # CloudWatch Event #
        # ================ #

        # Run every day at 21:30 JST
        # See https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html
        events_daily_process = aws_events.Rule(
            scope=self,
            id=f"DailySFnProcess",
            schedule=aws_events.Schedule.cron(
                minute="30",
                hour="12",
                month='*',
                day="*",
                year='*'),
        )
        events_daily_process.add_target(aws_events_targets.SfnStateMachine(sfn_daily_process))
