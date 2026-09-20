#!/usr/bin/env python3
"""MCP server for one project's tracker, whichever tracker that is.

    mcp.servers["tracker-<slug>"] -> tracker_mcp.py <slug>

Same rule as figma_mcp.py / gcloud_env.py / git_env.py: the secret NAME comes
from the project's PROJECT_CONTEXT.md (`Tracker:` SecretRef), the VALUE from the
OpenClaw vault. No environment fallback, no hardcoded project, no hardcoded
tracker - the provider comes from the context file's `**Tracker:**` line and the
work is done by projects/_tools/trackers/.

Tool names are provider-neutral (`tracker_get_task`, `tracker_create_task`,
`tracker_update_task`) so a project can change tracker without any agent's deny
list, prompt or skill changing.

The board is taken from the context file, never from the caller: a single source
of truth is the whole point, and an agent that could pass a board id could pass
the wrong one.

Standard library only.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys

WORKSPACE = "/home/openclaw/.openclaw/workspace"
sys.path.insert(0, os.path.join(WORKSPACE, "projects/_tools"))
import trackers  # noqa: E402


class TrackerMCP:
    def __init__(self):
        self.tk, self.error, self.kind = None, None, "none"
        if len(sys.argv) < 2:
            self.error = "usage: tracker_mcp.py <slug>"
            return
        slug = sys.argv[1]
        ctx = f"{WORKSPACE}/projects/{slug}/PROJECT_CONTEXT.md"
        try:
            spec = importlib.util.spec_from_file_location(
                "vc", f"{WORKSPACE}/projects/_tools/validate_context.py")
            vc = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(vc)
            fields, _errors = vc.parse(ctx)
            self.kind = fields.get("tracker", "none")
            if self.kind == "none":
                self.error = f"{ctx} says `Tracker: none`: this project has no ticket system"
                return
            name = fields.get("tracker_secret")
            if not name:
                self.error = f"{ctx} has no 'Tracker:' SecretRef"
                return
            r = subprocess.run(
                [shutil.which("openclaw") or "/usr/bin/openclaw",
                 "secrets", "store", "get", "--plain", name],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            token = r.stdout.strip()
            if not token:
                self.error = (f"vault entry {name} (from {ctx}) could not be read: "
                              f"{r.stderr.strip()[:200]}")
                return
            self.tk = trackers.for_project(fields, token)
        except Exception as e:  # never crash the MCP handshake; report on first call
            self.error = f"could not set up the tracker for {slug}: {e}"

    def _need(self):
        if self.tk is None:
            raise RuntimeError(self.error or "tracker unavailable")
        return self.tk

    # --- tools ---------------------------------------------------------------
    def get_task(self, task_id):
        tk = self._need()
        found = tk.tasks().get(task_id)
        if found:
            return found
        # fall back to a direct read for a task the board listing did not include
        return {"id": task_id, "url": tk.task_url(task_id),
                "note": "not found on this project's board"}

    def create_task(self, name, description="", status=None, parent=None, tags=None):
        return self._need().create_task(name, description=description, status=status,
                                        parent=parent, tags=tags)

    def update_task(self, task_id, status=None, description=None):
        tk = self._need()
        if not status and not description:
            return {"error": "No fields to update provided."}
        if description:
            raise RuntimeError("description edits go through VanPM's feature-breakdown "
                               "scripts, which keep the spec markers in sync")
        tk.set_status(task_id, status)
        return {"id": task_id, "status": status, "ok": True}

    TOOLS = [
        {"name": "tracker_get_task",
         "description": "Fetch one ticket from this project's tracker.",
         "inputSchema": {"type": "object", "properties": {
             "task_id": {"type": "string", "description": "Ticket id or key"}},
             "required": ["task_id"]}},
        {"name": "tracker_create_task",
         "description": "Create a ticket or subtask on this project's board.",
         "inputSchema": {"type": "object", "properties": {
             "name": {"type": "string", "description": "Ticket title"},
             "description": {"type": "string", "description": "Markdown body"},
             "status": {"type": "string", "description": "Board status name"},
             "parent": {"type": "string", "description": "Parent ticket id (for a subtask)"},
             "tags": {"type": "array", "items": {"type": "string"}}},
             "required": ["name"]}},
        {"name": "tracker_update_task",
         "description": "Move one ticket to another status on this project's board.",
         "inputSchema": {"type": "object", "properties": {
             "task_id": {"type": "string", "description": "Ticket id or key"},
             "status": {"type": "string", "description": "Board status name"}},
             "required": ["task_id"]}},
    ]

    def handle_request(self, request):
        try:
            method = request.get("method")
            params = request.get("params", {})
            if method == "initialize":
                return {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
                        "serverInfo": {"name": "tracker_mcp", "version": "2.0.0"}}
            if method == "tools/list":
                return {"tools": self.TOOLS}
            if method == "tools/call":
                tool, args = params.get("name"), params.get("arguments", {})
                fn = {"tracker_get_task": self.get_task,
                      "tracker_create_task": self.create_task,
                      "tracker_update_task": self.update_task}.get(tool)
                if fn is None:
                    return {"isError": True,
                            "content": [{"type": "text", "text": f"Unknown tool: {tool}"}]}
                return {"content": [{"type": "text",
                                     "text": json.dumps(fn(**args), indent=2, default=str)}]}
            return {"error": {"code": -32601, "message": "Method not found"}}
        except Exception as e:  # noqa: BLE001
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


def main():
    server = TrackerMCP()
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line)
            response = {"jsonrpc": "2.0", "id": request.get("id")}
            result = server.handle_request(request)
            if "error" in result and isinstance(result["error"], dict):
                response["error"] = result["error"]
            else:
                response["result"] = result
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            continue
        except KeyboardInterrupt:
            break
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"Server error: {e}\n")
            sys.stderr.flush()


if __name__ == "__main__":
    main()
