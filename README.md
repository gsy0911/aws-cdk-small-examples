# AWS CDK small Examples

This repository contains a set of example projects for the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk).

## Environment

The code in this repository is checked under the environment below.

* [![macOS](https://img.shields.io/badge/macOS_Catalina-10.15.7-green.svg)]()
* [![cdk-version](https://img.shields.io/badge/aws_cdk-1.73.0-green.svg)](https://formulae.brew.sh/formula/aws-cdk)
* [![PythonVersion](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-377/)

# Python examples


## Deploy

In each directory,

```
$ cdk ls
```

and then,

```
$ cdk deploy {target_name}
```

## Contents

| Example | Description |
|:--:|:--:|
| [batch-stepfunctions](./python/batch-stepfunctions) | Creating a VPC and AWS Batch using ECR which already pushed, and invoke AWS Batch via StepFunctions with CloudWatch Events. |
| [lambda-stepfunctions]() | Creating a multiple Lambda with package, and invoke StepFunctions. |
| [lambda-creating-lambda_layers](./python/lambda-creating-lambda_layers) | Creating a Lambda which puts a zip file for LambdaLayers in S3. |
| [select-existing-resources]() | Select existing resource, VPC, Lambda, etc. |
| [apigateway-lambda]() |  |
| [apigateway-stepfunctions]() |  |
| [glue-stepfunctions]() | Creating a Glue Jobs, which will be used in StepFunctions. |


## Contents which will be added ?

* lambda
* vpc
* StepFunctions(lambda, SQS, SNS)
* Glue (Job, Crawler)
* Athena ?
* DynamoDB
* AWS Batch
* EKS
* Kinesis
* API Gateway
* CodeBuild ?
* CodeDeploy ?

# references

* [aws-samples/aws-cdk-examples](https://github.com/aws-samples/aws-cdk-examples)