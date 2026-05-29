# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Redactify, please report it responsibly.

**Do NOT open a public issue for security vulnerabilities.**

Instead, please email: taenam1214 (via GitHub private message)

## What to Report

- Bugs that could cause PII to leak through redaction
- Issues where data might be transmitted externally
- Dependency vulnerabilities that affect Redactify

## Scope

Redactify is designed to run locally. The following are by design:

- The tool reads files from disk (this is its purpose)
- The tool writes redacted files to disk (this is its purpose)
- spaCy models are downloaded from the internet during setup (one-time)

## Response Timeline

- Acknowledgment within 48 hours
- Fix or mitigation within 7 days for critical issues
