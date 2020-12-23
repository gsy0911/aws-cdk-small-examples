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
    StepFunctions
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


def apigw_dynamodb_lambda():
    stack_objective = "apigw-dynamodb-lambda"
    with Diagram(stack_objective, outformat="png", filename=f"{stack_objective}/pics/arch", show=False):
        APIGateway("/task") >> [
            Edge(label="POST /example/update") >> Lambda("update status") >> Edge(label="update item"),
            Edge(label="POST /example") >> Lambda("producer") >> Edge(label="put item"),
            Edge(label="GET /example") >> Lambda("consumer") >> Edge(label="read all item"),
        ] >> Dynamodb("DynamoDB")


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
    # apigw_dynamodb_lambda()
    apigw_lambda()
    batch_stepfunctions()


if __name__ == "__main__":
    main()
