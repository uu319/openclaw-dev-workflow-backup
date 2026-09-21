#!/usr/bin/env python3
"""Stress-test runner for the development factory.

    python3 _tools/stress/run.py                 # every offline tier
    python3 _tools/stress/run.py --tier 1        # one tier
    python3 _tools/stress/run.py -k backtick     # cases matching a substring
    python3 _tools/stress/run.py --list

Tiers:
  1  offline unit - validator edges, adapters, watcher logic. No network.
  2  contract - adapters against local mock servers, including fault injection.
  3  live - real Jira / Linear / GitHub Actions. Needs credentials; opt in.
  4  state and concurrency.

Exit code is the number of failures, so it works as a gate.
Standard library only.
"""
import argparse
import importlib.util
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(HERE, "cases")


def modules(tier=None):
    out = []
    for f in sorted(os.listdir(CASES)):
        if not f.startswith("t") or not f.endswith(".py"):
            continue
        t = int(f[1])
        if tier and t != tier:
            continue
        spec = importlib.util.spec_from_file_location(f[:-3], os.path.join(CASES, f))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        out.append((t, f[:-3], m))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", type=int)
    ap.add_argument("-k", help="only cases whose name contains this")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()

    passed = failed = skipped = 0
    fails = []
    for tier, modname, m in modules(a.tier):
        cases = [(n, f) for n, f in getattr(m, "CASES", []) if not a.k or a.k.lower() in n.lower()]
        if not cases:
            continue
        print(f"\n\033[1mtier {tier} · {getattr(m, 'TITLE', modname)}\033[0m")
        for name, fn in cases:
            if a.list:
                print(f"  - {name}")
                continue
            t0 = time.time()
            try:
                fn()
            except NotImplementedError as e:
                skipped += 1
                print(f"  \033[33mSKIP\033[0m {name} ({e})")
                continue
            except AssertionError as e:
                failed += 1
                fails.append((name, str(e)))
                print(f"  \033[31mFAIL\033[0m {name}\n        {str(e).replace(chr(10), chr(10) + '        ')}")
                continue
            except Exception:  # noqa: BLE001 - an unexpected crash is a failure too
                failed += 1
                tb = traceback.format_exc().strip().splitlines()[-1]
                fails.append((name, tb))
                print(f"  \033[31mERROR\033[0m {name}\n        {tb}")
                continue
            passed += 1
            ms = (time.time() - t0) * 1000
            print(f"  \033[32mok\033[0m   {name}" + (f"  ({ms:.0f}ms)" if a.verbose or ms > 500 else ""))

    if a.list:
        return 0
    print(f"\n{passed} passed, {failed} failed, {skipped} skipped")
    if fails:
        print("\nfailures:")
        for n, e in fails:
            print(f"  - {n}: {e.splitlines()[0]}")
    return min(failed, 120)


if __name__ == "__main__":
    sys.exit(main())
