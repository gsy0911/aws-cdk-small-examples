from aws_cdk import (
    core,
)

from vpc_stack import VpvStack


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


def main():
    app = core.App()
    BatchNestedEnvironment(app, "batch-nested-environment")
    app.synth()


if __name__ == "__main__":
    main()
