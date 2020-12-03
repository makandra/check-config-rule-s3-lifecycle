This lambda function serves the purpose to evaluate if an AWS Config rule is
compliant. It's written to check if AWS::S3::Bucket resources with versioning
enabled have a lifecycle policy. It does not check what is configured in the
lifecycle policy.
Based on https://github.com/soroushatarod/aws-config-rule-public-security-group

# Deploy requirements

You need [serverless](https://www.serverless.com/) installed locally (or on your deployment/CI/CD server). 

You need to setup [AWS Config](https://aws.amazon.com/config/) (and therefore [Cloudtrail](https://aws.amazon.com/cloudtrail/) to get it to work. For the SNS notifcations you have to enable [SSM](https://aws.amazon.com/systems-manager/).

# Deployment

Before you deploy you need to have a `parameters.yml`. You can copy the `parameters.yml.example` as a starting point. You should create a new git branch when adding a `parameters.yml` because it stores deployment dependent configuration (Account specific `ARN`s). Please check for existing branches before you start. All parameters need to have a value (even though some might not be used). If you omit a parameter the validation of the generated Cloudformation template will fail. Otherwise the deploy will fail.

## Parameters

### `createConfigResources`

If set to `true`, an `AWS::Config::ConfigRule` and an `AWS::Config::RemediationConfiguration` resource will be created. The Rule will be triggered whenever a S3 bucket resource is changed. The remediation configuration triggers a Publish SNS Message action via SSM so that you can get notified about an issue in the configuration. So it does not try to fix the "problem" but it notifies you that a bucket is missing a lifecycle policy.

If you set this to `false` only the Lambda function will be deployed and you have to create `Config` rules yourself.

### `ssmServiceRole`

The `ARN` of the IAM role which will publish a SNS message via SSM is expected. You need to create this resource yourself. It's not in the scope of this Repository. It needs the following permissions:

- `sns:ListTagsForResource`
- `sns:ListSubscriptionsByTopic`
- `sns:GetTopicAttributes`
- `sns:ListTopics`
- `sns:GetPlatformApplicationAttributes`
- `sns:GetSubscriptionAttributes`
- `sns:ListSubscriptions`
- `sns:CheckIfPhoneNumberIsOptedOut`
- `sns:ListPhoneNumbersOptedOut`
- `sns:ListEndpointsByPlatformApplication`
- `sns:GetEndpointAttributes`
- `sns:Publish`
- `sns:GetSMSAttributes`
- `sns:ListPlatformApplications`

Amazon's default policies `AmazonEC2RoleforSSM` and `AmazonSSMAutomationRole` should be assigned to the role too. You may create a role with fewer permissions, but that's beyond the scope of this README.

### `snsTopic`

The `ARN` of the snsTopic which will receive the notifications by the remediation action. You need to create this snsTopic yourself.

## Deploy

The deploy is a usual `serverless` deployment. You should read the documentation how you can modify the deployment behaviour and how it works. If you just want to get started with this without getting into `serverless` you can use `serverless deploy` to deploy the lambda. If you are using multiple profiles be sure to specify that in the env variable `AWS_PROFILE="<profilename>" serverless deploy`.

Serverless compares your function with the already deployed function (if there is any) via checksums when you attempt a deploy. If there is no change, the deploy will not be executed. If you made changes to your configuration or the Cloudformation configuration it may not be recognized. You can force the deploy then via `serverless deploy --force`. 

# Development requirements

You need the deploy requirements and [Poetry](https://python-poetry.org/). Also you should have something like [pyenv](https://github.com/pyenv/pyenv) to install a suitable python version. Dependencies like `flake8` and `pytest` will be installed via `Poetry`.

## Tests and linting

For linting you can run `poetry run flake8`

To run tests you can run `poetry run py.test`
Please always run tests from the repository root dir to avoid file path issues (there is no smart logic to detect from which directory you run your tests).

There is no 100% test coverage.
