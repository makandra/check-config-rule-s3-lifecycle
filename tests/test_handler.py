import pytest
import json
from handler import evaluate_compliance


@pytest.fixture
def compliant_s3_bucket():
    with open('tests/jsons/compliant_s3_bucket.json') as json_file:
        return json.load(json_file)["configurationItem"]


@pytest.fixture
def no_versioning_s3_bucket():
    with open('tests/jsons/no_versioning_s3_bucket.json') as json_file:
        return json.load(json_file)["configurationItem"]


@pytest.fixture
def missing_lifecycle_s3_bucket():
    with open('tests/jsons/missing_lifecycle_s3_bucket.json') as json_file:
        return json.load(json_file)["configurationItem"]


@pytest.fixture
def wrong_resource_type():
    with open('tests/jsons/wrong_resource_type.json') as json_file:
        return json.load(json_file)["configurationItem"]


@pytest.fixture
def deleted_s3_bucket():
    with open('tests/jsons/deleted_s3_bucket.json') as json_file:
        return json.load(json_file)["configurationItem"]


def test_compliant_s3_bucket_is_compliant(compliant_s3_bucket):
    assert evaluate_compliance(compliant_s3_bucket) == {
        "compliance_type": 'COMPLIANT',
        "annotation": ("Bucket bestBucket has versioning enabled and "
                       "one or more Lifecycle rules.")
    }


def test_no_versioning_s3_bucket_is_not_applicable(no_versioning_s3_bucket):
    assert evaluate_compliance(no_versioning_s3_bucket) == {
        "compliance_type": 'NOT_APPLICABLE',
        "annotation": ("Bucket bestBucket has no versioning enabled. "
                       "No Lifecycle rules enforced.")
    }


def test_versioning_without_lifecycle_s3_bucket_is_not_applicable(
        missing_lifecycle_s3_bucket):
    assert evaluate_compliance(missing_lifecycle_s3_bucket) == {
        "compliance_type": 'NON_COMPLIANT',
        "annotation": ("Bucket bestBucket has versioning enabled but "
                       "no Lifecycle rules.")
    }


def test_wrong_resource_type_is_not_applicable(
        wrong_resource_type):
    assert evaluate_compliance(wrong_resource_type) == {
        "compliance_type": 'NOT_APPLICABLE',
        "annotation": ("The rule doesn't apply to resources of type "
                       "AWS::S3::fakeBucket.")
    }


def test_deleted_s3_bucket_is_not_applicable(
        deleted_s3_bucket):
    assert evaluate_compliance(deleted_s3_bucket) == {
        "compliance_type": 'NOT_APPLICABLE',
        "annotation": ("The configurationItem was deleted and "
                       "therefore cannot be validated.")
    }
