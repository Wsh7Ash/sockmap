import socket

KNOWN = {22: 'ssh', 80: 'http', 443: 'https', 3306: 'mysql', 5432: 'postgres',
         6379: 'redis', 8080: 'http-alt', 8787: 'alt-ports', 27017: 'mongodb'}

def probe_port(port, host='127.0.0.1', timeout=0.3):
    if host not in ('127.0.0.1', 'localhost'):
        raise ValueError('sockmap only probes localhost')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
        except (ConnectionRefusedError, TimeoutError, OSError):
            return None
        banner = ''
        try:
            s.send(b'\r\n')
            banner = s.recv(64).decode('utf-8', errors='replace').strip()
        except OSError:
            pass
        return {'port': port, 'service': KNOWN.get(port, 'unknown'), 'banner': banner}

def scan(ports, host='127.0.0.1'):
    out = []
    for p in ports:
        res = probe_port(p, host)
        if res:
            out.append(res)
    return out
