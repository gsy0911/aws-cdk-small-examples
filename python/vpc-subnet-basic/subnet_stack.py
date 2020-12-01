from aws_cdk import (
    core,
    aws_ec2,
    aws_cloudformation as aws_cfn
)


class SubnetStack(aws_cfn.NestedStack):
    """
    The class creates
    * Subnet
    """

    def __init__(
            self,
            app: core.Construct,
            stack_name: str,
            vpc: aws_ec2.Vpc,
            subnet_cidr: str,
            subnet_name: str,
            availability_zone: str,
            is_public_subnet: bool
    ):
        super().__init__(scope=app, id=f"{stack_name}-subnet-{subnet_name}")

        self.subnet = aws_ec2.Subnet(
            scope=self,
            id=subnet_name,
            cidr_block=subnet_cidr,
            vpc_id=vpc.vpc_id,
            availability_zone=availability_zone,
            map_public_ip_on_launch=is_public_subnet
        )
