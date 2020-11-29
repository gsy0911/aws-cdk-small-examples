from aws_cdk import (
    core,
    aws_ec2,
    aws_batch,
    aws_ecr_assets,
    aws_ecs,
    aws_iam,
    aws_cloudformation as aws_cfn
)

S3_BUCKET = ""


class BatchStack(aws_cfn.NestedStack):
    """
    The class creates
    * Batch

    """

    def __init__(
            self,
            app: core.Construct,
            stack_name: str,
            vpc: aws_ec2.Vpc,
            security_group: aws_ec2.SecurityGroup):
        super().__init__(scope=app, id=f"{stack_name}-batch")

        batch_role = aws_iam.Role(
            scope=self,
            id=f"batch_role",
            role_name=f"batch_role",
            assumed_by=aws_iam.ServicePrincipal("batch.amazonaws.com")
        )

        batch_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_managed_policy_arn(
                scope=self,
                id=f"AWSBatchServiceRole",
                managed_policy_arn="arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
            )
        )

        batch_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                resources=[
                    "arn:aws:logs:*:*:*"
                ],
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogStreams"
                ]
            )
        )

        # Role to attach EC2
        instance_role = aws_iam.Role(
            scope=self,
            id=f"instance_role",
            role_name=f"instance_role_for",
            assumed_by=aws_iam.ServicePrincipal("ec2.amazonaws.com")
        )

        instance_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_managed_policy_arn(
                scope=self,
                id=f"AmazonEC2ContainerServiceforEC2Role",
                managed_policy_arn="arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
            )
        )

        # add policy to access S3
        instance_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                resources=["*"],
                actions=["s3:*"]
            )
        )

        # add policy to access CloudWatch Logs
        instance_role.add_to_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                resources=[
                    "arn:aws:logs:*:*:*"
                ],
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogStreams"
                ]
            )
        )

        # attach role to EC2
        instance_profile = aws_iam.CfnInstanceProfile(
            scope=self,
            id=f"instance_profile",
            instance_profile_name=f"instance_profile",
            roles=[instance_role.role_name]
        )

        # ===== #
        # batch #
        # ===== #
        batch_compute_resources = aws_batch.ComputeResources(
            vpc=vpc,
            maxv_cpus=4,
            minv_cpus=0,
            security_groups=[security_group],
            instance_role=instance_profile.attr_arn,
            type=aws_batch.ComputeResourceType.SPOT
        )

        batch_compute_environment = aws_batch.ComputeEnvironment(
            scope=self,
            id="batch_compute_environment",
            compute_environment_name="batch_compute_environment",
            compute_resources=batch_compute_resources,
            service_role=batch_role
        )

        job_role = aws_iam.Role(
            scope=self,
            id=f"job_role",
            role_name=f"job_role",
            assumed_by=aws_iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )

        job_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_managed_policy_arn(
                scope=self,
                id=f"AmazonECSTaskExecutionRolePolicy",
                managed_policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"

            )
        )

        job_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_managed_policy_arn(
                scope=self,
                id=f"AmazonS3FullAccess",
                managed_policy_arn="arn:aws:iam::aws:policy/AmazonS3FullAccess"

            )
        )

        job_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_managed_policy_arn(
                scope=self,
                id=f"CloudWatchLogsFullAccess",
                managed_policy_arn="arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
            )
        )

        self.batch_job_queue = aws_batch.JobQueue(
            scope=self,
            id=f"job_queue",
            job_queue_name=f"job_queue",
            compute_environments=[
                aws_batch.JobQueueComputeEnvironment(
                    compute_environment=batch_compute_environment,
                    order=1
                )
            ],
            priority=1
        )

        # ECR repository
        ecr_repository = aws_ecr_assets.DockerImageAsset(
            scope=self,
            id=f"ecr_image",
            directory="./docker",
            repository_name=f"repository"
        )

        # get image from ECR
        container_image = aws_ecs.ContainerImage.from_ecr_repository(
            repository=ecr_repository.repository
        )

        # job define
        # pass `S3_BUCKET` as environment argument.
        self.batch_job_definition = aws_batch.JobDefinition(
            scope=self,
            id=f"job_definition",
            job_definition_name=f"job_definition",
            container=aws_batch.JobDefinitionContainer(
                image=container_image,
                environment={
                    "S3_BUCKET": f"{S3_BUCKET}"
                },
                job_role=job_role,
                vcpus=1,
                memory_limit_mib=1024
            )
        )
