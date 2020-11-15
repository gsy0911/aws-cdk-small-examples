from aws_cdk import (
    core,
    aws_ec2,
    aws_batch,
    aws_ecr,
    aws_ecs,
    aws_iam,
    aws_stepfunctions as aws_sfn,
    aws_stepfunctions_tasks as aws_sfn_tasks,
    aws_events,
    aws_events_targets,
)

ACCOUNT_NUMBER = ""
REGION = ""
ECR_REPOSITORY_NAME = ""
PROJECT_NAME = ""


class BatchEnvironment(core.Stack):
    """
    The class creates
    * VPC
    * Batch
    * StepFunctions
    * CloudWatch Event

    """
    # ECR-arn
    ECR_REPOSITORY_ARN = f"arn:aws:ecr:{REGION}:{ACCOUNT_NUMBER}:repository/{ECR_REPOSITORY_NAME}"

    def __init__(self, app: core.App, stack_name: str, stack_env: str):
        super().__init__(scope=app, id=f"{stack_name}-{stack_env}")

        # CIDR
        cidr = "192.168.0.0/24"

        # === #
        # vpc #
        # === #
        vpc = aws_ec2.Vpc(
            self,
            id=f"{stack_name}-{stack_env}-vpc",
            cidr=cidr,
            subnet_configuration=[
                # Public Subnet
                aws_ec2.SubnetConfiguration(
                    cidr_mask=28,
                    name=f"{stack_name}-{stack_env}-public",
                    subnet_type=aws_ec2.SubnetType.PUBLIC,
                )
            ],
        )

        security_group = aws_ec2.SecurityGroup(
            self,
            id=f'security-group-for-{stack_name}-{stack_env}',
            vpc=vpc,
            security_group_name=f'security-group-for-{stack_name}-{stack_env}',
            allow_all_outbound=True
        )

        batch_role = aws_iam.Role(
            scope=self,
            id=f"batch_role_for_{stack_name}-{stack_env}",
            role_name=f"batch_role_for_{stack_name}-{stack_env}",
            assumed_by=aws_iam.ServicePrincipal("batch.amazonaws.com")
        )

        batch_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_managed_policy_arn(
                scope=self,
                id=f"AWSBatchServiceRole-{stack_env}",
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
            id=f"instance_role_for_{stack_name}-{stack_env}",
            role_name=f"instance_role_for_{stack_name}-{stack_env}",
            assumed_by=aws_iam.ServicePrincipal("ec2.amazonaws.com")
        )

        instance_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_managed_policy_arn(
                scope=self,
                id=f"AmazonEC2ContainerServiceforEC2Role-{stack_env}",
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
            id=f"instance_profile_for_{stack_name}-{stack_env}",
            instance_profile_name=f"instance_profile_for_{stack_name}-{stack_env}",
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
            id=f"ProjectEnvironment-{stack_env}",
            compute_environment_name=f"ProjectEnvironmentBatch-{stack_env}",
            compute_resources=batch_compute_resources,
            service_role=batch_role
        )

        job_role = aws_iam.Role(
            scope=self,
            id=f"job_role_{stack_name}-{stack_env}",
            role_name=f"job_role_{stack_name}-{stack_env}",
            assumed_by=aws_iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )

        job_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_managed_policy_arn(
                scope=self,
                id=f"AmazonECSTaskExecutionRolePolicy_{stack_name}-{stack_env}",
                managed_policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"

            )
        )

        job_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_managed_policy_arn(
                scope=self,
                id=f"AmazonS3FullAccess_{stack_name}-{stack_env}",
                managed_policy_arn="arn:aws:iam::aws:policy/AmazonS3FullAccess"

            )
        )

        job_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_managed_policy_arn(
                scope=self,
                id=f"CloudWatchLogsFullAccess_{stack_name}-{stack_env}",
                managed_policy_arn="arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
            )
        )

        batch_job_queue = aws_batch.JobQueue(
            scope=self,
            id=f"job_queue_for_{stack_name}-{stack_env}",
            job_queue_name=f"job_queue_for_{stack_name}-{stack_env}",
            compute_environments=[
                aws_batch.JobQueueComputeEnvironment(
                    compute_environment=batch_compute_environment,
                    order=1
                )
            ],
            priority=1
        )

        # ECR repository
        ecr_repository = aws_ecr.Repository.from_repository_arn(
            scope=self,
            id=f"image_for_{stack_name}-{stack_env}",
            repository_arn=self.ECR_REPOSITORY_ARN
        )

        # get image from ECR
        container_image = aws_ecs.ContainerImage.from_ecr_repository(
            repository=ecr_repository
        )

        # job define
        # pass `S3_BUCKET` as environment argument.
        batch_job_definition = aws_batch.JobDefinition(
            scope=self,
            id=f"job_definition_for_{stack_env}",
            job_definition_name=f"job_definition_for_{stack_env}",
            container=aws_batch.JobDefinitionContainer(
                image=container_image,
                environment={
                    "S3_BUCKET": f"{YOUR_S3_BUCKET}"
                },
                job_role=job_role,
                vcpus=1,
                memory_limit_mib=1024
            )
        )

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
            id=f"batch_job_{stack_env}",
            job_definition=batch_job_definition,
            job_name=f"batch_job_{stack_env}_today",
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
            id=f"YourProjectSFn-{stack_env}",
            definition=definition
        )

        # ================ #
        # CloudWatch Event #
        # ================ #

        # Run every day at 21:30 JST
        # See https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html
        events_daily_process = aws_events.Rule(
            scope=self,
            id=f"DailySFnProcess-{stack_env}",
            schedule=aws_events.Schedule.cron(
                minute="30",
                hour="12",
                month='*',
                day="*",
                year='*'),
        )
        events_daily_process.add_target(aws_events_targets.SfnStateMachine(sfn_daily_process))


def main():
    app = core.App()
    BatchEnvironment(app, "your-project", "feature")
    BatchEnvironment(app, "your-project", "dev")
    BatchEnvironment(app, "your-project", "prod")
    app.synth()


if __name__ == "__main__":
    main()
