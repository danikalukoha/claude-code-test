import logging
import boto3
import botocore.exceptions

logger = logging.getLogger(__name__)


def make_client(region: str):
    """Return a boto3 EC2 client, raising SystemExit(2) on credential errors."""
    try:
        client = boto3.client("ec2", region_name=region)
        # Eagerly validate credentials with a cheap call.
        client.describe_regions(RegionNames=[region])
        return client
    except botocore.exceptions.NoCredentialsError:
        logger.error("No AWS credentials found. Configure via ~/.aws/credentials or environment variables.")
        raise SystemExit(2)
    except botocore.exceptions.ClientError as exc:
        logger.error("AWS API error while initialising client: %s", exc)
        raise SystemExit(2)


def list_instances(client) -> list[dict]:
    """Return a flat list of instance dicts from all reservations."""
    try:
        paginator = client.get_paginator("describe_instances")
        instances = []
        for page in paginator.paginate():
            for reservation in page["Reservations"]:
                instances.extend(reservation["Instances"])
        return instances
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list EC2 instances: %s", exc)
        raise SystemExit(2)
