#!/usr/bin/env python3
import os

import aws_cdk as cdk

from simple_calculator_cdk.simple_calculator_cdk_stack import SimpleCalculatorCdkStack


app = cdk.App()
SimpleCalculatorCdkStack(app, "SimpleCalculatorCdkStack",)


app.synth()
