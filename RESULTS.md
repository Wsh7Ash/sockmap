# Results — sockmap

## Environment
- OS: Windows (msys2 shell), Python 3.14.3
- Runtime: python.exe in a fresh virtualenv
- Dependency manager: pip (`pip install -e .`)

## Validation performed
- install: PASS (exit 0)
- unit tests: PASS (exit 0)
- CLI help: PASS (exit 0)
- CLI scan (closed ports only): PASS (exit 0)
- CLI bad spec (exit 2 expected): PASS (exit 2)
- demo run: PASS (47 lines captured in results/demo-output.txt)
- secret/path scan: PASS (no secrets, no machine-specific paths)

## Commands executed

```shell
-m pip install -q -e .
```
# -> install: exit 0
```shell
-m pytest -q
```
# -> unit tests: exit 0
```shell
sockmap --help
```
# -> CLI help: exit 0
```shell
sockmap scan-ports --ports 1,3 --timeout 0.2
```
# -> CLI scan (closed ports only): exit 0
```shell
sockmap scan-ports --ports banana
```
# -> CLI bad spec (exit 2 expected): exit 2

## Observed result

**install**

```

```

**unit tests**

```
.............                                                            [100%]
13 passed in 1.16s
```

**CLI help**

```
  --help     Show this message and exit.
Commands:
  scan-ports  Probe PORTS on loopback and print the open ones.
```

**CLI scan (closed ports only)**

```
no open ports among 2 probed on 127.0.0.1
0 open, 2 closed/filtered of 2 probed
```

**CLI bad spec (exit 2 expected)**

```
error: bad port 'banana'
```

## Generated artifacts

- `results/demo-output.txt` — full demo transcript with real exit codes
- `docs/ARCHITECTURE.md`, `docs/USAGE.md`, `docs/PROJECT_SPEC.md`
- `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `README.md`

## Known limitations

See the **Limitations** section of `README.md`. In short: single-process scope,
heuristic detection where noted, and advisory output that must be interpreted by
a human who knows the system under test.
