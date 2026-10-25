#!/usr/bin/env python3
"""Local demo target for sockmap — a loopback TCP server with a fake banner.

Standard library only:

    python examples/banner_server.py --port 2222
    sockmap scan-ports --ports 2222,22,80

It accepts one connection at a time, announces an SSH-2.0 banner, answers the
CRLF probe with a second line, then closes. Binds loopback only.
"""

import argparse
import socket


def serve(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(4)
        print(f"banner server on {host}:{port} — Ctrl+C to stop")
        while True:
            conn, addr = server.accept()
            with conn:
                conn.settimeout(2.0)
                conn.sendall(b"SSH-2.0-OpenSSH_9.6 demo\r\n")
                try:
                    conn.recv(64)
                except (socket.timeout, OSError):
                    pass
                print(f"  served {addr[0]}:{addr[1]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=2222)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
