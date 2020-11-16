from aws_cdk import (
    aws_glue as glue,
    aws_stepfunctions as sfn,
    aws_s3_assets as s3_assets,
    aws_stepfunctions_tasks as sfn_tasks,
    aws_iam as iam,
    core,
)


class GlueStepfunctionsStack(core.Stack):
    """

    """

    # version references
    # see: https://docs.aws.amazon.com/glue/latest/dg/add-job.html
    # accepted pattern: ^\w+\.\w+$
    GLUE_VERSION_0_9 = "0.9"
    GLUE_VERSION_1_0 = "1.0"
    GLUE_VERSION_2_0 = "2.0"

    # GlueJobCommand
    # see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-glue-job-jobcommand.html
    GLUE_JOB_COMMAND_PYTHON_SHELL = "pythonshell"
    GLUE_JOB_COMMAND_GLUE_ETL = "glueetl"

    # GlueWorkerType
    GLUE_WORKER_TYPE_STANDARD = "Standard"
    GLUE_WORKER_TYPE_G_1X = "G.1X"
    GLUE_WORKER_TYPE_G_2X = "G.2X"

    def __init__(self, app: core.App, cfn_name: str, stack_env):
        super().__init__(scope=app, id=f"{cfn_name}-{stack_env}")

        glue_code = s3_assets.Asset(
            scope=self,
            id=f"{cfn_name}-glue-script",
            path="./glue_script/glue_job_script.py",
        )

        glue_s3_access_role = iam.Role(
            scope=self,
            id=f"glue_s3_access_role_{stack_env}",
            role_name=f"glue_s3_access_role_{stack_env}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )

        # add policy to access S3
        glue_s3_access_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=["*"],
                actions=["s3:*"]
            )
        )

        # add policy to access CloudWatch Logs
        glue_s3_access_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
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

        # glue
        glue_job = glue.CfnJob(
            scope=self,
            id=f"{cfn_name}-glue-job",
            command=glue.CfnJob.JobCommandProperty(
                # glueetl or pythonshell
                name=self.GLUE_JOB_COMMAND_GLUE_ETL,
                script_location=f"s3://{glue_code.s3_bucket_name}/{glue_code.s3_object_key}"
            ),
            # set role-name!
            role=glue_s3_access_role.role_name,
            glue_version=self.GLUE_VERSION_2_0,
            number_of_workers=2,
            worker_type=self.GLUE_WORKER_TYPE_STANDARD,
            timeout=1800
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
            task=sfn_tasks.RunGlueJobTask(
                glue_job_name=f"{cfn_name}-glue-job",

            ),
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
    GlueStepfunctionsStack(app, "GlueStepfunctions", "prod")
    app.synth()


if __name__ == "__main__":
    main()
