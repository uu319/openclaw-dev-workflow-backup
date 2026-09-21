#!/usr/bin/env python3
"""Tier 6 - soak and resource limits.

Two questions, measured rather than assumed:

1. Do the framework tools leak anything when run over and over? Memory, file
   descriptors, temp files, stale locks. Every tool writes temp files and takes
   flocks, and `/tmp` here is a 1 GB RAM disk - a full one presents as "out of
   memory", never "out of disk", which is the shape of the incident this box
   already had.
2. How fast does main's session DB actually grow? It is ~918 MB. The guide calls
   150 MB pathological, and the degenerate-loop incident happened on an
   oversized session, so the growth rate is the number that matters.

Nothing here touches the live projects/ tree: the tool iterations run against
OPENCLAW_WORKSPACE sandboxes, and everything else is read-only sampling.

  soak.py --minutes 45 [--interval 30] [--out report.json]

Standard library only.
"""
import argparse
import json
import os
import resource
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
MAIN_DB = os.path.join(HOME, ".openclaw/agents/main/agent/openclaw-agent.sqlite")


def _kb(path):
    try:
        return os.path.getsize(path) // 1024
    except OSError:
        return 0


def sample():
    """One point in time. All reads, no writes."""
    s = {"t": time.time()}

    mem = {}
    with open("/proc/meminfo") as f:
        for line in f:
            k, _, v = line.partition(":")
            mem[k] = int(v.split()[0])          # kB
    s["mem_available_kb"] = mem.get("MemAvailable", 0)
    s["swap_used_kb"] = mem.get("SwapTotal", 0) - mem.get("SwapFree", 0)

    tmp = shutil.disk_usage("/tmp")
    s["tmp_used_kb"] = (tmp.total - tmp.free) // 1024
    s["tmp_total_kb"] = tmp.total // 1024

    s["main_db_kb"] = _kb(MAIN_DB)
    s["main_wal_kb"] = _kb(MAIN_DB + "-wal")

    # Stale temp files from our own tools: each is a crash that left a file behind.
    s["stress_tmp_dirs"] = len([d for d in os.listdir("/tmp")
                                if d.startswith(("stress-ctx-", "stress-ws-"))])

    # Our own high-water mark, as a leak check on the soak process itself.
    s["soak_rss_kb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return s


def iteration(env):
    """One pass of the offline suite. Returns (ok, seconds, summary line)."""
    t0 = time.time()
    p = subprocess.run([sys.executable, os.path.join(HERE, "run.py")],
                       capture_output=True, text=True, env=env, timeout=900)
    dt = time.time() - t0
    last = [l for l in p.stdout.strip().splitlines() if l.strip()]
    return p.returncode == 0, dt, (last[-1] if last else "no output")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=45)
    ap.add_argument("--interval", type=float, default=30, help="seconds between samples")
    ap.add_argument("--out", default=os.path.join(HERE, "soak-report.json"))
    a = ap.parse_args()

    env = dict(os.environ)
    env.setdefault("TMPDIR", "/tmp")            # a shell has no gateway drop-in

    deadline = time.time() + a.minutes * 60
    samples, runs, failures = [sample()], [], []
    print(f"soak: {a.minutes:g} min, sampling every {a.interval:g}s", flush=True)
    print(f"  start: {samples[0]['mem_available_kb']//1024} MB avail, "
          f"/tmp {samples[0]['tmp_used_kb']//1024} MB, "
          f"main db {samples[0]['main_db_kb']//1024} MB", flush=True)

    n = 0
    while time.time() < deadline:
        n += 1
        ok, dt, line = iteration(env)
        runs.append({"n": n, "ok": ok, "seconds": round(dt, 1), "line": line})
        if not ok:
            failures.append({"n": n, "line": line})
            print(f"  [{n}] FAILED after {dt:.0f}s: {line}", flush=True)
        s = sample()
        samples.append(s)
        print(f"  [{n}] {dt:5.1f}s  {line[:34]:34}  "
              f"avail {s['mem_available_kb']//1024:5} MB  "
              f"/tmp {s['tmp_used_kb']//1024:4} MB  "
              f"db {s['main_db_kb']//1024:5} MB(+{s['main_wal_kb']//1024} wal)  "
              f"strays {s['stress_tmp_dirs']}", flush=True)
        left = deadline - time.time()
        if left > 0:
            time.sleep(min(a.interval, left))

    first, last = samples[0], samples[-1]
    span_min = (last["t"] - first["t"]) / 60 or 1
    delta = {k: last[k] - first[k] for k in
             ("mem_available_kb", "tmp_used_kb", "main_db_kb", "main_wal_kb",
              "swap_used_kb", "stress_tmp_dirs")}
    report = {"minutes": round(span_min, 1), "iterations": n,
              "failures": failures, "delta_kb": delta,
              "db_growth_mb_per_hour": round(delta["main_db_kb"] / 1024 / (span_min / 60), 1),
              "tmp_peak_kb": max(s["tmp_used_kb"] for s in samples),
              "tmp_total_kb": last["tmp_total_kb"],
              "mem_low_kb": min(s["mem_available_kb"] for s in samples),
              "samples": samples, "runs": runs}
    json.dump(report, open(a.out, "w"), indent=1)

    print(f"\n{n} iterations over {span_min:.0f} min, {len(failures)} failed")
    print(f"  memory available : {first['mem_available_kb']//1024} -> "
          f"{last['mem_available_kb']//1024} MB (low {report['mem_low_kb']//1024} MB)")
    print(f"  /tmp RAM disk    : {first['tmp_used_kb']//1024} -> {last['tmp_used_kb']//1024} MB "
          f"(peak {report['tmp_peak_kb']//1024} of {report['tmp_total_kb']//1024} MB)")
    print(f"  main session db  : {first['main_db_kb']//1024} -> {last['main_db_kb']//1024} MB "
          f"= {report['db_growth_mb_per_hour']} MB/hour")
    print(f"  stray temp dirs  : {delta['stress_tmp_dirs']:+d}")
    print(f"  report: {a.out}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
