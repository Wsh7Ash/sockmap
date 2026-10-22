#!/usr/bin/env python3
import click
from rich.console import Console
from rich.table import Table
from .mapper import scan
console = Console()
@click.group()
@click.version_option()
def main(): pass
@main.command()
@click.option('--ports', default='22,80,443,3306,5432,6379,8080,27017')
def scan_ports(ports):
    plist = [int(p) for p in ports.split(',')]
    results = scan(plist)
    t = Table(title='Open local ports')
    t.add_column('Port'); t.add_column('Service'); t.add_column('Banner')
    for r in results: t.add_row(str(r['port']), r['service'], r['banner'][:40])
    console.print(t)
if __name__ == '__main__': main()
