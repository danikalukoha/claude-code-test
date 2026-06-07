import platform
import socket


def get_system_info():
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": platform.python_version(),
        "hostname": socket.gethostname(),
    }


def main():
    info = get_system_info()
    print(f"OS:             {info['os']} {info['os_version']}")
    print(f"Python version: {info['python_version']}")
    print(f"Hostname:       {info['hostname']}")


if __name__ == "__main__":
    main()
