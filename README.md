# ec2-janitor

A production-style Python CLI that audits EC2 instances for missing required tags.
Exits with code `1` if any violations are found, `0` if everything is clean.

---

## Install

```bash
pip install -e .
```

## Usage

```bash
# Default: checks Owner and Environment tags in us-east-1
ec2-janitor

# Custom region and tags
ec2-janitor --region eu-west-1 --required-tags Owner,Environment,CostCentre

# Also write results to a JSON file
ec2-janitor --region us-east-1 --json-out results.json
```

`--region` defaults to the `AWS_REGION` environment variable, then `us-east-1`.

## Example output

```
+---------------------+---------+---------------------+--------+
| Instance ID         | State   | Missing Tags        | Status |
+=====================+=========+=====================+========+
| i-0abc123def456789a | running | —                   | OK     |
+---------------------+---------+---------------------+--------+
| i-0deadbeefcafe001  | stopped | Owner, Environment  | FAIL   |
+---------------------+---------+---------------------+--------+
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | All instances are clean |
| 1 | One or more instances have violations |
| 2 | AWS credential or API error |

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Project layout

```
src/ec2_janitor/
  cli.py       # argparse entry point
  aws.py       # boto3 client wrapper
  checks.py    # tag audit logic
tests/
  test_ec2_janitor.py
```
