#!/usr/bin/env python3
"""Check the Team roster in the main agent's AGENTS.md against OpenClaw config and skills on disk.

Usage: validate_team.py [--config PATH] [--agents-md PATH]
Prints each problem and exits 1, or prints VALID and exits 0.
"""
import argparse
import json
import os
import re
import sys

HOME = os.path.expanduser("~")
DEFAULT_CONFIG = os.path.join(HOME, ".openclaw", "openclaw.json")
MAIN_ID = "main"
BOOTSTRAP_MAX_CHARS = 20000  # OpenClaw default for agents.defaults.bootstrapMaxChars
ENTRY_RE = re.compile(r"^####\s+`([^`]+)`\s*[-–—]\s*(.+?)\s*$")
FIELD_RE = re.compile(r"^-\s+\*\*([^*]+?):\*\*\s*(.*)$")
REQUIRED = {"Agents": ["Owns", "Spawn with"], "Workflows": ["Use for", "Agents"]}


def parse_roster(text):
    lines = text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == "## Team roster")
    except StopIteration:
        return None
    roster = {"Agents": {}, "Workflows": {}}
    group = entry = None
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        if line.startswith("### "):
            group = line[4:].strip()
            entry = None
            continue
        m = ENTRY_RE.match(line)
        if m:
            entry = {"name": m.group(2), "fields": {}, "dup": False}
            bucket = roster.setdefault(group or "?", {})
            if m.group(1) in bucket:
                bucket[m.group(1)]["dup"] = True
            else:
                bucket[m.group(1)] = entry
            continue
        f = FIELD_RE.match(line.strip())
        if f and entry is not None:
            entry["fields"][f.group(1).strip()] = f.group(2).strip()
    return roster


def find_skill(skill_id, workspace):
    for base in (os.path.join(workspace, "skills"),
                 os.path.join(HOME, ".openclaw", "skills"),
                 "/usr/lib/node_modules/openclaw/skills"):
        path = os.path.join(base, skill_id, "SKILL.md")
        if os.path.isfile(path):
            return path
    return None


def skill_name(path):
    with open(path) as fh:
        m = re.search(r"^name:\s*(\S+)", fh.read(), re.M)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=DEFAULT_CONFIG)
    ap.add_argument("--agents-md")
    args = ap.parse_args()

    errors, warnings = [], []
    try:
        with open(args.config) as fh:
            cfg = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"ERROR cannot read config {args.config}: {exc}")
        return 1

    entries = (cfg.get("agents") or {}).get("entries") or {}
    main_entry = entries.get(MAIN_ID) or {}
    workspace = main_entry.get("workspace") or os.path.join(HOME, ".openclaw", "workspace")
    agents_md = args.agents_md or os.path.join(workspace, "AGENTS.md")
    allow = ((main_entry.get("subagents") or {}).get("allowAgents")
             or ((cfg.get("agents") or {}).get("defaults") or {}).get("subagents", {}).get("allowAgents")
             or [])
    allow_any = "*" in allow

    try:
        with open(agents_md) as fh:
            text = fh.read()
        roster = parse_roster(text)
    except OSError as exc:
        print(f"ERROR cannot read {agents_md}: {exc}")
        return 1
    if roster is None:
        print(f"ERROR no '## Team roster' section in {agents_md}")
        return 1

    limit = ((cfg.get("agents") or {}).get("defaults") or {}).get("bootstrapMaxChars") or BOOTSTRAP_MAX_CHARS
    if len(text) > limit:
        errors.append(f"{agents_md} is {len(text)} chars; OpenClaw truncates it at {limit}, cutting off the roster")
    elif len(text) > 0.85 * limit:
        warnings.append(f"{agents_md} is {len(text)} of {limit} chars; trim it before the roster gets truncated")

    for group in roster:
        if group not in REQUIRED:
            errors.append(f"unknown roster group '### {group}' (use '### Agents' or '### Workflows')")

    agents = roster.get("Agents", {})
    workflows = roster.get("Workflows", {})

    for group, items in (("Agents", agents), ("Workflows", workflows)):
        for item_id, e in items.items():
            if e["dup"]:
                errors.append(f"{group}: `{item_id}` is listed more than once")
            for field in REQUIRED[group]:
                if not e["fields"].get(field):
                    errors.append(f"{group}: `{item_id}` is missing '- **{field}:**'")

    for agent_id in agents:
        if agent_id == MAIN_ID:
            errors.append("Agents: `main` is you; don't list yourself")
            continue
        entry = entries.get(agent_id)
        if entry is None:
            errors.append(f"Agents: `{agent_id}` is not configured in OpenClaw (openclaw agents add {agent_id} ...)")
            continue
        if not allow_any and agent_id not in allow:
            errors.append(f"Agents: `{agent_id}` is not in agents.entries.main.subagents.allowAgents, so spawning it will fail")
        ws = entry.get("workspace")
        if not ws or not os.path.isdir(ws):
            warnings.append(f"Agents: `{agent_id}` workspace missing: {ws}")
        elif not os.path.isfile(os.path.join(ws, "AGENTS.md")):
            warnings.append(f"Agents: `{agent_id}` has no AGENTS.md describing its lane in {ws}")

    for agent_id in entries:
        if agent_id != MAIN_ID and agent_id not in agents:
            errors.append(f"Config: agent `{agent_id}` exists but is not in the roster, so the main agent will never use it")
    for agent_id in allow:
        if agent_id not in ("*", MAIN_ID) and agent_id not in agents:
            errors.append(f"Config: allowAgents lists `{agent_id}` but the roster doesn't")

    for wf_id, e in workflows.items():
        path = find_skill(wf_id, workspace)
        if path is None:
            errors.append(f"Workflows: `{wf_id}` has no skills/{wf_id}/SKILL.md")
        elif skill_name(path) != wf_id:
            errors.append(f"Workflows: {path} has name '{skill_name(path)}', expected '{wf_id}'")
        for used in [a.strip(" `") for a in e["fields"].get("Agents", "").split(",") if a.strip()]:
            if used not in agents:
                errors.append(f"Workflows: `{wf_id}` uses `{used}`, which is not in the Agents roster")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    if errors:
        return 1
    print(f"VALID  {len(agents)} agents, {len(workflows)} workflows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
