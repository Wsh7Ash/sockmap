# Security Policy

## Supported versions

The latest release on `main` is supported; there are no versioned release
lines yet.

## Reporting a vulnerability

If you find a vulnerability or unsafe default in `sockmap` itself, please open a
private security advisory on the GitHub repository (or open an issue describing the
problem at a high level if you cannot use advisories). We will acknowledge within
72 hours and coordinate a fix before public disclosure.

## Intended use

Connections are made only to 127.0.0.1/localhost/::1 — check_host() raises for anything else and no flag bypasses it. Banners are untrusted, length-capped and never executed.

## Secrets

`sockmap` stores no credentials and requires none. Do not commit real tokens, cookies
or keys to the spec/example files in this repository; `.gitignore` excludes `.env`
and common key material.
