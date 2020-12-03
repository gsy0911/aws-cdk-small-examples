from aws_cdk import (
    aws_lambda as lambda_,
    core,
)


class LambdaContainer(core.Stack):
    def __init__(self, app: core.App, _id: str):
        super().__init__(scope=app, id=_id)

        _ = lambda_.DockerImageFunction(
            scope=self,
            id="container_function",
            code=lambda_.DockerImageCode.from_image_asset(
                directory="docker",
                repository_name="lambda_container_example"
            )
        )


def main():
    app = core.App()
    LambdaContainer(app, "LambdaContainer")
    app.synth()


if __name__ == "__main__":
    main()
