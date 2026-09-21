#!/usr/bin/env python3
"""Tiny test harness for the stress suite. Standard library only.

A case is a function that raises AssertionError when the system misbehaves. The
point of every case is a SPECIFIC expected outcome - "does not crash" is not a
result, because the failures this suite exists to catch are the ones that do not
crash (a watcher that confidently reports the wrong thing).
"""
import contextlib
import importlib.util
import io
import os
import sys
import tempfile

WS = os.environ.get("OPENCLAW_WORKSPACE", "/home/openclaw/.openclaw/workspace")
TOOLS = os.path.join(WS, "projects/_tools")


def load(name, path):
    """Import a tool by path (they are scripts, not a package)."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# --- assertions that say what was expected ---------------------------------

def eq(actual, expected, what):
    if actual != expected:
        raise AssertionError(f"{what}\n   expected: {expected!r}\n   actual:   {actual!r}")


def contains(haystack, needle, what):
    hay = " ".join(haystack) if isinstance(haystack, (list, tuple)) else str(haystack)
    if needle.lower() not in hay.lower():
        raise AssertionError(f"{what}\n   expected to contain: {needle!r}\n   actual: {hay[:400]!r}")


def not_contains(haystack, needle, what):
    hay = " ".join(haystack) if isinstance(haystack, (list, tuple)) else str(haystack)
    if needle.lower() in hay.lower():
        raise AssertionError(f"{what}\n   expected NOT to contain: {needle!r}\n   actual: {hay[:400]!r}")


def raises(exc, fn, what):
    try:
        fn()
    except exc as e:
        return e
    except Exception as e:  # noqa: BLE001
        raise AssertionError(f"{what}\n   expected {exc.__name__}, got {type(e).__name__}: {e}")
    raise AssertionError(f"{what}\n   expected {exc.__name__}, nothing was raised")


@contextlib.contextmanager
def captured():
    """Capture stdout so a case can assert on what a tool printed."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        yield buf


# --- a valid PROJECT_CONTEXT to mutate --------------------------------------

BASE = """# Project Context: harness

## Identity
- **Slug:** `harness`
- **Display name:** Harness

## Repository
- **Git SSH Clone URL:** `git@github.com:acme/harness.git`
- **GitHub Repo:** `acme/harness`
- **Default branch:** `main`

## Stack
- **Layout:** single service
- **Runtime:** Python 3.12, pytest

## Tracker & Design
- **Tracker:** `clickup`
- **Tracker Board ID:** `1100770000001008`
- **Tracker MCP server:** `tracker-harness`
- **Figma file:** none
- **SecretRefs:**
  - Tracker: `CLICKUP_API_TOKEN_HARNESS`
  - GitHub Token: `GITHUB_TOKEN_HARNESS`

## Workflow Rules
- **Statuses:** `to do`, `in progress`, `qa`, `rejected`, `on hold`, `complete`, `cancelled`
- **Create status:** `to do`
- **Branch Prefixes:** `feature/`, `bug/`
- **Deploy checks:** `deploy-fe`, `deploy-be`

## Flow
- **Profile:** `factory`
- **Deploy signal:** `none`
- **Merge by:** `van`

## Artifact Routing
- **Code (CWD):** `/tmp/harness-code`
- **Internal Artifacts:** `/tmp/harness-artifacts/`
"""


def context(*edits, base=BASE):
    """Write a PROJECT_CONTEXT.md with (old, new) substitutions applied.

    A `new` of None deletes the line. Returns the path (in a temp dir that
    survives the run, so a failing case can be inspected).
    """
    s = base
    for old, new in edits:
        if old not in s:
            raise AssertionError(f"harness: base context has no {old!r} to replace")
        s = s.replace(old, "" if new is None else new)
    d = tempfile.mkdtemp(prefix="stress-ctx-")
    p = os.path.join(d, "PROJECT_CONTEXT.md")
    open(p, "w", encoding="utf-8").write(s)
    return p


def parsed(*edits, base=BASE):
    """-> (fields, errors) from the real validator."""
    vc = load("vc_stress", os.path.join(TOOLS, "validate_context.py"))
    return vc.parse(context(*edits, base=base))
