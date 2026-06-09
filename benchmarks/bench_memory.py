"""Benchmark peak memory usage for streaming vs non-streaming modes."""

import resource
import tempfile
import time
from pathlib import Path

from benchmarks.bench_detectors import generate_corpus


def get_peak_rss_mb() -> float:
    """Get peak resident set size in MB (macOS/Linux)."""
    usage = resource.getrusage(resource.RUSAGE_SELF)
    # macOS reports in bytes, Linux in KB
    import sys
    if sys.platform == "darwin":
        return usage.ru_maxrss / (1024 * 1024)
    return usage.ru_maxrss / 1024


def bench_memory(n_lines: int) -> None:
    """Compare memory usage between normal and streaming scan."""
    from redactify.core.engine import RedactionEngine

    corpus = generate_corpus(n_lines)
    tmp = Path(tempfile.mktemp(suffix=".txt"))
    tmp.write_text(corpus, encoding="utf-8")
    file_size = tmp.stat().st_size

    engine = RedactionEngine(use_ner=False)

    # Normal scan
    start = time.perf_counter()
    engine.scan(tmp)
    normal_time = time.perf_counter() - start
    normal_mem = get_peak_rss_mb()

    # Streaming scan
    start = time.perf_counter()
    engine.scan_streaming(tmp)
    stream_time = time.perf_counter() - start
    stream_mem = get_peak_rss_mb()

    print(
        f"  {file_size:>10,} bytes | "
        f"normal: {normal_time:.3f}s / {normal_mem:.1f}MB | "
        f"stream: {stream_time:.3f}s / {stream_mem:.1f}MB"
    )
    tmp.unlink()


def main():
    print("Memory benchmark (peak RSS):\n")
    for n_lines in [1_000, 10_000, 50_000]:
        bench_memory(n_lines)


if __name__ == "__main__":
    main()
