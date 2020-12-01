from aws_cdk import (
    core,
    aws_ec2,
    aws_cloudformation as aws_cfn
)


class VpvStack(aws_cfn.NestedStack):
    """
    The class creates
    * VPC
    * Batch
    * StepFunctions
    * CloudWatch Event

    """

    def __init__(self, app: core.Construct, stack_name: str, cidr: str = "10.0.0.0/16"):
        super().__init__(scope=app, id=f"{stack_name}-vpc")

        # === #
        # vpc #
        # === #
        self.vpc = aws_ec2.Vpc(
            self,
            id="vpc",
            cidr=cidr
        )

        # self.security_group = aws_ec2.SecurityGroup(
        #     self,
        #     id="security-group",
        #     vpc=self.vpc,
        #     security_group_name="security-group-public",
        #     allow_all_outbound=True
        # )
