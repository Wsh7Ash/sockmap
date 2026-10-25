#!/usr/bin/env python3
"""sockmap — map open ports on your own machine to likely services."""

from __future__ import annotations

import json
import sys

import click
from rich.console import Console
from rich.table import Table

from .mapper import DEFAULT_PORTS, check_host, parse_ports, scan

console = Console()


@click.group()
@click.version_option()
def main():
    """Probe loopback ports and identify the services listening on them."""


@main.command("scan-ports")
@click.option("--ports", default=",".join(str(p) for p in DEFAULT_PORTS),
              show_default=True,
              help="Ports to probe: '22,80,443' or '8000-8010' or a mix.")
@click.option("--host", default="127.0.0.1", show_default=True,
              help="Loopback host (other hosts are refused).")
@click.option("--timeout", default=0.3, show_default=True, type=float,
              help="Per-port connect timeout in seconds.")
@click.option("--no-banner", is_flag=True, help="Skip banner grabbing.")
@click.option("--require", default=None,
              help="Comma-separated ports that must be open (exit 1 if any "
                   "are closed) — useful as a local health check.")
@click.option("--json-out", is_flag=True, help="Print the result as JSON.")
def scan_ports(ports, host, timeout, no_banner, require, json_out):
    """Probe PORTS on loopback and print the open ones."""
    try:
        port_list = parse_ports(ports)
        check_host(host)
        required = parse_ports(require) if require else []
    except ValueError as exc:
        console.print(f"[red]error:[/red] {exc}")
        sys.exit(2)

    results = scan(port_list, host=host, timeout=timeout, grab=not no_banner)
    open_ports = [r["port"] for r in results]
    missing = [p for p in required if p not in open_ports]

    if json_out:
        click.echo(json.dumps({
            "host": host,
            "probed": len(port_list),
            "open": results,
            "missing_required": missing,
        }, indent=2))
    else:
        if not results:
            console.print(f"no open ports among {len(port_list)} probed on {host}")
        else:
            table = Table(title=f"Open ports on {host}")
            for col in ("Port", "Service", "Banner"):
                table.add_column(col)
            for r in results:
                table.add_row(str(r["port"]), r["service"],
                              (r["banner"] or "")[:60])
            console.print(table)
        closed = len(port_list) - len(results)
        console.print(f"{len(results)} open, {closed} closed/filtered "
                      f"of {len(port_list)} probed")

    if missing:
        if not json_out:
            console.print(f"[red]missing required port(s): "
                          f"{', '.join(str(p) for p in missing)}[/red]")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
