#!/usr/bin/env python3
"""Run a command against ONE project's GCP identity. Never touches global gcloud state.

Usage:
  gcloud_env.py <slug> -- <command> [args...]
  gcloud_env.py <slug> --export        # print the env assignments, for eval/debugging

Sibling of figma_mcp.py: same rule, same shape. The project's PROJECT_CONTEXT.md is the
single source of truth. This reads it, resolves that project's own service-account key,
and execs the command with the credentials injected into the CHILD ENVIRONMENT ONLY:

  GOOGLE_APPLICATION_CREDENTIALS         -> libraries / SDKs (ADC)
  CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE -> the gcloud CLI
  CLOUDSDK_CORE_PROJECT / _COMPUTE_REGION-> the project and region from PROJECT_CONTEXT
  CLOUDSDK_ACTIVE_CONFIG_NAME=<slug>     -> any `gcloud config set` lands in this project's
                                            own named configuration, never in `default`

Nothing is written to ~/.bashrc, no `gcloud config set` is run, and the ambient default
configuration is never read. If the slug has no GCP environment this exits non-zero with a
message naming the field to fill, so an agent fails loudly instead of silently acting as
some other project's service account.

If the key file is missing it is materialized from the OpenClaw secret vault entry named in
PROJECT_CONTEXT.md (GCP Key Vault) and written 0600.

Standard library only.
"""
import importlib.util
import os
import shutil
import stat
import subprocess
import sys

WORKSPACE = "/home/openclaw/.openclaw/workspace"
VALIDATOR = f"{WORKSPACE}/projects/_tools/validate_context.py"


def die(m):
    print(f"gcloud_env: {m}", file=sys.stderr)
    sys.exit(1)


def load_fields(slug):
    ctx = f"{WORKSPACE}/projects/{slug}/PROJECT_CONTEXT.md"
    if not os.path.isfile(ctx):
        die(f"no PROJECT_CONTEXT.md for '{slug}' at {ctx}")
    spec = importlib.util.spec_from_file_location("vc", VALIDATOR)
    vc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vc)
    fields, errors = vc.parse(ctx)
    if errors:
        die(f"invalid {ctx}: " + "; ".join(errors))
    return ctx, fields


def ensure_key(ctx, fields):
    key = fields.get("gcp_key_json")
    if not key:
        die(f"{ctx} has no 'GCP Key JSON:' SecretRef line")
    if os.path.isfile(key) and os.path.getsize(key) > 0:
        return key
    name = fields.get("gcp_key_secret")
    if not name:
        die(f"{key} is missing and {ctx} has no 'GCP Key Vault:' SecretRef to restore it from")
    openclaw = shutil.which("openclaw") or "/usr/bin/openclaw"
    r = subprocess.run([openclaw, "secrets", "store", "get", "--plain", name],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    blob = r.stdout.strip()
    if r.returncode != 0 or not blob:
        die(f"key file {key} is missing and vault entry {name} could not be read "
            f"(exit {r.returncode}): {r.stderr.strip()[:300]}")
    os.makedirs(os.path.dirname(key), exist_ok=True)
    fd = os.open(key, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IRUSR | stat.S_IWUSR)
    with os.fdopen(fd, "w") as fh:
        fh.write(blob if blob.endswith("\n") else blob + "\n")
    return key


def build_env(slug, fields, key):
    env = dict(os.environ)
    # Drop anything inherited that could point at another project.
    for k in ("GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CLOUD_PROJECT", "GCLOUD_PROJECT",
              "CLOUDSDK_CORE_PROJECT", "CLOUDSDK_CORE_ACCOUNT", "CLOUDSDK_ACTIVE_CONFIG_NAME",
              "CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE", "CLOUDSDK_COMPUTE_REGION"):
        env.pop(k, None)
    env.update({
        "GOOGLE_APPLICATION_CREDENTIALS": key,
        "CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE": key,
        "CLOUDSDK_CORE_PROJECT": fields["gcp_project_id"],
        "GOOGLE_CLOUD_PROJECT": fields["gcp_project_id"],
        "CLOUDSDK_ACTIVE_CONFIG_NAME": slug,
    })
    if fields.get("gcp_region"):
        env["CLOUDSDK_COMPUTE_REGION"] = fields["gcp_region"]
    return env


def main():
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        sys.exit(1)
    slug = argv[0]
    rest = argv[1:]

    ctx, fields = load_fields(slug)
    if not fields.get("gcp_project_id"):
        die(f"project '{slug}' has no GCP environment: {ctx} is missing "
            f"'**GCP Project ID:**'. Fill that field (and the GCP SecretRefs) before "
            f"running any gcloud/GCP command for this project. Refusing to fall back to "
            f"an ambient default, which would act as a different project's service account.")
    key = ensure_key(ctx, fields)
    env = build_env(slug, fields, key)

    if rest and rest[0] == "--export":
        for k in ("GOOGLE_APPLICATION_CREDENTIALS", "CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE",
                  "CLOUDSDK_CORE_PROJECT", "GOOGLE_CLOUD_PROJECT",
                  "CLOUDSDK_ACTIVE_CONFIG_NAME", "CLOUDSDK_COMPUTE_REGION"):
            if k in env:
                print(f"export {k}={env[k]}")
        return
    if rest and rest[0] == "--":
        rest = rest[1:]
    if not rest:
        die("nothing to run: use 'gcloud_env.py <slug> -- <command> [args...]' or '--export'")

    exe = shutil.which(rest[0], path=env.get("PATH", os.defpath))
    if not exe:
        die(f"command not found: {rest[0]}")
    os.execve(exe, rest, env)


if __name__ == "__main__":
    main()
