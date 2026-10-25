"""Tests for sockmap: port parsing, loopback guard, live probes, CLI exits."""

import json
import socket
import threading

import pytest
from click.testing import CliRunner

from sockmap.cli import main
from sockmap.mapper import (
    check_host,
    guess_service,
    parse_ports,
    probe_port,
    scan,
)


def make_listener(banner: bytes = b"SSH-2.0-OpenSSH_9.0\r\n"):
    """Bind a loopback socket, serve `banner` once, return (server, port)."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]

    def serve():
        try:
            conn, _ = server.accept()
        except OSError:
            return
        try:
            if banner:
                conn.sendall(banner)
            conn.settimeout(1.0)
            try:
                conn.recv(64)
            except (socket.timeout, OSError):
                pass
        finally:
            conn.close()

    threading.Thread(target=serve, daemon=True).start()
    return server, port


# ------------------------------------------------------------ port parsing

def test_parse_ports_list_range_and_mix():
    assert parse_ports("22,80,443") == [22, 80, 443]
    assert parse_ports("8000-8002") == [8000, 8001, 8002]
    assert parse_ports(" 22 , 20-22, 21 ") == [22, 20, 21]  # deduped, ordered


def test_parse_ports_rejects_bad_input():
    for bad in ("", "   ", "abc", "0", "70000", "5-3", "1-99999", "22-"):
        with pytest.raises(ValueError):
            parse_ports(bad)


def test_parse_ports_rejects_huge_range():
    with pytest.raises(ValueError):
        parse_ports("1-5000")


# ----------------------------------------------------------- loopback guard

def test_check_host_allows_loopback_only():
    assert check_host("127.0.0.1") == "127.0.0.1"
    assert check_host("localhost") == "localhost"
    with pytest.raises(ValueError):
        check_host("8.8.8.8")


def test_probe_refuses_remote_host():
    with pytest.raises(ValueError):
        probe_port(80, host="example.test")
    with pytest.raises(ValueError):
        scan([80], host="10.0.0.1")


# ------------------------------------------------------------ service guess

def test_guess_service_prefers_banner():
    assert guess_service(9999, "SSH-2.0-OpenSSH_9.0") == "ssh"
    assert guess_service(9999, "HTTP/1.1 200 OK") == "http"
    assert guess_service(3306, "") == "mysql"
    assert guess_service(9999, "") == "unknown"


# -------------------------------------------------------------- live probe

def test_probe_open_and_closed_ports():
    server, port = make_listener()
    try:
        result = probe_port(port)
        assert result is not None
        assert result["port"] == port
        assert result["service"] == "ssh"
        assert "OpenSSH" in result["banner"]
    finally:
        server.close()

    # assume nothing listens on port 1 (privileged/unused)
    assert probe_port(1, timeout=0.2) is None


def test_scan_returns_open_in_order():
    server, port = make_listener(banner=b"HTTP/1.1 404 Not Found\r\n\r\n")
    try:
        closed = [p for p in (1, 3) if p != port]
        results = scan(closed + [port], timeout=0.2)
    finally:
        server.close()
    assert [r["port"] for r in results] == [port]
    assert results[0]["service"] == "http"


# -------------------------------------------------------------------- CLI

def test_cli_scan_table():
    server, port = make_listener()
    try:
        res = CliRunner().invoke(main, ["scan-ports", "--ports", str(port)])
    finally:
        server.close()
    assert res.exit_code == 0, res.output
    assert str(port) in res.output


def test_cli_json_out():
    server, port = make_listener()
    try:
        res = CliRunner().invoke(main, ["scan-ports", "--ports", str(port),
                                        "--json-out", "--require", str(port)])
    finally:
        server.close()
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["probed"] == 1
    assert payload["open"][0]["port"] == port
    assert payload["missing_required"] == []


def test_cli_bad_spec_exits_2():
    res = CliRunner().invoke(main, ["scan-ports", "--ports", "banana"])
    assert res.exit_code == 2
    assert "error" in res.output


def test_cli_remote_host_exits_2():
    res = CliRunner().invoke(main, ["scan-ports", "--host", "8.8.8.8"])
    assert res.exit_code == 2
    assert "loopback" in res.output


def test_cli_require_missing_port_exits_1():
    res = CliRunner().invoke(main, ["scan-ports", "--ports", "1",
                                    "--require", "1", "--timeout", "0.2"])
    assert res.exit_code == 1, res.output
