# batch-stepfunctions-nested


## generating resources


![image](./pics/aws-cdk-small-examples-batch-stepfunction-nested.png)

* VPC
* AWS Batch
* StepFunctions
* CloudWatch Events
* IAM Role

## Why using StepFunctions ?

Although CloudWatch Events is also able to invoke AWS Batch,
it is not flexible to pass arguments through CloudWatch Events.

In addition, AWS Batch may be used within StepFunctions utilizing other AWS services, such as Lambda.

# References

* [AWS CDKでネストされたスタックを作ってみる](https://dev.classmethod.jp/articles/aws-cdk-cfn-nest-stack/)
