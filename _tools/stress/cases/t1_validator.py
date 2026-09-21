#!/usr/bin/env python3
"""Tier 1 - PROJECT_CONTEXT parsing.

Every case here is a WRONG-BUT-ACCEPTED parse: the validator returns success and
a value that is not what the file says. Those are worse than errors, because the
wrong value flows into `git_env.py`'s enforced PR base, the watcher's branch, or
a ticket-moving decision.

Cases assert the CORRECT outcome, so a case that fails is a defect that is still
open - not a broken test.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import contains, eq, not_contains, parsed  # noqa: E402

TITLE = "validator: wrong-but-accepted parses"


def _flow(fields, key):
    return (fields.get("flow") or {}).get(key)


# --- backticks in a parenthetical steal the value ---------------------------

def backtick_hijack_deploy_signal():
    """A parenthetical is prose, not the value. Same class as the 12.5f bug."""
    f, errs = parsed(("- **Deploy signal:** `none`",
                      "- **Deploy signal:** none (was `cloud-build`)"))
    eq(_flow(f, "deploy_signal"), "none",
       "a backticked aside must not become the Deploy signal")


def backtick_hijack_pr_base():
    """PR base flows into git_env.py's enforced --base, so a wrong value is a wrong merge target."""
    f, errs = parsed(("- **Merge by:** `van`",
                      "- **Merge by:** `van`\n- **PR base:** main (never `develop`)"))
    eq(_flow(f, "pr_base"), "main",
       "a backticked aside must not become the PR base")


# --- whole sections silently ignored ----------------------------------------

def crlf_flow_section_is_not_silently_dropped():
    """`## Flow` is matched with a bare \\n, so a CRLF file falls back to defaults."""
    f, errs = parsed(("- **Profile:** `factory`", "- **Profile:** `teammate`"))
    base_profile = _flow(f, "profile")
    eq(base_profile, "teammate", "sanity: the LF file parses its profile")

    crlf = open(
        __import__("harness").context(("- **Profile:** `factory`", "- **Profile:** `teammate`")),
        encoding="utf-8").read().replace("\n", "\r\n")
    import harness
    f2, errs2 = __import__("harness").load(
        "vc_crlf", os.path.join(harness.TOOLS, "validate_context.py")).parse(
        harness.context(base=crlf))
    got = (f2.get("flow") or {}).get("profile")
    if got != "teammate":
        # falling back silently is the bug; an explicit error would also be acceptable
        contains([w for w in f2.get("warnings", [])] + errs2, "flow",
                 "a CRLF file must not silently lose its whole ## Flow section")
        raise AssertionError(
            "CRLF silently reverted the Flow profile to 'factory' (warning only). "
            "Either parse \\r\\n or make it a hard error.")


# --- unanchored patterns pick up prose --------------------------------------

def prose_cannot_hijack_the_tracker_secret():
    """`Tracker:\\s*`X`` has no `**` and no anchor, so any sentence matching it wins."""
    f, errs = parsed(("## Workflow Rules",
                      "## Workflow Rules\n<!-- If the Tracker: `WRONG_NAME_FROM_PROSE` is stale, re-store it. -->"))
    eq(f.get("tracker_secret"), "CLICKUP_API_TOKEN_HARNESS",
       "a commented sentence must not become the vault key name")


# --- a placeholder silently empties a list ----------------------------------

def placeholder_must_not_silently_empty_deploy_checks():
    """An empty expected set makes a commit 'green' on ONE passing check."""
    f, errs = parsed(("- **Deploy checks:** `deploy-fe`, `deploy-be`",
                      "- **Deploy checks:** `deploy-fe`, <the backend one, TBD>"))
    checks = f.get("deploy_checks")
    if checks == []:
        raise AssertionError(
            "one unfilled placeholder silently emptied Deploy checks, so every commit "
            "is judged deployed on a single green run; expected ['deploy-fe'] or an error")
    eq(checks, ["deploy-fe"], "the filled check must survive a placeholder beside it")


def branch_prefixes_without_backticks_is_not_silently_empty():
    """Empty prefixes disable the worktree guard AND make is_ours() claim every PR."""
    f, errs = parsed(("- **Branch Prefixes:** `feature/`, `bug/`",
                      "- **Branch Prefixes:** feature/, bug/"))
    got = f.get("branch_prefixes")
    if got in ([], None):
        raise AssertionError(
            "prefixes written without backticks parsed as empty; that disables the "
            "worktree prefix guard and the PR-ownership fallback. Expected them parsed or an error.")
    eq(got, ["feature/", "bug/"], "prefixes should parse with or without backticks")


# --- duplicates and shapes ---------------------------------------------------

def a_duplicated_label_is_reported():
    """First match wins silently, so a 'corrected' line below the original is ignored."""
    f, errs = parsed(("- **Create status:** `to do`",
                      "- **Create status:** `to do`\n- **Create status:** `in progress`"))
    contains(errs, "declared more than once",
             "a field declared twice with different values must be reported, not silently first-wins")


def github_repo_must_not_allow_path_traversal():
    """`owner/..` collapses the API path in every gh call built from it."""
    f, errs = parsed(("- **GitHub Repo:** `acme/harness`", "- **GitHub Repo:** `acme/..`"))
    contains(errs, "github repo", "owner/.. must be refused as a repo name")


def pr_stages_need_a_repo_to_act_on():
    """review, merge-gate and delivery-watch all operate on pull requests.

    Only delivery-watch used to be checked, so a project could declare a review
    stage with no repo behind it: onboarding passed, then step 3 had nothing to
    open a PR against. Each stage must be named in the error so the fix is obvious.
    """
    for stage in ("review", "merge-gate", "delivery-watch"):
        f, errs = parsed(("- **Profile:** `factory`",
                          f"- **Profile:** `custom`\n- **Stages:** `{stage}`"),
                         ("- **GitHub Repo:** `acme/harness`\n", ""))
        contains(errs, "GitHub Repo",
                 f"stage `{stage}` acts on PRs, so a missing repo must be refused")
        contains(errs, stage, f"the error must name `{stage}` as the stage that needs it")

    # ...and a stage set that needs no repo must still onboard without one.
    # The GitHub Token SecretRef goes too: it requires a repo on its own, which
    # is a separate (correct) rule and would mask what this case is checking.
    f, errs = parsed(("- **Profile:** `factory`",
                      "- **Profile:** `custom`\n- **Stages:** `spec`, `tickets`"),
                     ("- **GitHub Repo:** `acme/harness`\n", ""),
                     ("  - GitHub Token: `GITHUB_TOKEN_HARNESS`\n", ""))
    if any("act on" in e for e in errs):
        raise AssertionError(f"spec+tickets act on no PR, so need no repo, but got: {errs}")


def a_status_containing_a_comma_is_not_split():
    f, errs = parsed(("- **Statuses:** `to do`, `in progress`, `qa`, `rejected`, `on hold`, `complete`, `cancelled`",
                      "- **Statuses:** `to do`, `done, verified`, `in progress`, `cancelled`"),
                     )
    st = f.get("statuses") or []
    if "done" in st and "verified" in st:
        raise AssertionError(
            "a backticked status containing a comma was split into two; "
            f"expected 'done, verified' to survive intact, got {st}")


# --- inference that guesses wrong --------------------------------------------

def an_unparseable_tracker_line_does_not_silently_become_clickup():
    """Trailing content breaks the match, and the fallback infers clickup from a board id."""
    f, errs = parsed(("- **Tracker:** `clickup`", "- **Tracker:** `jira` (moved from ClickUp)"))
    if f.get("tracker") == "clickup" and not errs:
        raise AssertionError(
            "a Tracker line the regex could not read silently inferred `clickup` from the "
            "board id - so a Jira project would be given a ClickUp adapter. Expected `jira` or an error.")
    eq(f.get("tracker"), "jira", "the declared tracker must win")


def board_id_has_a_sane_length_cap():
    """An unbounded id is concatenated straight into an API URL."""
    f, errs = parsed(("- **Tracker Board ID:** `1100770000001008`",
                      "- **Tracker Board ID:** `" + "9" * 4000 + "`"))
    if not errs:
        raise AssertionError("a 4000-digit board id was accepted and would be sent to the tracker API")


def a_plain_kanban_board_can_be_onboarded():
    """To Do / In Progress / In Review / Done - no cancelled, no QA column.

    The framework used to REQUIRE `cancelled`, so this perfectly ordinary board
    could not be onboarded at all. `cancelled` is used in exactly one place (the
    closed set, beside `done`), so its absence just means nothing is cancelled.
    """
    f, errs = parsed(
        ("- **Statuses:** `to do`, `in progress`, `qa`, `rejected`, `on hold`, `complete`, `cancelled`",
         "- **Statuses:** `To Do`, `In Progress`, `In Review`, `Done`"),
        ("- **Create status:** `to do`", "- **Create status:** `To Do`"))
    eq(errs, [], "a board with no cancelled/qa/hold column must still onboard")
    eq(f["status"]["doing"], "In Progress", "the two load-bearing keys must still resolve")
    eq(f["status"]["done"], "Done", "the two load-bearing keys must still resolve")
    eq(f["status"]["cancelled"], None, "an absent status maps to None, not an error")
    contains(f.get("warnings", []), "cancelled",
             "what is lost by an absent status must be said, not silently assumed")


def fms_studio_vocabulary_is_not_in_the_shared_alias_table():
    """"For Development" was one project's name for a REJECTED column.

    Left in the shared inference table, a board that uses it to mean *todo* has
    its todo tickets inferred as rejected - which makes the watcher emit a
    REJECTED action per ticket and spawn VanPM and VanDev at each one.
    """
    f, errs = parsed(
        ("- **Statuses:** `to do`, `in progress`, `qa`, `rejected`, `on hold`, `complete`, `cancelled`",
         "- **Statuses:** `For Development`, `In Progress`, `Done`"),
        ("- **Create status:** `to do`", "- **Create status:** `For Development`"))
    eq(errs, [], "this board must onboard")
    if f["status"].get("rejected") == "For Development":
        raise AssertionError(
            "'For Development' was inferred as the REJECTED status - one project's "
            "vocabulary in a table applied to every project. Each of those tickets would "
            "produce a REJECTED action and spawn agents.")


CASES = [
    ("backtick aside hijacks Deploy signal", backtick_hijack_deploy_signal),
    ("backtick aside hijacks PR base", backtick_hijack_pr_base),
    ("CRLF silently drops the Flow section", crlf_flow_section_is_not_silently_dropped),
    ("prose hijacks the Tracker SecretRef", prose_cannot_hijack_the_tracker_secret),
    ("placeholder empties Deploy checks", placeholder_must_not_silently_empty_deploy_checks),
    ("branch prefixes without backticks", branch_prefixes_without_backticks_is_not_silently_empty),
    ("duplicated label accepted silently", a_duplicated_label_is_reported),
    ("PR stages need a repo", pr_stages_need_a_repo_to_act_on),
    ("github repo path traversal", github_repo_must_not_allow_path_traversal),
    ("status name containing a comma", a_status_containing_a_comma_is_not_split),
    ("unparseable Tracker line infers clickup", an_unparseable_tracker_line_does_not_silently_become_clickup),
    ("board id length cap", board_id_has_a_sane_length_cap),
    ("plain Kanban board onboards", a_plain_kanban_board_can_be_onboarded),
    ("no project vocabulary in the alias table", fms_studio_vocabulary_is_not_in_the_shared_alias_table),
]

