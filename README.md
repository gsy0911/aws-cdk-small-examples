# AWS CDK small Examples

This repository contains a set of example projects for the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk).

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
| [batch-stepfunctions]() | Creating a VPC and AWS Batch using ECR which already pushed, and invoke AWS Batch via StepFunctions with CloudWatch Events. |
| [lambda-stepfunctions]() | Creating a multiple Lambda with package, and invoke StepFunctions. |
| [lambda-creating-lambda_layers]() | Creating a Lambda which puts a zip file for LambdaLayers in S3 |
|  |  |

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