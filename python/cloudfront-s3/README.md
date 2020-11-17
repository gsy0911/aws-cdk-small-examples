# cloudfront-s3

![cdk-version](https://img.shields.io/badge/aws_cdk-1.73.0-green.svg)

## generating resources

![image](./pics/aws-cdk-small-examples-cloudfront-s3.png)

* S3
    * generate new `S3 Bucket`
    * deploy assets to `web/static` in the Bucket
* CloudFront
    * use Origin with the Bucket above
    * default domain (not custom domain)

## result

after you deploy, access via CloudFront-console domain name

![image](./pics/example_result.png)

# References

* [Qiita for the concept of CloudFront](https://qiita.com/NaokiIshimura/items/46994e67b712831c3016)
