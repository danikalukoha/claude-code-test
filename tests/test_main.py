from datetime import datetime, timezone
from unittest.mock import MagicMock
from s3_lister.main import list_buckets


def make_mock_client(buckets):
    client = MagicMock()
    client.list_buckets.return_value = {"Buckets": buckets}
    return client


def test_list_buckets_returns_table_rows():
    buckets = [
        {"Name": "my-bucket", "CreationDate": datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)},
        {"Name": "another-bucket", "CreationDate": datetime(2023, 6, 1, 8, 0, 0, tzinfo=timezone.utc)},
    ]
    rows = list_buckets(client=make_mock_client(buckets))
    assert rows == [
        ("my-bucket", "2024-01-15 10:30:00 UTC"),
        ("another-bucket", "2023-06-01 08:00:00 UTC"),
    ]


def test_list_buckets_empty():
    rows = list_buckets(client=make_mock_client([]))
    assert rows == []


def test_list_buckets_single():
    buckets = [
        {"Name": "solo", "CreationDate": datetime(2022, 3, 10, 0, 0, 0, tzinfo=timezone.utc)},
    ]
    rows = list_buckets(client=make_mock_client(buckets))
    assert len(rows) == 1
    assert rows[0][0] == "solo"
