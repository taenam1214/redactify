"""Benchmark end-to-end engine scan/redact by file size."""

import tempfile
import time
from pathlib import Path

from benchmarks.bench_detectors import generate_corpus


def bench_file_size(size_label: str, n_lines: int) -> None:
    """Benchmark scan and redact for a given corpus size."""
    from redactify.core.engine import RedactionEngine

    corpus = generate_corpus(n_lines)
    tmp = Path(tempfile.mktemp(suffix=".txt"))
    tmp.write_text(corpus, encoding="utf-8")
    file_size = tmp.stat().st_size

    engine = RedactionEngine(use_ner=False)

    # Benchmark scan
    start = time.perf_counter()
    report = engine.scan(tmp)
    scan_time = time.perf_counter() - start

    # Benchmark redact
    out = Path(tempfile.mktemp(suffix=".txt"))
    start = time.perf_counter()
    engine.redact(tmp, output_path=out)
    redact_time = time.perf_counter() - start

    print(
        f"  {size_label:10s}  {file_size:>10,} bytes  "
        f"scan: {scan_time:.3f}s  redact: {redact_time:.3f}s  "
        f"entities: {report.total_entities}"
    )
    tmp.unlink()
    out.unlink()


def main():
    print("Engine benchmarks (no NER):\n")
    sizes = [
        ("1 KB", 10),
        ("100 KB", 1_000),
        ("1 MB", 10_000),
        ("10 MB", 100_000),
    ]
    for label, n_lines in sizes:
        bench_file_size(label, n_lines)


if __name__ == "__main__":
    main()
