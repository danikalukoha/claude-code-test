import platform
import socket
from hello import get_system_info


def test_get_system_info_keys():
    info = get_system_info()
    assert set(info.keys()) == {"os", "os_version", "python_version", "hostname"}


def test_get_system_info_values_match_platform():
    info = get_system_info()
    assert info["os"] == platform.system()
    assert info["os_version"] == platform.version()
    assert info["python_version"] == platform.python_version()
    assert info["hostname"] == socket.gethostname()


def test_get_system_info_nonempty():
    info = get_system_info()
    for key, value in info.items():
        assert value, f"{key} should not be empty"
