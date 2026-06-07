import json
import pytest
from unittest.mock import MagicMock, patch
import botocore.exceptions

from ec2_janitor.checks import audit_instance, audit_instances
from ec2_janitor.aws import make_client, list_instances
from ec2_janitor.cli import main


REQUIRED_TAGS = ["Owner", "Environment"]


def _make_instance(instance_id, tags: dict, state: str = "running") -> dict:
    return {
        "InstanceId": instance_id,
        "State": {"Name": state},
        "Tags": [{"Key": k, "Value": v} for k, v in tags.items()],
    }


def _mock_ec2_client(instances: list[dict]) -> MagicMock:
    """Return a boto3-shaped mock client that paginates the given instances."""
    client = MagicMock()
    client.describe_regions.return_value = {"Regions": [{"RegionName": "us-east-1"}]}
    paginator = MagicMock()
    paginator.paginate.return_value = [
        {"Reservations": [{"Instances": instances}]}
    ] if instances else [{"Reservations": []}]
    client.get_paginator.return_value = paginator
    return client


# ---------------------------------------------------------------------------
# checks.py unit tests (pure Python, no AWS)
# ---------------------------------------------------------------------------

def test_clean_instance_no_violations():
    instance = _make_instance("i-clean", {"Owner": "alice", "Environment": "prod"})
    report = audit_instance(instance, REQUIRED_TAGS)
    assert not report.has_violations
    assert report.missing_tags == []


def test_untagged_instance_all_missing():
    instance = _make_instance("i-bare", {})
    report = audit_instance(instance, REQUIRED_TAGS)
    assert report.has_violations
    assert set(report.missing_tags) == {"Owner", "Environment"}


def test_partial_tags_one_missing():
    instance = _make_instance("i-partial", {"Owner": "bob"})
    report = audit_instance(instance, REQUIRED_TAGS)
    assert report.has_violations
    assert report.missing_tags == ["Environment"]


def test_audit_instances_mixed():
    instances = [
        _make_instance("i-ok", {"Owner": "alice", "Environment": "prod"}),
        _make_instance("i-bad", {}),
    ]
    reports = audit_instances(instances, REQUIRED_TAGS)
    assert len(reports) == 2
    ok = next(r for r in reports if r.instance_id == "i-ok")
    bad = next(r for r in reports if r.instance_id == "i-bad")
    assert not ok.has_violations
    assert bad.has_violations


# ---------------------------------------------------------------------------
# aws.py tests (mocked boto3)
# ---------------------------------------------------------------------------

def test_list_instances_empty():
    client = _mock_ec2_client([])
    assert list_instances(client) == []


def test_list_instances_returns_instances():
    inst = _make_instance("i-abc", {"Owner": "x", "Environment": "dev"})
    client = _mock_ec2_client([inst])
    result = list_instances(client)
    assert len(result) == 1
    assert result[0]["InstanceId"] == "i-abc"


def test_missing_credentials_exits_2():
    with patch("ec2_janitor.aws.boto3.client") as mock_boto:
        mock_boto.return_value.describe_regions.side_effect = (
            botocore.exceptions.NoCredentialsError()
        )
        with pytest.raises(SystemExit) as exc:
            make_client("us-east-1")
    assert exc.value.code == 2


def test_client_error_exits_2():
    with patch("ec2_janitor.aws.boto3.client") as mock_boto:
        mock_boto.return_value.describe_regions.side_effect = (
            botocore.exceptions.ClientError(
                {"Error": {"Code": "UnauthorizedOperation", "Message": "Denied"}},
                "DescribeRegions",
            )
        )
        with pytest.raises(SystemExit) as exc:
            make_client("us-east-1")
    assert exc.value.code == 2


# ---------------------------------------------------------------------------
# cli.py end-to-end tests (mocked make_client + list_instances)
# ---------------------------------------------------------------------------

def _patch_cli(instances):
    client = _mock_ec2_client(instances)
    return patch("ec2_janitor.cli.make_client", return_value=client), \
           patch("ec2_janitor.cli.list_instances", return_value=instances)


def test_cli_clean_instance_exits_zero():
    instances = [_make_instance("i-ok", {"Owner": "alice", "Environment": "prod"})]
    p1, p2 = _patch_cli(instances)
    with p1, p2:
        with pytest.raises(SystemExit) as exc:
            main(["--region", "us-east-1", "--required-tags", "Owner,Environment"])
    assert exc.value.code == 0


def test_cli_untagged_instance_exits_one():
    instances = [_make_instance("i-bad", {})]
    p1, p2 = _patch_cli(instances)
    with p1, p2:
        with pytest.raises(SystemExit) as exc:
            main(["--region", "us-east-1", "--required-tags", "Owner,Environment"])
    assert exc.value.code == 1


def test_cli_json_out(tmp_path):
    instances = [_make_instance("i-bad", {})]
    out = tmp_path / "results.json"
    p1, p2 = _patch_cli(instances)
    with p1, p2:
        with pytest.raises(SystemExit):
            main(["--region", "us-east-1", "--json-out", str(out)])
    data = json.loads(out.read_text())
    assert isinstance(data, list)
    assert data[0]["status"] == "FAIL"
    assert data[0]["instance_id"] == "i-bad"
