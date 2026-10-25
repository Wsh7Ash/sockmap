# PROJECT SPEC — sockmap

| Field | Value |
|---|---|
| Name | `sockmap` |
| Category | networking |
| Target user | Developers and admins checking what is listening locally |
| Problem | netstat shows an open port but not what is behind it, and checking a handful of ports by hand has no repeatable, scriptable form. |
| Solution | Probe a short list or range of loopback ports, grab a banner when offered, and map open ports to services — with a --require health-check mode and hard refusal of any non-loopback host. |
| Core workflow | name ports/ranges -> scan loopback -> read table -> assert required ports |
| Stack | Python >=3.10, click, rich |
| Test strategy | tests/test_mapper.py covers the port-spec grammar (lists, ranges, dedupe, malformed and oversized input), loopback refusal, banner prioritization, a live listener with an SSH banner, scan ordering, and CLI exit codes 0/1/2 in table and JSON modes. |
| Demo strategy | `logs/2026-10-25/run_demos.py` runs the real workflow and captures `results/demo-output.txt` with asserted exit codes |
| Safety | Connections are made only to 127.0.0.1/localhost/::1 — check_host() raises for anything else and no flag bypasses it. Banners are untrusted, length-capped and never executed. |
| Definition of done | install + pytest + CLI smoke + demo transcript + secret scan all pass; docs (README, ARCHITECTURE, USAGE, CHANGELOG, CONTRIBUTING, SECURITY) present; pushed with green CI |

## Must-have features

- Core workflow end to end: name ports/ranges -> scan loopback -> read table -> assert required ports
- Exit-code contract (0/1/2) usable from CI
- `--json-out` machine-readable output where a machine should read it

## Nice-to-have (deferred)

- See README Roadmap.
