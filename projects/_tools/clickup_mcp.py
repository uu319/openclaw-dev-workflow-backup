#!/usr/bin/env python3
import sys
import json
import os
import importlib.util
import shutil
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime

# ClickUp API base
CLICKUP_API = "https://api.clickup.com/api/v2"

# FastMCP Server wrapper
class ClickUpMCP:
    def __init__(self):
        # Same rule as figma_mcp.py / gcloud_env.py / git_env.py: the secret NAME comes from the
        # project's PROJECT_CONTEXT.md ("Tracker:" SecretRef), the VALUE from the OpenClaw vault.
        # No environment fallback and no hardcoded project: a missing field fails loudly.
        self.token, self.token_error = None, None
        if len(sys.argv) < 2:
            self.token_error = "usage: clickup_mcp.py <slug>"
            return
        slug = sys.argv[1]
        ctx = f"/home/openclaw/.openclaw/workspace/projects/{slug}/PROJECT_CONTEXT.md"
        try:
            spec = importlib.util.spec_from_file_location(
                "vc", "/home/openclaw/.openclaw/workspace/projects/_tools/validate_context.py")
            vc = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(vc)
            fields, errors = vc.parse(ctx)
            name = fields.get("tracker_secret")
            if not name:
                self.token_error = f"{ctx} has no 'Tracker:' SecretRef"
                return
            r = subprocess.run([shutil.which("openclaw") or "/usr/bin/openclaw", "secrets", "store", "get",
                                "--plain", name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.token = r.stdout.strip() or None
            if not self.token:
                self.token_error = f"vault entry {name} (from {ctx}) could not be read: {r.stderr.strip()[:200]}"
        except Exception as e:  # never crash the MCP handshake; report on first call instead
            self.token_error = f"could not resolve the tracker token for {slug}: {e}"
        
    def _request(self, method, endpoint, payload=None):
        if not self.token:
            raise Exception(f"ClickUp API token unavailable: {self.token_error}")
        
        url = f"{CLICKUP_API}{endpoint}"
        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }
        
        data = None
        if payload:
            data = json.dumps(payload).encode('utf-8')
            
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode('utf-8')
            raise Exception(f"ClickUp API Error {e.code}: {err_msg}")

    def create_task(self, list_id, name, description="", status="to do", parent=None, tags=None):
        payload = {
            "name": name,
            "description": description,
            "status": status,
        }
        if parent:
            payload["parent"] = parent
        if tags:
            payload["tags"] = tags
            
        return self._request("POST", f"/list/{list_id}/task", payload)

    def update_task(self, task_id, status=None, description=None):
        payload = {}
        if status:
            payload["status"] = status
        if description:
            payload["description"] = description
            
        if not payload:
            return {"error": "No fields to update provided."}
            
        return self._request("PUT", f"/task/{task_id}", payload)

    def get_task(self, task_id):
        return self._request("GET", f"/task/{task_id}")

    def handle_request(self, request):
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            # Initialization
            if method == "initialize":
                return {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "clickup_mcp", "version": "1.0.0"}}
            
            # Tool Listing
            elif method == "tools/list":
                return {
                    "tools": [
                        {
                            "name": "clickup_create_task",
                            "description": "Create a new task or subtask in ClickUp.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "list_id": {"type": "string", "description": "The ClickUp List ID"},
                                    "name": {"type": "string", "description": "Task title"},
                                    "description": {"type": "string", "description": "Task markdown description"},
                                    "status": {"type": "string", "description": "Task status (e.g. 'to do')"},
                                    "parent": {"type": "string", "description": "Parent task ID (for subtasks)"},
                                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Array of string tags"}
                                },
                                "required": ["list_id", "name"]
                            }
                        },
                        {
                            "name": "clickup_update_task",
                            "description": "Update a ClickUp task's status or description.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "string", "description": "The ClickUp Task ID"},
                                    "status": {"type": "string", "description": "New status string"},
                                    "description": {"type": "string", "description": "New description string"}
                                },
                                "required": ["task_id"]
                            }
                        },
                        {
                            "name": "clickup_get_task",
                            "description": "Fetch a ClickUp task's details.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "string", "description": "The ClickUp Task ID"}
                                },
                                "required": ["task_id"]
                            }
                        }
                    ]
                }
            
            # Tool Execution
            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})
                
                result = None
                if tool_name == "clickup_create_task":
                    result = self.create_task(**args)
                elif tool_name == "clickup_update_task":
                    result = self.update_task(**args)
                elif tool_name == "clickup_get_task":
                    result = self.get_task(**args)
                else:
                    return {"isError": True, "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}]}
                
                # Format success result
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            
            # Unhandled
            return {"error": {"code": -32601, "message": "Method not found"}}
            
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def main():
    server = ClickUpMCP()
    
    # Simple JSON-RPC stdin/stdout loop
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            
            # JSON-RPC standard response wrapper
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
        except Exception as e:
            sys.stderr.write(f"Server error: {e}\n")
            sys.stderr.flush()

if __name__ == '__main__':
    main()
