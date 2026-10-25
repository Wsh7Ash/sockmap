# Architecture — sockmap

## Overview

`sockmap` (networking) is a single-package Python CLI: a `src/sockmap/` package
with a pure logic module and a Click command layer, console-script entry point
`sockmap = sockmap.cli:main`, and no runtime services.

### `src/sockmap/mapper.py`

parse_ports() (list/range/mix, dedupe, caps), check_host() (loopback only), guess_service() (banner evidence first, well-known table second), probe_port() (one TCP connect, read up to 256 bytes, CRLF only if silent) and scan() (in-order, open only).

### `src/sockmap/cli.py`

Click group with `scan-ports` (--ports, --host, --timeout, --no-banner, --require, --json-out). Exits 0 completed, 1 required port closed, 2 bad spec or non-loopback host.


## Design decisions

- **Logic/rendering separation.** Every decision (classify, parse, lint, plan,
  probe) lives in a pure module with no console output, so tests assert on data
  rather than on terminal formatting.
- **Exit codes as the CI contract.** 0 = clean/success, 1 = findings or failed
  requirement, 2 = usage or read error. `--json-out` switches stdout to
  machine-readable JSON without changing exit codes.
- **Small dependency surface.** Only `click` (CLI), `rich` (tables) and, where
  network I/O is the point, `requests`; everything else is the standard library.

## Data flow

```
input (file / URL / ports + flags)
   -> Click command validates arguments
   -> pure module computes findings / profiles / verdicts / plan
   -> renderer prints table or JSON
   -> process exits 0 / 1 / 2
```

## Testing strategy

tests/test_mapper.py covers the port-spec grammar (lists, ranges, dedupe, malformed and oversized input), loopback refusal, banner prioritization, a live listener with an SSH banner, scan ordering, and CLI exit codes 0/1/2 in table and JSON modes.
