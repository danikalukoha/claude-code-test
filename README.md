# s3-lister

A small Python CLI that lists your AWS S3 buckets and prints their names and creation dates as a formatted table.

## Requirements

- Python 3.8+
- AWS credentials configured (via `~/.aws/credentials`, environment variables, or IAM role)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m s3_lister.main
```

Example output:

```
+------------------+-------------------------+
| Bucket Name      | Creation Date           |
+==================+=========================+
| my-data-bucket   | 2023-04-10 12:00:00 UTC |
+------------------+-------------------------+
| logs-archive     | 2022-11-01 09:15:00 UTC |
+------------------+-------------------------+
```

## Running Tests

```bash
pytest tests/
```

Tests use `unittest.mock` — no real AWS calls are made.
