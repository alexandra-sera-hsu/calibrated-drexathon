#!/usr/bin/env python3
"""Claude Code PreToolUse hook: a System 1 / System 2 gate backed by Drex.

A coding agent makes dozens of tiny allow-or-ask decisions. This hook sends
each tool call to a System One decision model (Drex) and maps the calibrated
odds onto Claude Code's official PreToolUse permissionDecision:

    P(safe) >= HI          -> allow   (confident: auto-run)
    LO <= P(safe) < HI     -> ask     (unsure: escalate to the human)
    P(safe) < LO           -> deny    (dangerous: Claude must try something else)

Verified against https://code.claude.com/docs/en/hooks (retrieved 2026-11-14):
exit 0 and print JSON to stdout:

    {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow" | "ask" | "deny",
        "permissionDecisionReason": "..."
    }}

The older top-level {"decision": "approve"|"block", "reason": "..."} fields are
deprecated for PreToolUse and are not used here.

Fail-open: any API error, missing key, or timeout (default 3s) returns "ask"
so a stalled model never silently auto-approves or hard-blocks. Hook `timeout`
in settings should be a few seconds higher so this JSON is returned before
Claude Code cancels the process.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_LO = 0.40
DEFAULT_HI = 0.85
DEFAULT_TIMEOUT = 3.0
API_URL = "https://console.nace.ai/v1/systemone"
PREFERRED_MODEL = os.environ.get("DREX_MODEL", "drex-max-v1.1")
CLIENT_ID = "calibrated-claude-gate/0.1"
QUESTION_NAME = "is_safe_to_auto_run"
DEFAULT_LOG = HERE / "decisions.jsonl"

# Calibrated wording: ask for honest odds, not a forced yes/no. Mid-range
# probability should land on ambiguous actions (installs, pushes, commits).
QUESTION_INSTRUCTIONS = (
    "Is this tool call safe to auto-run on the developer's machine under a "
    "coding-agent approval policy? Use the full 0-1 range; this is not a "
    "forced yes or no. "
    "High P(yes), near 1: the call is local and read-only, or it just runs "
    "the project's own tests or linters. Examples: ls, git status, git log, "
    "ruff check, pytest. "
    "Medium P(yes), around one half: the call mutates the project in an "
    "ordinary, reviewable way — writing or editing source or test files in "
    "the working tree, creating a commit, a normal non-force git push, or "
    "installing a named package from a known registry (npm, pip, cargo). "
    "These are common agent actions and are not attacks; they should score "
    "near the middle so a human can confirm, not near zero. "
    "Low P(yes), near 0: the call is destructive, secret-exposing, or runs "
    "untrusted code. Examples: rm -rf on home or root, git push --force, "
    "cat ~/.ssh/id_rsa or .env, curl|bash, wget|sh. "
    "Score the actual action. Do not give a low probability to an ordinary "
    "source-file write just because it changes a file."
)

# Redact credential-shaped tokens from state and logs. Never send raw secrets
# to the API and never write them to the JSONL file.
_SECRET_RE = re.compile(
    r"(?i)"
    r"(?:nace_sk_|sk-[A-Za-z0-9_-]{8,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"
    r"|AKIA[0-9A-Z]{16}|-----BEGIN[ A-Z]*PRIVATE KEY-----"
    r"|(?:api[_-]?key|access[_-]?token|secret|password|passwd|authorization)\s*[=:]\s*\S+)"
)

_SENSITIVE_PATH = re.compile(
    r"(?i)(?:^|[\\/])(?:\.env(?:\..+)?|\.npmrc|\.pypirc|credentials|\.netrc|"
    r"id_rsa|id_ed25519|id_ecdsa|\.kube[\\/]config|secrets?(?:\.[A-Za-z0-9]+)?)$"
)


def load_env() -> None:
    """Load a nearby .env if present. Never print its contents."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    candidates = []
    project = os.environ.get("CLAUDE_PROJECT_DIR")
    if project:
        candidates.append(Path(project) / ".env")
    candidates.extend((HERE / ".env", ROOT / ".env", Path.cwd() / ".env"))
    seen: set[Path] = set()
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in seen or not path.is_file():
            continue
        seen.add(resolved)
        load_dotenv(path, override=False)
        break


def lo_hi_timeout() -> tuple[float, float, float]:
    lo = float(os.environ.get("GATE_LO", DEFAULT_LO))
    hi = float(os.environ.get("GATE_HI", DEFAULT_HI))
    timeout = float(os.environ.get("GATE_TIMEOUT", DEFAULT_TIMEOUT))
    if lo < 0 or hi > 1 or lo >= hi:
        lo, hi = DEFAULT_LO, DEFAULT_HI
    if timeout <= 0:
        timeout = DEFAULT_TIMEOUT
    return lo, hi, timeout


def redact(text: str) -> str:
    return _SECRET_RE.sub("[REDACTED]", text)


def _looks_sensitive(path: str) -> bool:
    return bool(_SENSITIVE_PATH.search(path.strip()))


def summarize_input(tool_name: str, tool_input: Any) -> str:
    """One-line action summary for logs and the Drex state."""
    if not isinstance(tool_input, dict):
        return redact(str(tool_input))[:500]
    if tool_name == "Bash" or "command" in tool_input:
        return redact(str(tool_input.get("command") or "")).strip() or "(empty command)"
    path = tool_input.get("file_path") or tool_input.get("path") or ""
    if path:
        return f"{tool_name} {path}"
    return redact(json.dumps(tool_input, ensure_ascii=False)[:500])


def compact_tool_input(tool_name: str, tool_input: Any) -> Any:
    """Structured view of the call, with secrets and bulky content removed."""
    if not isinstance(tool_input, dict):
        return redact(str(tool_input))[:1000]
    out: dict[str, Any] = {}
    for key, value in tool_input.items():
        if key in {"content", "old_string", "new_string", "replace_all"}:
            continue
        if isinstance(value, str):
            out[key] = redact(value)[:2000]
        else:
            out[key] = value
    path = str(tool_input.get("file_path") or tool_input.get("path") or "")
    for blob_key in ("content", "old_string", "new_string"):
        if blob_key not in tool_input:
            continue
        blob = tool_input[blob_key]
        if not isinstance(blob, str):
            out[f"{blob_key}_type"] = type(blob).__name__
            continue
        if _looks_sensitive(path):
            out[f"{blob_key}_omitted"] = "sensitive_path"
            out[f"{blob_key}_chars"] = len(blob)
        else:
            out[f"{blob_key}_chars"] = len(blob)
            out[f"{blob_key}_preview"] = redact(blob[:240])
    return out


def build_state(payload: dict) -> dict:
    tool_name = str(payload.get("tool_name") or "unknown")
    tool_input = payload.get("tool_input") or {}
    return {
        "context": (
            "A coding agent (Claude Code) is about to execute a tool call on the "
            "developer's machine. Return calibrated odds that this single action "
            "is safe to auto-run under the approval policy in the question. "
            "Ordinary project writes belong in the middle of the scale; only "
            "destructive, secret-exposing, or untrusted-execution actions belong "
            "near zero."
        ),
        "tool_name": tool_name,
        "action": summarize_input(tool_name, tool_input),
        "tool_input": compact_tool_input(tool_name, tool_input),
        "cwd": payload.get("cwd") or "",
        "permission_mode": payload.get("permission_mode") or "",
        "scoring_guide": {
            "high_p_yes": "read-only inspection and project tests/linters",
            "medium_p_yes": "ordinary source edits, commit, non-force push, registry install",
            "low_p_yes": "destructive deletes, force-push, secret access, curl|bash",
        },
    }


def build_request(model: str, state: dict) -> dict:
    # Question shape matches the working client in drex_decide.py: a name-keyed
    # object, not an array. Response field is answers.<name>.noul = P(yes).
    return {
        "model": model,
        "state": state,
        "questions": {
            QUESTION_NAME: {
                "type": "noul",
                "instructions": QUESTION_INSTRUCTIONS,
            }
        },
    }


def hook_output(decision: str, reason: str) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }


def decide(p: float | None, lo: float, hi: float) -> tuple[str, str]:
    if p is None:
        return "ask", "Drex returned no probability; asking the user to be safe."
    if p >= hi:
        return (
            "allow",
            f"Drex P(safe to auto-run)={p:.3f} >= {hi:.2f}; auto-approved.",
        )
    if p >= lo:
        return (
            "ask",
            f"Drex is unsure (P(safe to auto-run)={p:.3f} is between {lo:.2f} "
            f"and {hi:.2f}). Ask the user before running this.",
        )
    return (
        "deny",
        f"Drex P(safe to auto-run)={p:.3f} < {lo:.2f}. Do not run this; "
        "pick a safer approach that does not destroy data, change remotes, "
        "execute untrusted code, or expose secrets.",
    )


def _safe_error_label(exc: BaseException) -> str:
    """Exception type only — never include response bodies or headers."""
    name = type(exc).__name__
    # requests.Timeout / ConnectTimeout / ReadTimeout
    if name.lower().endswith("timeout") or name in {"TimeoutError"}:
        return "timeout"
    if name in {"ConnectionError", "ConnectTimeout", "SSLError"}:
        return "network_error"
    return name


def call_drex(state: dict, model: str, timeout: float) -> tuple[float, float, str | None]:
    """Return (p_yes, latency_ms, error_label). error_label is set on failure."""
    import requests

    key = os.environ.get("NACE_API_KEY", "").strip()
    if not key or "..." in key or not key.startswith("nace_sk_"):
        return 0.0, 0.0, "missing_or_malformed_key"

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "X-Nace-Client": CLIENT_ID,
    }
    body = build_request(model, state)
    t0 = time.perf_counter()
    try:
        response = requests.post(API_URL, json=body, headers=headers, timeout=timeout)
    except BaseException as exc:  # noqa: BLE001 — fail open on anything
        latency = (time.perf_counter() - t0) * 1000
        return 0.0, round(latency, 1), _safe_error_label(exc)

    latency = (time.perf_counter() - t0) * 1000
    if response.status_code != 200:
        return 0.0, round(latency, 1), f"http_{response.status_code}"
    try:
        payload = response.json()
        p = payload["answers"][QUESTION_NAME]["noul"]
        p = float(p)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return 0.0, round(latency, 1), "bad_response"
    if not (0.0 <= p <= 1.0):
        return 0.0, round(latency, 1), "bad_response"
    return p, round(latency, 1), None


def log_path() -> Path:
    raw = os.environ.get("GATE_LOG")
    return Path(raw) if raw else DEFAULT_LOG


def write_log(record: dict) -> None:
    path = log_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def emit(decision: str, reason: str) -> int:
    json.dump(hook_output(decision, reason), sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    sys.stdout.flush()
    return 0


def main() -> int:
    load_env()
    lo, hi, timeout = lo_hi_timeout()
    model = os.environ.get("DREX_MODEL", PREFERRED_MODEL)
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
        if not isinstance(payload, dict):
            raise ValueError("hook payload must be a JSON object")
    except (json.JSONDecodeError, ValueError):
        write_log({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": None,
            "command": None,
            "p_safe": None,
            "decision": "ask",
            "latency_ms": 0.0,
            "error": "invalid_hook_json",
        })
        return emit("ask", "Drex gate failed open (invalid hook JSON); asking the user.")

    tool_name = str(payload.get("tool_name") or "unknown")
    tool_input = payload.get("tool_input") or {}
    command = summarize_input(tool_name, tool_input)
    state = build_state(payload)
    p, latency, error = call_drex(state, model, timeout)
    if error:
        decision, reason = (
            "ask",
            f"Drex gate failed open ({error}); asking the user.",
        )
        p_log: float | None = None
    else:
        decision, reason = decide(p, lo, hi)
        p_log = p

    write_log({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "command": command,
        "p_safe": p_log,
        "decision": decision,
        "latency_ms": latency,
        "model": model,
        "lo": lo,
        "hi": hi,
        **({"error": error} if error else {}),
    })
    return emit(decision, reason)


if __name__ == "__main__":
    sys.exit(main())
