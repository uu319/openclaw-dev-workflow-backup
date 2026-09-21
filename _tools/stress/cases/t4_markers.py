#!/usr/bin/env python3
"""Tier 4 - marker resolution must agree across tools.

A feature's tickets live in a marker file beside its spec. There are two valid
names - `.tracker.json` going forward, `.clickup.json` from before the rename -
and two places to look, the live specs dir and `specs/_done/`.

Two separate implementations resolve that, and they are not near each other:
`delivery_watch.markers()` decides which tickets a merged PR moves, and
`tracker_status.marker_for()` decides which tickets VanPM claims and sets. They
once disagreed - one checked both locations of a single suffix before trying the
other - so with a stale marker in `_done/` the watcher and VanPM could act on
different ticket ids for the same spec. That is silent: both tools report
success, against different tickets.

The order both must keep: live before archived, `.tracker.json` before
`.clickup.json`.
"""
import contextlib
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness  # noqa: E402
from harness import eq  # noqa: E402

dw = harness.load("dw_markers", os.path.join(harness.TOOLS, "delivery_watch.py"))
ts = harness.load("ts_markers", os.path.join(
    harness.WS, "project-manager/skills/feature-breakdown/scripts/tracker_status.py"))

TITLE = "marker resolution: the watcher and VanPM must pick the same file"

SLUG = "password-reset"


class _Ctx:
    """Only what markers() reads."""

    def __init__(self, specs):
        self.specs = specs


def _tree(*present):
    """Build a specs dir containing exactly the named marker variants.

    Each marker records where it came from, so a disagreement shows up as two
    different ticket ids rather than two paths that need eyeballing.
    """
    root = harness._mkdtemp("stress-mark-")
    specs = os.path.join(root, "specs")
    os.makedirs(os.path.join(specs, "_done"), exist_ok=True)
    open(os.path.join(specs, f"{SLUG}.md"), "w").write("# spec\n")
    for where in present:
        d = specs if where.startswith("live") else os.path.join(specs, "_done")
        sfx = ".tracker.json" if where.endswith("tracker") else ".clickup.json"
        json.dump({"[Feature] thing": {"id": f"TICKET-FROM-{where}"}},
                  open(os.path.join(d, SLUG + sfx), "w"))
    return specs


def _both(specs):
    """(watcher's ticket id, VanPM's ticket id) for the same spec."""
    marks = dw.markers(_Ctx(specs))
    _, watcher_marker = marks[SLUG]
    watcher_id = next(v["id"] for k, v in watcher_marker.items() if not k.startswith("_"))

    # marker_for warns on stderr when several markers exist, which is correct and
    # expected here - every combination below has more than one on purpose.
    with contextlib.redirect_stderr(io.StringIO()):
        path = ts.marker_for(os.path.join(specs, f"{SLUG}.md"))
    vanpm_id = next(v["id"] for k, v in json.load(open(path)).items()
                    if not k.startswith("_"))
    return watcher_id, vanpm_id


def every_marker_combination_resolves_the_same_way():
    """All 15 non-empty combinations of the four possible marker files."""
    variants = ["live-tracker", "live-clickup", "done-tracker", "done-clickup"]
    checked = 0
    for mask in range(1, 16):
        present = [v for i, v in enumerate(variants) if mask & (1 << i)]
        specs = _tree(*present)
        w, p = _both(specs)
        if w != p:
            raise AssertionError(
                f"with markers {present}: the watcher resolved {w} but VanPM resolved {p}. "
                "They would move and set different tickets for the same spec, both "
                "reporting success.")
        checked += 1
    eq(checked, 15, "every combination must have been exercised")


def the_live_tracker_marker_wins_over_every_other():
    """The documented order, pinned: live before archived, tracker before clickup."""
    for present, expected in (
        (["live-tracker", "live-clickup", "done-tracker", "done-clickup"], "live-tracker"),
        (["live-clickup", "done-tracker", "done-clickup"], "live-clickup"),
        (["done-tracker", "done-clickup"], "done-tracker"),
        (["done-clickup"], "done-clickup"),
    ):
        w, p = _both(_tree(*present))
        eq(w, f"TICKET-FROM-{expected}", f"watcher order wrong for {present}")
        eq(p, f"TICKET-FROM-{expected}", f"VanPM order wrong for {present}")


# --- daily lint ownership ---------------------------------------------------

def a_broken_project_cannot_capture_the_daily_lint():
    """The global lint is reported by ONE project, and that choice used to be
    `sorted(projects)[0]` - by name alone.

    `Ctx()` dies on a context with errors, so a half-onboarded project sorting
    first took the lint and then died before running it. Every other project
    skipped it because it was not first, so the daily lint stopped for everyone
    with nothing printed. Adding a project is precisely when a half-written
    context exists, which is precisely when the lint matters most.
    """
    import validate_context  # noqa: F401  (ensures TOOLS is importable)

    root = harness._mkdtemp("stress-lint-")
    os.makedirs(os.path.join(root, "projects"), exist_ok=True)
    for rel in ("projects/_tools", "_tools", "project-manager"):
        src, dstp = os.path.join(harness.WS, rel), os.path.join(root, rel)
        if os.path.exists(src) and not os.path.exists(dstp):
            os.makedirs(os.path.dirname(dstp), exist_ok=True)
            os.symlink(src, dstp)

    def project(slug, valid):
        d = os.path.join(root, "projects", slug)
        os.makedirs(d, exist_ok=True)
        body = (harness.BASE.replace("`harness`", f"`{slug}`")
                .replace("`tracker-harness`", f"`tracker-{slug}`"))
        if not valid:                      # half-onboarded: the slug line never filled in
            body = body.replace(f"- **Slug:** `{slug}`", "- **Slug:** `<slug>`")
        open(os.path.join(d, "PROJECT_CONTEXT.md"), "w").write(body)

    project("aaa-half-onboarded", valid=False)
    project("zzz-real-project", valid=True)

    real_ws, dw.WORKSPACE = dw.WORKSPACE, root
    try:
        owner = dw.lint_owner(["aaa-half-onboarded", "zzz-real-project"])
    finally:
        dw.WORKSPACE = real_ws

    eq(owner, "zzz-real-project",
       "a project whose context does not validate must not own the daily lint: it "
       "dies in Ctx() before running it, and the lint stops for every project")


def the_first_valid_project_owns_the_lint():
    """Still exactly one owner, and still the first - among those that work."""
    root = harness._mkdtemp("stress-lint-")
    os.makedirs(os.path.join(root, "projects"), exist_ok=True)
    for slug in ("aaa-one", "bbb-two"):
        d = os.path.join(root, "projects", slug)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "PROJECT_CONTEXT.md"), "w").write(
            harness.BASE.replace("`harness`", f"`{slug}`")
            .replace("`tracker-harness`", f"`tracker-{slug}`"))
    real_ws, dw.WORKSPACE = dw.WORKSPACE, root
    try:
        eq(dw.lint_owner(["aaa-one", "bbb-two"]), "aaa-one",
           "with both valid, the first by name still owns it")
        eq(dw.lint_owner([]), None, "no projects means no lint owner, not a crash")
    finally:
        dw.WORKSPACE = real_ws


def the_lint_block_actually_calls_lint_owner():
    """Pins the WIRING, not just the helper.

    Caught the hard way: reverting the call site to `projects[0]` left both cases
    above green, because they call lint_owner() directly. A correct helper that
    nothing calls is worth nothing, and source inspection is the cheap way to say
    so without standing up a full multi-project heartbeat.
    """
    import inspect
    src = inspect.getsource(dw.main)
    if "lint_owner(" not in src:
        raise AssertionError("the daily-lint block must choose its owner via lint_owner()")
    if "projects[0]" in src:
        raise AssertionError(
            "the daily-lint block still selects `projects[0]` by name: a project "
            "whose context does not validate would capture the lint and then die")


CASES = [
    ("broken project cannot own the lint", a_broken_project_cannot_capture_the_daily_lint),
    ("lint block is wired to lint_owner", the_lint_block_actually_calls_lint_owner),
    ("first valid project owns the lint", the_first_valid_project_owns_the_lint),
    ("all 15 marker combinations agree", every_marker_combination_resolves_the_same_way),
    ("live .tracker.json wins", the_live_tracker_marker_wins_over_every_other),
]
