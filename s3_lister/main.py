import boto3
from tabulate import tabulate


def list_buckets(client=None):
    if client is None:
        client = boto3.client("s3")
    response = client.list_buckets()
    return [
        (b["Name"], b["CreationDate"].strftime("%Y-%m-%d %H:%M:%S UTC"))
        for b in response.get("Buckets", [])
    ]


def main():
    rows = list_buckets()
    if not rows:
        print("No S3 buckets found.")
        return
    print(tabulate(rows, headers=["Bucket Name", "Creation Date"], tablefmt="grid"))


if __name__ == "__main__":
    main()
