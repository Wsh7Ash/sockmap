# Usage — sockmap

## Install

```shell
pip install -e .
```

## Commands

```shell
sockmap --help
```

## Examples

### Probe common ports

```shell
sockmap scan-ports --ports 22,80,443,5432
```

### Range with a health check

```shell
sockmap scan-ports --ports 8000-8010 --require 8000
```

### JSON for a script

```shell
sockmap scan-ports --ports 5432,6379 --json-out | jq ".open[].service"
```

### Connectivity only

```shell
sockmap scan-ports --ports 1-100 --no-banner --timeout 0.1
```

## Port spec grammar

- list: `22,80,443`
- range: `8000-8010` (max 4096 ports per range)
- mix: `22,8000-8010,443` (duplicates removed, input order preserved)
- anything else — `banana`, `0`, `70000`, `5-3` — is a usage error (exit 2)

Service detection prefers the banner (`SSH-2.0`, `HTTP/`, `220 ... SMTP`, `+OK`,
`-ERR`, engine greetings) and falls back to the well-known port table, then
`unknown`. `--require` turns the tool into a health check: exit 1 when a named
port is closed.

## Validation gates

- **install**: `pip install -e . (fresh venv)`
- **unit tests**: `pytest -q (13 tests, includes a live banner listener)`
- **CLI smoke**: `sockmap --help; sockmap scan-ports --ports 8080`
- **demo run**: `logs/2026-10-25/run_demos.py -> results/demo-output.txt`
- **secret scan**: `no tokens/keys/.env/machine paths in tree`

## Exit codes

- `0` — success / nothing at or above the threshold
- `1` — findings, failures, or an unmet `--require`
- `2` — usage error, unreadable input, or rejected target
