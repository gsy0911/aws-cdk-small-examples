from aws_cdk import (
    core,
    aws_lambda as lambda_,
    aws_apigateway as apigw_
)


class ApiCorsLambdaStack(core.Stack):

    def __init__(self, scope: core.App, id_: str, **kwargs) -> None:
        super().__init__(scope, id_, **kwargs)

        base_lambda = lambda_.Function(
            self, 'ApiCorsLambda',
            handler='lambda_handler.handler',
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.asset('lambda_script'),
        )

        base_api = apigw_.RestApi(
            scope=self,
            id='ApiGatewayWithCors',
            rest_api_name='ApiGatewayWithCors'
        )

        example_entity = base_api.root.add_resource('example')
        example_entity_lambda_integration = apigw_.LambdaIntegration(
            handler=base_lambda,
            proxy=False,
            integration_responses=[
                apigw_.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
            ]
        )
        example_entity.add_method(
            http_method='GET',
            integration=example_entity_lambda_integration,
            method_responses=[
                apigw_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True,
                    }
                )
            ]
        )

        self.add_cors_options(example_entity)

    @staticmethod
    def add_cors_options(apigw_resource):
        mock_integration = apigw_.MockIntegration(
            integration_responses=[
                apigw_.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                        'method.response.header.Access-Control-Allow-Origin': "'*'",
                        'method.response.header.Access-Control-Allow-Methods': "'GET,OPTIONS'"
                    }
                ),
            ],
            passthrough_behavior=apigw_.PassthroughBehavior.WHEN_NO_MATCH,
            request_templates={"application/json": "{\"statusCode\":200}"}
        )

        apigw_resource.add_method(
            http_method='OPTIONS',
            integration=mock_integration,
            method_responses=[
                apigw_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Headers': True,
                        'method.response.header.Access-Control-Allow-Methods': True,
                        'method.response.header.Access-Control-Allow-Origin': True,
                    }
                )
            ]
        )


def main():
    app = core.App()
    ApiCorsLambdaStack(app, "ApiCorsLambdaStack")
    app.synth()


if __name__ == "__main__":
    main()
