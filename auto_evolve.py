#!/usr/bin/env python3
"""Auto-evolution loop: evaluate -> reflect -> mutate with fresh signals injected periodically."""
import os
import re
import sys
import random
import subprocess
from datetime import datetime

CYCLES = int(sys.argv[1]) if len(sys.argv) > 1 else 25
POP_DIR = "population"

SIGNAL_POOLS = [
    # CI/CD Depth
    [
        ('if "build matrix" in content or "matrix" in content:\n    score += 2', "CI/CD matrix builds"),
        ('if "cache" in content and ("pip" in content or "npm" in content or "apt" in content):\n    score += 2', "Dependency caching"),
        ('if "artifact" in content and ("upload" in content or "download" in content):\n    score += 2', "Build artifacts"),
        ('if "semantic release" in content or "semantic-release" in content:\n    score += 2', "Semantic release"),
        ('if "conventional commit" in content:\n    score += 2', "Conventional commits"),
    ],
    # Container & Security
    [
        ('if "non-root" in content or "nonroot" in content:\n    score += 2', "Non-root container"),
        ('if "readonly" in content and ("rootfs" in content or "filesystem" in content):\n    score += 2', "Read-only filesystem"),
        ('if "securitycontext" in content or "security context" in content:\n    score += 2', "K8s security context"),
        ('if "seccomp" in content or "apparmor" in content:\n    score += 2', "Seccomp/AppArmor"),
        ('if "pod security" in content or "psp" in content or "psa" in content:\n    score += 2', "Pod security"),
    ],
    # Database & Storage
    [
        ('if "index" in content and ("database" in content or "sql" in content or "query" in content):\n    score += 2', "DB indexing"),
        ('if "connection string" in content or "dsn" in content:\n    score += 2', "Connection strings"),
        ('if "pool" in content and ("size" in content or "max" in content or "min" in content):\n    score += 2', "Pool sizing"),
        ('if "read replica" in content or "replica" in content:\n    score += 2', "DB replicas"),
        ('if "sharding" in content or "shard" in content:\n    score += 2', "DB sharding"),
    ],
    # Testing & Quality
    [
        ('if "parametrize" in content or "parameterize" in content:\n    score += 2', "Parameterized tests"),
        ('if "conftest" in content:\n    score += 2', "conftest.py"),
        ('if "mark" in content and ("integration" in content or "slow" in content or "unit" in content):\n    score += 2', "Pytest markers"),
        ('if "golden" in content and ("file" in content or "test" in content):\n    score += 2', "Golden file tests"),
        ('if "approval" in content or "approvaltest" in content:\n    score += 2', "Approval tests"),
    ],
    # API & Web
    [
        ('if "pagination" in content:\n    score += 2', "API pagination"),
        ('if "rate limit" in content and ("header" in content or "retry-after" in content):\n    score += 2', "Rate limit headers"),
        ('if "refresh token" in content or "token refresh" in content:\n    score += 2', "Token refresh"),
        ('if "hsts" in content or "strict-transport" in content:\n    score += 2', "HSTS headers"),
        ('if "content-type" in content or "content type" in content:\n    score += 2', "Content type handling"),
    ],
    # Observability
    [
        ('if "healthz" in content or "readyz" in content or "livez" in content:\n    score += 2', "Health check endpoints"),
        ('if "debug" in content and ("endpoint" in content or "mode" in content or "profile" in content):\n    score += 2', "Debug endpoints"),
        ('if "pprof" in content:\n    score += 2', "pprof profiling"),
        ('if "audit" in content and ("log" in content or "trail" in content):\n    score += 2', "Audit logging"),
        ('if "correlation" in content and ("id" in content or "header" in content):\n    score += 2', "Correlation IDs"),
    ],
    # Python & Async
    [
        ('if "asyncio.queue" in content or "asyncio.Queue" in content:\n    score += 2', "Async queues"),
        ('if "asyncio.semaphore" in content or "asyncio.Semaphore" in content:\n    score += 2', "Async semaphores"),
        ('if "asyncio.lock" in content or "asyncio.Lock" in content:\n    score += 2', "Async locks"),
        ('if "entry_point" in content or "console_script" in content:\n    score += 2', "Entry points"),
        ('if "extras" in content and ("require" in content or "depend" in content):\n    score += 2', "Package extras"),
    ],
    # Architecture & Docs
    [
        ('if "adr" in content or "architecture decision" in content:\n    score += 2', "Architecture decision records"),
        ('if "c4" in content and ("model" in content or "diagram" in content):\n    score += 2', "C4 model diagrams"),
        ('if "sequence diagram" in content or "plantuml" in content or "mermaid" in content:\n    score += 2', "Sequence diagrams"),
        ('if "contributing" in content or "contributing.md" in content:\n    score += 2', "Contributing guide"),
        ('if "code of conduct" in content or "conduct.md" in content:\n    score += 2', "Code of conduct"),
    ],
    # Performance
    [
        ('if "connection pool" in content and ("size" in content or "max" in content or "limit" in content):\n    score += 2', "Pool size config"),
        ('if "idle" in content and ("timeout" in content or "connection" in content):\n    score += 2', "Idle timeout"),
        ('if "keepalive" in content or "keep alive" in content:\n    score += 2', "Keep alive"),
        ('if "compression" in content or "gzip" in content or "deflate" in content:\n    score += 2', "Compression"),
        ('if "brotli" in content or "zstd" in content:\n    score += 2', "Modern compression"),
    ],
    # Networking
    [
        ('if "dns" in content and ("resolve" in content or "lookup" in content):\n    score += 2', "DNS resolution"),
        ('if "proxy" in content and ("http" in content or "https" in content):\n    score += 2', "Proxy support"),
        ('if "retry" in content and ("backoff" in content or "jitter" in content or "exponential" in content):\n    score += 2', "Retry backoff"),
        ('if "circuit breaker" in content and ("threshold" in content or "half-open" in content or "reset" in content):\n    score += 2', "Circuit breaker detail"),
        ('if "bulkhead" in content or "bulk head" in content:\n    score += 2', "Bulkhead pattern"),
    ],
]


def inject_new_signals(count=8):
    """Inject new scoring signals into evaluate.py to raise the ceiling."""
    with open("evaluate.py") as f:
        content = f.read()

    # Find the insertion point (before 'scores[f] = round(min(500.0, score), 1)')
    insert_marker = "scores[f] = round(min(1000.0, score), 1)"
    if insert_marker not in content:
        print("WARN: could not find insertion point in evaluate.py")
        return 0

    # Pick random signals from pools
    flat_pool = []
    for pool in SIGNAL_POOLS:
        flat_pool.extend(pool)

    # Filter out signals already present
    available = [(code, desc) for code, desc in flat_pool
                  if code.split('"')[1] not in content.lower()]

    if not available:
        print("WARN: no new signals available to inject")
        return 0

    to_inject = random.sample(available, min(count, len(available)))
    injected = []
    for code, desc in to_inject:
        # Build the full code block with proper indentation
        lines = code.split("\n")
        indented = "\n".join("            " + l if l.strip() else l for l in lines)
        block = f"\n{indented}"
        new_content = content.replace(insert_marker, block + "\n            " + insert_marker)
        if new_content != content:
            injected.append(desc)
            content = new_content

    with open("evaluate.py", "w") as f:
        f.write(content)

    print(f"Injected {len(injected)} new signals: {', '.join(injected)}")
    return len(injected)


def main():
    cycles_run = 0
    injection_interval = max(3, CYCLES // 8)

    for cycle in range(1, CYCLES + 1):
        print(f"\n{'='*60}")
        print(f"CYCLE {cycle}/{CYCLES}")
        print(f"{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting...")

        # Step 1: Inject fresh signals every N cycles
        if cycle % injection_interval == 0:
            inject_new_signals(6)

        # Step 2: Evaluate
        print("\n--- Evaluating ---")
        result = subprocess.run(
            [sys.executable, "evaluate.py"],
            capture_output=True, text=True, timeout=120
        )
        # Parse last line for champion
        lines = result.stdout.strip().split("\n")
        for line in lines:
            print(line)
        if result.stderr:
            print("STDERR:", result.stderr[:200])

        # Step 3: Reflect
        print("\n--- Reflecting ---")
        result = subprocess.run(
            [sys.executable, "reflect.py"],
            capture_output=True, text=True, timeout=30
        )
        if result.stdout.strip():
            print(result.stdout.strip()[:200])
        if result.stderr:
            print("STDERR:", result.stderr[:200])

        # Step 4: Mutate
        print("\n--- Mutating ---")
        result = subprocess.run(
            [sys.executable, "mutate.py"],
            capture_output=True, text=True, timeout=30
        )
        print(result.stdout.strip())
        if result.stderr:
            print("STDERR:", result.stderr[:200])

        cycles_run += 1
        pop_count = len([f for f in os.listdir(POP_DIR) if f.endswith(".txt")])
        print(f"\n  -> Population: {pop_count} prompts, Cycle {cycle} complete")

    # Final evaluation
    print(f"\n{'='*60}")
    print(f"FINAL EVALUATION after {cycles_run} cycles")
    print(f"{'='*60}")
    result = subprocess.run(
        [sys.executable, "evaluate.py"],
        capture_output=True, text=True, timeout=120
    )
    print(result.stdout)

    # Read best score
    best_score = 0
    best_file = ""
    with open("results.log") as f:
        first = f.readline()
        if ":" in first:
            best_file, best_score_str = first.split(":")
            best_score = float(best_score_str.strip())

    print(f"\nCHAMPION: {best_file} ({best_score})")
    pop_count = len([f for f in os.listdir(POP_DIR) if f.endswith(".txt")])
    print(f"Final population: {pop_count} prompts across {cycles_run} generations")
    return best_score


if __name__ == "__main__":
    main()
