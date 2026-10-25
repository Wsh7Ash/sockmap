# sockmap

**Find out what is actually listening on your own machine — map open loopback
ports to likely services using banners and well-known port tables.**

## The problem

`netstat` tells you a port is open; it does not tell you *what* opened it or
which of the eight ports you care about are even reachable. sockmap probes a
short list of ports on `127.0.0.1`, grabs a banner where one is offered, and
prints a table of what answered — refusing to look at any host other than
loopback.

## Features

- **Flexible port specs** — `22,80,443`, `8000-8010`, or a mix; duplicates
  removed, ranges capped at 4096 ports, malformed input rejected.
- **Banner-based identification** — a peer that speaks wins over the port
  table: an `SSH-2.0` banner on port 8793 is reported as `ssh` even though
  8793 is not in the table.
- **Loopback guard** — `check_host()` raises for anything that is not
  `127.0.0.1`, `localhost` or `::1`.
- **Health-check mode** — `--require 5432` exits `1` when a required port is
  closed, so the same command works in a script.
- **`--json-out`** for automation; `--no-banner` for a pure connectivity check.

Exit codes: `0` scan completed (and `--require` satisfied), `1` a required
port was closed, `2` bad spec or non-loopback host.

## Example output

Real output from `results/demo-output.txt` — port 8793 running
`examples/banner_server.py`, ports 1 and 22 closed:

```console
$ sockmap scan-ports --ports 8793,1,22 --timeout 0.3
Open ports on 127.0.0.1
┌──────┬─────────┬──────────────────────────┐
│ Port │ Service │ Banner                   │
├──────┼─────────┼──────────────────────────┤
│ 8793 │ ssh     │ SSH-2.0-OpenSSH_9.6 demo │
└──────┴─────────┴──────────────────────────┘
1 open, 2 closed/filtered of 3 probed
[exit 0]
```

## Architecture

```
src/sockmap/
├── mapper.py   # parse_ports(), check_host(), guess_service(), probe_port(), scan()
└── cli.py      # click: spec parsing, rendering, --require, exit codes
```

`guess_service()` prefers evidence from the banner and falls back to the
well-known port table, then `unknown`. `probe_port()` opens one TCP
connection, reads up to 256 bytes, and sends a single CRLF only if the peer
stays silent.

## Requirements

- Python 3.10+; `click` and `rich` (installed automatically)

## Installation

```shell
git clone https://github.com/Wsh7Ash/sockmap
cd sockmap
pip install -e .
```

## Quick start

```shell
# optional: a loopback listener with a fake SSH banner
python examples/banner_server.py --port 2222 &

sockmap scan-ports --ports 2222,22,80,443
```

## Usage

```shell
# a range with a required-port health check
sockmap scan-ports --ports 8000-8010 --require 8000

# JSON for a script
sockmap scan-ports --ports 5432,6379 --json-out | jq '.open[].service'

# connectivity only, no banner read
sockmap scan-ports --ports 1-100 --no-banner --timeout 0.1
```

## Configuration

| Option | Default | Purpose |
| --- | --- | --- |
| `--ports` | `22,80,443,3306,5432,6379,8080,27017` | ports/ranges to probe |
| `--host` | `127.0.0.1` | loopback host (others refused) |
| `--timeout` | `0.3` | per-port connect timeout (seconds) |
| `--no-banner` | off | skip banner grabbing |
| `--require` | none | ports that must be open (exit 1 otherwise) |

## Testing

```shell
pip install -e . pytest
pytest -q        # 13 tests, including a live listener with a real banner
```

## Project structure

```
sockmap/
├── src/sockmap/{mapper,cli}.py
├── tests/test_mapper.py
├── examples/banner_server.py
├── docs/{ARCHITECTURE,USAGE,PROJECT_SPEC}.md
├── results/demo-output.txt
├── RESULTS.md
└── .github/workflows/ci.yml
```

## Limitations

- Loopback only — by design. It will not scan your LAN or the internet.
- Ports are probed sequentially with a short timeout, so very large ranges
  take proportionally longer.
- Banner grabbing sends a single CRLF when the peer is silent; services that
  misbehave on an unexpected newline may drop the connection (the port is
  still reported as open).
- Service names are a best guess: a proxy on 8080 and an app on 8080 both
  report `http-proxy`.

## Roadmap

- `--profile` sending a protocol-specific probe (HTTP `OPTIONS`, TLS
  `ClientHello`) for better identification.
- Parallel probing with a bounded worker pool.
- Baseline file so `scan-ports` can report newly opened ports.

## Security

Only loopback connections are permitted — `check_host()` rejects any other
host, and there is no mode that bypasses it. Banner data is untrusted input
that is length-capped and never executed. See [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).
