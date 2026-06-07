import os
import argparse
from tabulate import tabulate

REDACTED_PATTERNS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "PASSWD", "CREDENTIAL")


def is_sensitive(name: str) -> bool:
    upper = name.upper()
    return any(p in upper for p in REDACTED_PATTERNS)


def get_env(search: str = "") -> list[tuple[str, str]]:
    rows = []
    for name, value in sorted(os.environ.items()):
        if is_sensitive(name):
            continue
        if search and search.lower() not in name.lower():
            continue
        rows.append((name, value))
    return rows


def main():
    parser = argparse.ArgumentParser(description="Inspect environment variables safely.")
    parser.add_argument("--search", "-s", default="", help="Filter variables by name (case-insensitive)")
    args = parser.parse_args()

    rows = get_env(search=args.search)
    if not rows:
        print("No matching environment variables found.")
        return
    print(tabulate(rows, headers=["Variable", "Value"], tablefmt="grid"))


if __name__ == "__main__":
    main()
