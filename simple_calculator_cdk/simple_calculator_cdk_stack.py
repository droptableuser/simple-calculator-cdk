import json
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as lambda_,
    RemovalPolicy,
    aws_apigateway as api_gw,
)
from constructs import Construct
from os import path


class SimpleCalculatorCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # create a named Bucket, so that our lambda function can use it hardcoded
        # a bucket with the same name cannot exist
        bucket = s3.Bucket(self, "SimpleCalcHistory", bucket_name="calc-history",
                           access_control=s3.BucketAccessControl.PRIVATE,
                           removal_policy=RemovalPolicy.DESTROY, auto_delete_objects=True)
        # upload the function code from the folder ./lambda_function
        calc_fn = lambda_.Function(self, "SimpleCalculatorLambda",
                                   runtime=lambda_.Runtime.NODEJS_16_X,
                                   handler="index.handler",
                                   code=lambda_.Code.from_asset(path.join(".", "lambda_function")))
        # grant r/w access for the bucket to the lambda function
        bucket.grant_read_write(calc_fn)
        # create an REST API gateway. We do not create parameter mappings to safe on code here, the logic
        # in the function needed for this is minimally
        api = api_gw.RestApi(self, "SimpleCalcApi",
                             rest_api_name="Simple Calculator API")
        # integrate the API and Lambda function. This will give execute permissions for the function to the API gateway
        calc_integration = api_gw.LambdaIntegration(
            calc_fn, request_templates={"application/json": "{'statusCode':'200'}"})
        # build the query path for GET request first /{a}/{b}/{op}
        a = api.root.add_resource("{a}")
        b = a.add_resource("{b}")
        op = b.add_resource("{op}")
        # add GET method to query path
        op.add_method("GET", calc_integration)

        # create POST method as a root request
        api.root.add_method("POST", calc_integration)

'''
For a more mature application stack/CD pipeline, you would separate the deployments into several stacks to limit dependencies and update code for generic names:
BucketCdkStack: Generate bucket for history (Bucket Name is required for the Lambda Function)
LambdaCdkStack: Dynamically update the bucket-name variable in JS via lookup or cross stack reference
ApiGatewayCdkStack: Dynamically update the x-amazon-apigateway-integration.uri for the OpenAPI JSON export for each method with the ARN of the Lambda Function before importing
'''
# class ApiGatewayCdkStack(Stack):
#     def __init__(self, scope: Construct, construct_id: str, lambda_func: lambda_.Function, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)
#
#         arn = lambda_func.resource_arns_for_grant_invoke
#       TODO rewrite openapi JSON with ARN
#         api_definition = api_gw.SpecRestApi(self,"calc-api",api_definition=api_gw.ApiDefinition.from_asset(path.join(".","API/openapi.json")))
#
