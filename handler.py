"""
This lambda function serves the purpose to evaluate if an AWS Config rule is
compliant. It's written to check if AWS::S3::Bucket resources with versioning
enabled have a lifecycle policy. It does not check what is configured in the
lifecycle policy.
Based on https://github.com/soroushatarod/aws-config-rule-public-security-group
"""
import boto3
import json

APPLICABLE_RESOURCES = ["AWS::S3::Bucket"]
IGNORE_BUCKETS = []
COMPLIANT = "COMPLIANT"
NON_COMPLIANT = "NON_COMPLIANT"
NOT_APPLICABLE = "NOT_APPLICABLE"


def evaluate_compliance(configuration_item: dict) -> dict:
    """Evaluates the resource compliance

    Parameters
    ----------
    configuration_item : dict
        This is the data about the resource which got fetched from cloudtrail
        and is passed from AWS Config
    """
    if configuration_item["resourceType"] not in APPLICABLE_RESOURCES:
        return {
            "compliance_type": "NOT_APPLICABLE",
            "annotation": "The rule doesn't apply to resources of type " +
                          configuration_item["resourceType"] + "."
        }

    if configuration_item["configurationItemStatus"] == "ResourceDeleted":
        return {
            "compliance_type": "NOT_APPLICABLE",
            "annotation": ("The configurationItem was deleted and "
                           "therefore cannot be validated.")
        }

    bucket_name = configuration_item['configuration']['name']

    if bucket_name not in IGNORE_BUCKETS:
        suppl_config = configuration_item['supplementaryConfiguration']
        vers_status = suppl_config['BucketVersioningConfiguration']['status']
        if vers_status == 'Enabled':
            if 'BucketLifecycleConfiguration' in suppl_config:
                compliance_type = COMPLIANT
                annotation_message = ("Bucket {b} has versioning enabled and "
                                      "one or more Lifecycle rules."
                                      ).format(b=bucket_name)
            else:
                compliance_type = NON_COMPLIANT
                annotation_message = ("Bucket {b} has versioning enabled but "
                                      "no Lifecycle rules."
                                      ).format(b=bucket_name)

        else:
            compliance_type = NOT_APPLICABLE
            annotation_message = ("Bucket {b} has no versioning enabled. "
                                  "No Lifecycle rules enforced."
                                  ).format(b=bucket_name)

    return {
        "compliance_type": compliance_type,
        "annotation": annotation_message
    }


def lambda_handler(event: dict, context):
    """
    Function to invoke this lambda function.
    Invokes a function to evaluate S3 Bucket resource compliance
    and returns the evlaution result to AWS config.

    Parameters
    ----------
    event : dict
        AWS Lambda uses this parameter to pass in event data to the handler
    context
         This object provides methods and properties that provide information
         about the invocation, function, and execution environment.
         It's passed to every lambda function. It's unused here.
    """
    print("Incoming Event:")
    print(event)

    if event['version'] != '1.0':
        print("Warning: Unkown event version {v}. "
              "Lambda might fail.").format(v=event['version'])

    invoking_event = json.loads(event['invokingEvent'])
    print("Invoking Event JSON:")
    print(json.dumps(invoking_event))
    configuration_item = invoking_event["configurationItem"]

    evaluation = evaluate_compliance(configuration_item)

    config = boto3.client('config')
    config_item = invoking_event['configurationItem']
    evaluations = [
        {
            'ComplianceResourceType': config_item['resourceType'],
            'ComplianceResourceId': config_item['resourceId'],
            'ComplianceType': evaluation["compliance_type"],
            "Annotation": evaluation["annotation"],
            'OrderingTimestamp': config_item['configurationItemCaptureTime']
        },
    ]

    config.put_evaluations(
        Evaluations=evaluations,
        ResultToken=event['resultToken'])

    print("Evaluation results:")
    print(evaluations)
