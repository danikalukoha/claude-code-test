import pytest
from unittest.mock import patch
from env_inspector.main import is_sensitive, get_env


@pytest.mark.parametrize("name,expected", [
    ("AWS_ACCESS_KEY_ID", True),
    ("GITHUB_TOKEN", True),
    ("DB_SECRET", True),
    ("DB_PASSWORD", True),
    ("MY_CREDENTIAL", True),
    ("HOME", False),
    ("PATH", False),
    ("USER", False),
    ("MY_KEY", True),
])
def test_is_sensitive(name, expected):
    assert is_sensitive(name) == expected


FAKE_ENV = {
    "HOME": "/home/user",
    "PATH": "/usr/bin:/bin",
    "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE",
    "GITHUB_TOKEN": "ghp_secret",
    "USER": "alice",
    "SHELL": "/bin/bash",
}


def test_get_env_excludes_sensitive():
    with patch("env_inspector.main.os.environ", FAKE_ENV):
        rows = get_env()
    names = [r[0] for r in rows]
    assert "AWS_ACCESS_KEY_ID" not in names
    assert "GITHUB_TOKEN" not in names


def test_get_env_includes_safe():
    with patch("env_inspector.main.os.environ", FAKE_ENV):
        rows = get_env()
    names = [r[0] for r in rows]
    assert "HOME" in names
    assert "USER" in names


def test_get_env_search_filter():
    with patch("env_inspector.main.os.environ", FAKE_ENV):
        rows = get_env(search="shell")
    assert rows == [("SHELL", "/bin/bash")]


def test_get_env_search_no_match():
    with patch("env_inspector.main.os.environ", FAKE_ENV):
        rows = get_env(search="zzznomatch")
    assert rows == []


def test_get_env_sorted():
    with patch("env_inspector.main.os.environ", FAKE_ENV):
        rows = get_env()
    names = [r[0] for r in rows]
    assert names == sorted(names)
