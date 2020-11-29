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

    def __init__(self, app: core.Construct, stack_name: str):
        super().__init__(scope=app, id=f"{stack_name}-vpc")

        # CIDR
        cidr = "192.168.0.0/24"

        # === #
        # vpc #
        # === #
        self.vpc = aws_ec2.Vpc(
            self,
            id="vpc",
            cidr=cidr,
            subnet_configuration=[
                # Public Subnet
                aws_ec2.SubnetConfiguration(
                    cidr_mask=28,
                    name="public_vpc",
                    subnet_type=aws_ec2.SubnetType.PUBLIC,
                )
            ],
        )

        self.security_group = aws_ec2.SecurityGroup(
            self,
            id="security-group",
            vpc=self.vpc,
            security_group_name="security-group-public",
            allow_all_outbound=True
        )
