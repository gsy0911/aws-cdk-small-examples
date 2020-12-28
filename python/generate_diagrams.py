from diagrams import Diagram, Edge, Cluster
from diagrams.aws.compute import (
    Batch,
    EC2,
    EC2ContainerRegistry,
    Lambda,
)
from diagrams.aws.database import (
    Dynamodb
)
from diagrams.aws.network import (
    ELB,
    APIGateway,
    CloudFront,
    VPC
)
from diagrams.aws.storage import (
    S3
)
from diagrams.aws.integration import (
    StepFunctions,
    SQS
)
from diagrams.aws.analytics import (
    Glue
)
from diagrams.aws.management import (
    Cloudwatch
)
from diagrams.aws.security import (
    IAMRole
)
from diagrams.aws.general import (
    GenericSDK as SFn_TASK
)


def apigw_dynamodb_lambda():
    stack_objective = "apigw-dynamodb-lambda"
    with Diagram(stack_objective, outformat="png", filename=f"{stack_objective}/pics/arch", show=False):
        apigw = APIGateway("/task")
        dynamodb = Dynamodb("DynamoDB")
        apigw >> Edge(label="POST /example/update") >> Lambda("update status") >> Edge(label="update item") >> dynamodb
        apigw >> Edge(label="POST /example") >> Lambda("producer") >> Edge(label="put item") >> dynamodb
        apigw >> Edge(label="GET /example") >> Lambda("consumer") >> Edge(label="read all item") >> dynamodb


def apigw_dynamodb_sfn_with_heavytask():
    stack_objective = "apigw-dynamodb-sfn-with-heavytask"
    with Diagram(stack_objective, outformat="png", filename=f"{stack_objective}/pics/arch", show=False):
        sqs = SQS("SQS")
        apigw = APIGateway("/task") >> Lambda("integration") >> [sqs, Dynamodb("DynamoDB")]

        timer_lambda = Lambda("timer lambda")
        sqs << Edge(label="dequeue") << timer_lambda << Cloudwatch("cron")

        with Cluster(label="StepFunctions", direction="TB"):
            sfn_start = SFn_TASK("update DynamoDB\nset `running`")
            sfn_start \
                >> Lambda("Some Task") \
                >> [SFn_TASK("update DynamoDB\nset `success`"), SFn_TASK("update DynamoDB\nset `failure`")]

        # invoke sfn from Lambda
        timer_lambda >> sfn_start


def apigw_lambda():
    stack_objective = "apigw-lambda"
    with Diagram(stack_objective, outformat="png", filename=f"{stack_objective}/pics/arch", show=False):
        APIGateway("APIGateway") >> Edge(label="integration") >> Lambda("task")


def batch_stepfunctions():
    stack_objective = "batch-stepfunctions"
    with Diagram(stack_objective, outformat="png", filename=f"{stack_objective}/pics/arch", show=False):
        with Cluster("StepFunctions"):
            batch = Batch("AWS Batch")

        Cloudwatch("CloudWatch Event") >> Edge(label="cron") \
            >> batch << Edge(label="image") << EC2ContainerRegistry("ECR")

        batch >> Edge(label="access through IAM Role") >> S3("S3")


def main():
    apigw_dynamodb_lambda()
    apigw_dynamodb_sfn_with_heavytask()
    apigw_lambda()
    batch_stepfunctions()


if __name__ == "__main__":
    main()
