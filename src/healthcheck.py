import socket
import sys

HEALTH_CHECK_MSG = b'\x01'


def check_health() -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('', 0))
        sock.sendto(HEALTH_CHECK_MSG, ('localhost', int(sys.argv[1])))
        sock.settimeout(1)
        sock.recvfrom(1)
        return True
    except Exception:
        return False
    finally:
        sock.close()


if __name__ == "__main__":
    healthy: bool = check_health()
    sys.exit(1 - int(healthy))
