from aws_cdk import (
    core,
)

from vpc_stack import VpvStack
from batch_stack import BatchStack
from inoke_stack import InvokeStack

S3_BUCKET = ""


class BatchNestedEnvironment(core.Stack):
    """
    The class creates
    * VPC
    * Batch
    * StepFunctions
    * CloudWatch Event

    """
    def __init__(self, app: core.App, stack_name: str):
        super().__init__(scope=app, id=stack_name)

        vpc_stack = VpvStack(app=self, stack_name=stack_name)
        batch_stack = BatchStack(
            app=self,
            stack_name=stack_name,
            vpc=vpc_stack.vpc,
            security_group=vpc_stack.security_group
        )

        # invoke
        invoke_stack = InvokeStack(
            app=self,
            stack_name=stack_name,
            batch_job_definition=batch_stack.batch_job_definition,
            batch_job_queue=batch_stack.batch_job_queue
        )


def main():
    app = core.App()
    BatchNestedEnvironment(app, "batch-nested-environment")
    app.synth()


if __name__ == "__main__":
    main()
