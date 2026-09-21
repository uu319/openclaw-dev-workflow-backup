#!/usr/bin/env python3
"""Launch the Figma MCP server (figma-developer-mcp) for ONE project.

Usage (as the `command` of an `mcp.servers["figma-<slug>"]` entry, never by hand):
  figma_mcp.py <slug>

The gateway starts this over stdio. It reads projects/<slug>/PROJECT_CONTEXT.md,
takes the Design secret name from it, reads that env-kind value from the
OpenClaw secret store, then replaces itself with the MCP server:
  FIGMA_API_KEY = the project's own key (never another project's)
  IMAGE_DIR     = the project's Internal Artifacts dir: screenshots and assets land
                  there (never in the git repo); VanDev copies assets it needs into Code (CWD)
  cwd           = the project's Internal Artifacts dir (figma-developer-mcp loads
                  <cwd>/.env with override, so it must never start inside the repo)
Telemetry is off. Nothing is printed to stdout (that is the MCP channel).
Standard library only.
"""
import importlib.util
import os
import shutil
import subprocess
import sys

# The workspace root. `OPENCLAW_WORKSPACE` overrides it so the tools can be run
# against an isolated copy (tests, a dry run of a new project) without touching
# the live tree - which the heartbeat scans every 15 minutes and acts on.
WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", "/home/openclaw/.openclaw/workspace")
VALIDATOR = f"{WORKSPACE}/projects/_tools/validate_context.py"
SERVER_JS = "/home/openclaw/.local/lib/figma-developer-mcp/node_modules/figma-developer-mcp/dist/bin.js"


def die(m):
    print(f"figma_mcp: {m}", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        die("usage: figma_mcp.py <slug>")
    slug = sys.argv[1]
    ctx = f"{WORKSPACE}/projects/{slug}/PROJECT_CONTEXT.md"
    if not os.path.isfile(ctx):
        die(f"no PROJECT_CONTEXT.md for '{slug}' at {ctx}")

    spec = importlib.util.spec_from_file_location("vc", VALIDATOR)
    vc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vc)
    fields, errors = vc.parse(ctx)
    if errors:
        die(f"invalid {ctx}: " + "; ".join(errors))
    if fields.get("figma_mcp_server") != f"figma-{slug}":
        die(f"{ctx} must list '**Figma MCP server:** `figma-{slug}`'")

    name = fields.get("design_secret")
    if not name:
        die(f"{ctx} has no 'Design:' SecretRef line; a project without Figma has no figma-{slug} server")
    openclaw = shutil.which("openclaw") or "/usr/bin/openclaw"
    r = subprocess.run([openclaw, "secrets", "store", "get", "--plain", name],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    key = r.stdout.strip()
    if r.returncode != 0 or not key:
        die(f"could not read env-kind secret {name} (exit {r.returncode}): {r.stderr.strip()[:300]} "
            f"-- store it with: openclaw secrets store set {name} --kind env --value-file -")

    artifacts = fields["artifacts_dir"]
    os.makedirs(artifacts, exist_ok=True)
    os.chdir(artifacts)

    env = dict(os.environ)
    for k in ("FIGMA_OAUTH_TOKEN", "FIGMA_API_KEY"):
        env.pop(k, None)
    env.update({
        "FIGMA_API_KEY": key,
        "IMAGE_DIR": artifacts,
        "DO_NOT_TRACK": "1",
    })
    node = shutil.which("node") or "/usr/bin/node"
    os.execve(node, [node, SERVER_JS, "--stdio", "--no-telemetry"], env)


if __name__ == "__main__":
    main()
