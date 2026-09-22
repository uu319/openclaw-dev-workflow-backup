#!/usr/bin/env python3
"""Tier 1 - the design-fidelity gate in tracker_push.validate().

Every fms-studio screen built before 2026-09-21 shipped with a text stand-in
where the logo belongs and a grey box where the hero collage belongs, because
the pipeline downloaded a screenshot OF each screen and never the artwork IN it.
Nothing in the spec, the push script or the review said that was wrong.

These cases pin the gate that says it now: an `[FE]` ticket needs an asset
manifest whose files really exist, and a `## Design fidelity` section that
names hex colours and the repo path of every asset.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness  # noqa: E402
from harness import contains, eq, not_contains  # noqa: E402

TITLE = "design fidelity: assets reach the repo, not a placeholder"

PUSH = os.path.join(harness.WS, "project-manager/skills/feature-breakdown/scripts/tracker_push.py")

BODY = """## Context
Parent: [Feature] Landing: marketing page · Lane: FE

## User story
As a visitor, I want to see the product, so that I can decide to sign up.

## In scope
- The marketing landing page layout

## Out of scope (do NOT build)
- Checkout, auth, analytics

## Acceptance criteria
- Given the page loads, when the header renders, then the wordmark image is shown at 154x26.
- Given the page loads, when the hero renders, then the collage image is shown.
- Given a viewport narrower than 640px, when the page renders, then the hero stacks to one column.

{fidelity}
## Technical notes
- Interface / schema: static page, no API.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Run the [QA] scenario.

## Definition of done
- [ ] All acceptance criteria pass
"""

FIDELITY = """## Design fidelity
- Tokens: Primary `#FF6100` · Text `#313131` · Font `Host Grotesk` 400/500
- Assets (from the manifest, copy into the repo at these paths):
  - `assets/logo.svg` -> `frontend/public/brand/logo.svg` - wordmark, 154x26
- No placeholders: every asset above is rendered by the code.

"""


def _push():
    return harness.load("tracker_push_stress", PUSH)


def _sandbox(manifest=None, assets_on_disk=(("logo.svg", "<svg/>"),), shot_bytes=b"\x89PNG\r\n"):
    """A spec dir with a screenshot, an assets folder and (optionally) a manifest."""
    d = harness._mkdtemp("stress-design-")
    feat = os.path.join(d, "specs", "_figma", "landing")
    assets = os.path.join(feat, "assets")
    os.makedirs(assets, exist_ok=True)
    open(os.path.join(feat, "9731-3297.png"), "wb").write(shot_bytes)
    for name, content in assets_on_disk:
        open(os.path.join(assets, name), "w", encoding="utf-8").write(content)
    if manifest is not None:
        json.dump(manifest, open(os.path.join(assets, "manifest.json"), "w", encoding="utf-8"))
    return d


def _ticket(**over):
    t = {
        "title": "[FE] Landing: marketing page",
        "lane": "FE",
        "parent": "[Feature] Landing: marketing page",
        "estimate_hours": "6",
        "figma": "https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/F?node-id=9731-3297",
        "screenshots": "specs/_figma/landing/9731-3297.png",
        "assets": "specs/_figma/landing/assets/manifest.json",
        "body": BODY.format(fidelity=FIDELITY),
    }
    t.update(over)
    return t


PARENT = {
    "title": "[Feature] Landing: marketing page",
    "lane": "FEATURE",
    "body": BODY.format(fidelity=""),
}

GOOD_MANIFEST = {"feature": "landing", "assets": [
    {"file": "assets/logo.svg", "node": "9734:3530", "kind": "svg",
     "name": "wordmark", "repo_path": "frontend/public/brand/logo.svg"}]}


def _errors(ticket, art):
    """validate() exits 2 and prints to stderr; return what it complained about."""
    import contextlib
    import io
    push = _push()
    ctx = {"artifacts_dir": os.path.realpath(art), "has_figma": True}
    buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(buf):
            push.validate([PARENT, ticket], ctx, spec_path=None)
    except SystemExit as e:
        eq(e.code, 2, "validate() rejects with exit 2")
    return buf.getvalue()


# --- the gate accepts a complete ticket -------------------------------------

def complete_fe_ticket_passes():
    """Manifest, real files, hex tokens, repo path echoed in the section: no complaint."""
    art = _sandbox(GOOD_MANIFEST)
    eq(_errors(_ticket(), art), "", "a complete [FE] ticket must pass the design gate")


def css_only_screen_passes_with_empty_manifest():
    """A screen with no artwork says so explicitly; silence is what caused the bug."""
    art = _sandbox({"feature": "landing", "assets": []}, assets_on_disk=())
    body = BODY.format(fidelity="## Design fidelity\n- Tokens: Primary `#FF6100`\n"
                                "- Assets: none (this screen is CSS only)\n\n")
    eq(_errors(_ticket(body=body), art), "", "an empty manifest is a valid, positive statement")


# --- the gate catches what shipped placeholders -----------------------------

def fe_ticket_without_assets_header_is_rejected():
    art = _sandbox(GOOD_MANIFEST)
    contains(_errors(_ticket(assets=""), art), "needs 'assets:'",
             "an [FE] ticket with no asset manifest must be rejected")


def fe_ticket_without_design_fidelity_is_rejected():
    art = _sandbox(GOOD_MANIFEST)
    contains(_errors(_ticket(body=BODY.format(fidelity="")), art), "## Design fidelity",
             "an [FE] ticket with no design-fidelity section must be rejected")


def zero_byte_asset_is_rejected():
    """A failed download leaves an empty file and every later check passes."""
    art = _sandbox(GOOD_MANIFEST, assets_on_disk=(("logo.svg", ""),))
    contains(_errors(_ticket(), art), "0 bytes",
             "an asset that downloaded as 0 bytes must be rejected")


def zero_byte_screenshot_is_rejected():
    """9794-6547.png sat empty in fms-studio for five days."""
    art = _sandbox(GOOD_MANIFEST, shot_bytes=b"")
    contains(_errors(_ticket(), art), "0 bytes",
             "a screenshot that downloaded as 0 bytes must be rejected")


def empty_asset_cache_says_how_to_rebuild():
    """The binaries are a gitignored cache; a fresh clone has none. That is not a spec defect."""
    art = _sandbox(GOOD_MANIFEST, assets_on_disk=())
    out = _errors(_ticket(), art)
    contains(out, "asset cache", "an empty cache must be named as such")
    contains(out, "download_figma_images", "the error must say how to rebuild it")


def missing_asset_file_is_rejected():
    """One file gone while its siblings are there is a real defect, not a cold cache."""
    art = _sandbox(GOOD_MANIFEST, assets_on_disk=(("unrelated.png", "x"),))
    contains(_errors(_ticket(), art), "file not found",
             "a manifest entry whose file is missing from a populated cache must be rejected")


def named_colour_instead_of_hex_is_rejected():
    """'orange' is not a token. Generic Tailwind is what the placeholder build used."""
    art = _sandbox(GOOD_MANIFEST)
    body = BODY.format(fidelity="## Design fidelity\n- Tokens: Primary orange, dark grey text\n"
                                "- Assets:\n  - `assets/logo.svg` -> `frontend/public/brand/logo.svg`\n\n")
    contains(_errors(_ticket(body=body), art), "no colour as hex",
             "colours named in prose must be rejected")


def asset_owned_by_nobody_is_rejected():
    """A manifest entry no ticket claims is a file that never reaches the repo."""
    art = _sandbox(GOOD_MANIFEST)
    body = BODY.format(fidelity="## Design fidelity\n- Tokens: Primary `#FF6100`\n"
                                "- Assets: see the manifest\n\n")
    contains(_errors(_ticket(body=body), art), "is in no ticket's",
             "an asset claimed by no ticket must be rejected")


def asset_owned_by_two_tickets_is_rejected():
    """Two tickets writing the same file is two developers colliding."""
    import contextlib, io
    art = _sandbox(GOOD_MANIFEST)
    push = _push()
    ctx = {"artifacts_dir": os.path.realpath(art), "has_figma": True}
    second = _ticket(title="[FE] Landing: hero states")
    buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(buf):
            push.validate([PARENT, _ticket(), second], ctx, spec_path=None)
    except SystemExit:
        pass
    contains(buf.getvalue(), "claimed by 2 tickets",
             "an asset two tickets both ship must be rejected")


def a_second_fe_ticket_may_own_no_assets():
    """A copy fix or a wiring ticket ships no artwork; it must not have to duplicate the list."""
    import contextlib, io
    art = _sandbox(GOOD_MANIFEST)
    push = _push()
    ctx = {"artifacts_dir": os.path.realpath(art), "has_figma": True}
    copyfix = _ticket(title="[FE] Landing: fix copy and links", estimate_hours="2",
                      body=BODY.format(fidelity="## Design fidelity\n"
                                                "- Tokens: Primary `#FF6100` - text `#313131`\n"
                                                "- Assets: none - the layout ticket ships them\n\n"))
    buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(buf):
            push.validate([PARENT, _ticket(), copyfix], ctx, spec_path=None)
    except SystemExit:
        pass
    eq(buf.getvalue(), "", "an [FE] ticket that owns no assets must pass when a sibling ships them")


def inventing_an_asset_path_is_rejected():
    """A path the body names but the manifest does not have was never downloaded."""
    art = _sandbox(GOOD_MANIFEST)
    body = BODY.format(fidelity="## Design fidelity\n- Tokens: Primary `#FF6100`\n"
                                "- Assets:\n  - `assets/logo.svg` -> `frontend/public/brand/logo.svg`\n"
                                "  - `assets/hero.png` -> `frontend/public/hero.png`\n\n")
    contains(_errors(_ticket(body=body), art), "not in the asset manifest",
             "an asset named in the body but never downloaded must be rejected")


def broken_manifest_json_is_rejected():
    art = _sandbox(GOOD_MANIFEST)
    open(os.path.join(art, "specs", "_figma", "landing", "assets", "manifest.json"),
         "w", encoding="utf-8").write("{not json")
    contains(_errors(_ticket(), art), "not readable JSON",
             "an unparseable manifest must be rejected, not skipped")


def manifest_outside_artifacts_is_rejected():
    art = _sandbox(GOOD_MANIFEST)
    contains(_errors(_ticket(assets="/etc/manifest.json"), art), "outside Internal Artifacts",
             "a manifest path outside Internal Artifacts must be rejected")


# --- non-UI lanes stay unaffected -------------------------------------------

def backend_ticket_needs_no_assets():
    """[BE]/[DB]/[QA] have no screen; the gate must not invent work for them."""
    art = _sandbox(GOOD_MANIFEST)
    be = _ticket(title="[BE] Landing: none", lane="BE", figma="", screenshots="", assets="",
                 body=BODY.format(fidelity=""))
    out = _errors(be, art)
    not_contains(out, "needs 'assets:'", "a [BE] ticket must not be asked for an asset manifest")
    not_contains(out, "## Design fidelity", "a [BE] ticket must not be asked for design fidelity")


def project_without_figma_is_unaffected():
    """has_figma=false projects (CLI tools, libraries) keep working with no design headers."""
    import contextlib
    import io
    art = _sandbox(GOOD_MANIFEST)
    push = _push()
    ctx = {"artifacts_dir": os.path.realpath(art), "has_figma": False}
    fe = _ticket(figma="", screenshots="", assets="", body=BODY.format(fidelity=""))
    buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(buf):
            push.validate([PARENT, fe], ctx, spec_path=None)
    except SystemExit:
        pass
    not_contains(buf.getvalue(), "assets", "a project with no Figma file must not need a manifest")


CASES = [
    ("design: complete FE ticket passes", complete_fe_ticket_passes),
    ("design: CSS-only screen passes with empty manifest", css_only_screen_passes_with_empty_manifest),
    ("design: FE without assets header", fe_ticket_without_assets_header_is_rejected),
    ("design: FE without design fidelity", fe_ticket_without_design_fidelity_is_rejected),
    ("design: zero-byte asset", zero_byte_asset_is_rejected),
    ("design: zero-byte screenshot", zero_byte_screenshot_is_rejected),
    ("design: empty asset cache", empty_asset_cache_says_how_to_rebuild),
    ("design: manifest entry file missing", missing_asset_file_is_rejected),
    ("design: colour named instead of hex", named_colour_instead_of_hex_is_rejected),
    ("design: asset owned by nobody", asset_owned_by_nobody_is_rejected),
    ("design: asset owned by two tickets", asset_owned_by_two_tickets_is_rejected),
    ("design: sibling FE ticket owns no assets", a_second_fe_ticket_may_own_no_assets),
    ("design: invented asset path", inventing_an_asset_path_is_rejected),
    ("design: unparseable manifest", broken_manifest_json_is_rejected),
    ("design: manifest outside artifacts", manifest_outside_artifacts_is_rejected),
    ("design: backend ticket needs no assets", backend_ticket_needs_no_assets),
    ("design: project without figma unaffected", project_without_figma_is_unaffected),
]
