"""Localhost port-to-service mapper.

Only ever connects to loopback (127.0.0.1/localhost); passing another host
raises ValueError. Banner grabbing is a single read (plus one CRLF probe when
the peer is silent) — there is no scanning of ranges beyond the ports you
name, and no spoofing or exploitation logic.
"""

from __future__ import annotations

import socket

SERVICE_BY_PORT = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    80: "http", 110: "pop3", 143: "imap", 389: "ldap", 443: "https",
    445: "smb", 465: "smtps", 587: "submission", 631: "ipp",
    993: "imaps", 995: "pop3s", 1433: "mssql", 2049: "nfs",
    3306: "mysql", 3389: "rdp", 5432: "postgres", 5900: "vnc",
    6379: "redis", 6443: "k8s-api", 8000: "http-alt", 8080: "http-proxy",
    8443: "https-alt", 8787: "alt-service", 9000: "http-alt",
    9200: "elasticsearch", 11211: "memcached", 27017: "mongodb",
}

DEFAULT_PORTS = (22, 80, 443, 3306, 5432, 6379, 8080, 27017)
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def parse_ports(spec: str) -> list[int]:
    """Parse a port spec: ``"22,80,443"`` or ``"8000-8010"`` or a mix.

    Duplicates are removed, order is preserved. Raises ValueError on
    malformed input or out-of-range ports.
    """
    if not spec or not spec.strip():
        raise ValueError("empty port spec")
    ports: list[int] = []
    seen: set[int] = set()
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            lo_s, _, hi_s = chunk.partition("-")
            try:
                lo, hi = int(lo_s), int(hi_s)
            except ValueError:
                raise ValueError(f"bad port range {chunk!r}") from None
            if lo > hi or lo < 1 or hi > 65535:
                raise ValueError(f"bad port range {chunk!r}")
            if hi - lo > 4096:
                raise ValueError(f"range {chunk!r} is too large (max 4096 ports)")
            values = range(lo, hi + 1)
        else:
            try:
                values = [int(chunk)]
            except ValueError:
                raise ValueError(f"bad port {chunk!r}") from None
            if not 1 <= values[0] <= 65535:
                raise ValueError(f"port {values[0]} out of range 1-65535")
        for port in values:
            if port not in seen:
                seen.add(port)
                ports.append(port)
    if not ports:
        raise ValueError(f"no ports parsed from {spec!r}")
    return ports


def check_host(host: str) -> str:
    """Refuse anything that is not loopback."""
    if host not in LOOPBACK_HOSTS:
        raise ValueError(f"sockmap only probes loopback, not {host!r}")
    return host


def guess_service(port: int, banner: str = "") -> str:
    """Service name: a speaking peer wins over the well-known port table."""
    head = banner[:64].upper()
    if head.startswith("SSH-"):
        return "ssh"
    if head.startswith("HTTP/"):
        return "http"
    if head.startswith("220 ") and "SMTP" in head:
        return "smtp"
    if head.startswith("+OK"):
        return "pop3"
    if head.startswith("-ERR"):
        return "redis"
    if "MONGODB" in head or "MONGO" in head:
        return "mongodb"
    if "MYSQL" in head:
        return "mysql"
    if "POSTGRES" in head:
        return "postgres"
    return SERVICE_BY_PORT.get(port, "unknown")


def _grab_banner(sock: socket.socket) -> str:
    """Read whatever the peer says; probe with CRLF only if it stays silent."""
    try:
        data = sock.recv(256)
        if data:
            return data.decode("utf-8", errors="replace").strip()
    except (socket.timeout, OSError):
        return ""
    try:
        sock.sendall(b"\r\n")
        data = sock.recv(256)
        if data:
            return data.decode("utf-8", errors="replace").strip()
    except (socket.timeout, OSError):
        pass
    return ""


def probe_port(port: int, host: str = "127.0.0.1", timeout: float = 0.3,
               grab: bool = True) -> dict | None:
    """Connect to one local port; None when closed/filtered."""
    check_host(host)
    if not 1 <= port <= 65535:
        raise ValueError(f"port {port} out of range 1-65535")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
        except (ConnectionRefusedError, TimeoutError, OSError):
            return None
        banner = _grab_banner(sock) if grab else ""
    return {"port": port, "service": guess_service(port, banner),
            "banner": banner}


def scan(ports: list[int], host: str = "127.0.0.1", timeout: float = 0.3,
         grab: bool = True) -> list[dict]:
    """Probe each port on loopback and return the open ones, in input order."""
    check_host(host)
    out = []
    for port in ports:
        res = probe_port(port, host=host, timeout=timeout, grab=grab)
        if res:
            out.append(res)
    return out
