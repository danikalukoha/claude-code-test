import argparse
import json
import logging
import os
import sys
from tabulate import tabulate

from ec2_janitor.aws import make_client, list_instances
from ec2_janitor.checks import audit_instances

logger = logging.getLogger(__name__)


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="ec2-janitor",
        description="Audit EC2 instances for missing required tags.",
    )
    parser.add_argument(
        "--region",
        default=os.environ.get("AWS_REGION", "us-east-1"),
        help="AWS region (default: $AWS_REGION or us-east-1)",
    )
    parser.add_argument(
        "--required-tags",
        default="Owner,Environment",
        help="Comma-separated list of required tag keys (default: Owner,Environment)",
    )
    parser.add_argument(
        "--json-out",
        metavar="FILE",
        help="Write JSON results to this file path in addition to stdout table",
    )
    return parser.parse_args(argv)


def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stderr,
    )


def main(argv=None):
    _setup_logging()
    args = _parse_args(argv)
    required_tags = [t.strip() for t in args.required_tags.split(",") if t.strip()]

    logger.info("Region: %s | Required tags: %s", args.region, required_tags)

    client = make_client(args.region)
    instances = list_instances(client)
    logger.info("Found %d instance(s)", len(instances))

    reports = audit_instances(instances, required_tags)

    rows = [
        [
            r.instance_id,
            r.state,
            ", ".join(r.missing_tags) if r.missing_tags else "—",
            "FAIL" if r.has_violations else "OK",
        ]
        for r in reports
    ]

    headers = ["Instance ID", "State", "Missing Tags", "Status"]
    print(tabulate(rows, headers=headers, tablefmt="grid"))

    if args.json_out:
        payload = [
            {
                "instance_id": r.instance_id,
                "state": r.state,
                "missing_tags": r.missing_tags,
                "status": "FAIL" if r.has_violations else "OK",
            }
            for r in reports
        ]
        with open(args.json_out, "w") as fh:
            json.dump(payload, fh, indent=2)
        logger.info("JSON results written to %s", args.json_out)

    violations = any(r.has_violations for r in reports)
    sys.exit(1 if violations else 0)
