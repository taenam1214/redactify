# Privacy Guarantee

## How Redactify Protects Your Data

Redactify is designed with a single, uncompromising principle:

**Your data never leaves your machine.**

### What This Means

1. **No network calls** — Redactify makes zero HTTP requests during operation.
2. **No telemetry** — We don't collect usage data, crash reports, or analytics.
3. **No cloud processing** — All NLP/regex processing runs on your CPU.
4. **No temporary cloud storage** — Files are never uploaded anywhere.
5. **No external APIs** — We don't call OpenAI, AWS, or any external service.

### The Only Network Activity

The only time network access is used is during **initial setup**:

```bash
python -m spacy download en_core_web_sm
```

This downloads the spaCy language model (one-time). After that, Redactify works fully offline.

### Verification

You can verify this yourself:

1. Disconnect from the internet
2. Run `redactify redact document.txt`
3. It works perfectly

### Why This Matters

- **HIPAA compliance**: Patient data stays on your system
- **GDPR compliance**: No cross-border data transfer
- **Legal privilege**: Attorney-client privileged documents stay local
- **Corporate policy**: No data exfiltration risk

### Open Source Transparency

Every line of code is open source. Audit it yourself:

- No `requests`, `urllib`, or `httpx` in core dependencies
- No background threads phoning home
- No hidden endpoints

**Your privacy is not a feature. It's the foundation.**
