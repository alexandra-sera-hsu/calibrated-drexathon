#!/usr/bin/env python3
"""Pipe each test case through gate.py and print a results table.

    python claude_gate/run_tests.py

Uses the live Drex API (NACE_API_KEY from the repo .env). Never prints keys.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GATE = HERE / "gate.py"
CASES = HERE / "test_cases.json"


def load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = ROOT / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)


def has_key() -> bool:
    load_env()
    v = os.environ.get("NACE_API_KEY", "").strip()
    return bool(v) and "..." not in v and v.startswith("nace_sk_")


def hook_payload(case: dict) -> dict:
    return {
        "session_id": "gate-test",
        "cwd": case.get("cwd") or str(ROOT),
        "permission_mode": "default",
        "hook_event_name": "PreToolUse",
        "tool_name": case["tool_name"],
        "tool_input": case.get("tool_input") or {},
        "tool_use_id": f"test_{case['id']}",
    }


def run_case(case: dict, log_path: Path, python: str) -> dict:
    env = os.environ.copy()
    env["GATE_LOG"] = str(log_path)
    # Make sure a leftover key from the parent env still works; gate.py also loads .env.
    before = log_path.stat().st_size if log_path.exists() else 0
    proc = subprocess.run(
        [python, str(GATE)],
        input=json.dumps(hook_payload(case)),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(ROOT),
        timeout=20,
    )
    out = {"id": case["id"], "tool": case["tool_name"]}
    action = ""
    tool_input = case.get("tool_input") or {}
    if "command" in tool_input:
        action = tool_input["command"]
    elif "file_path" in tool_input:
        action = f"{case['tool_name']} {tool_input['file_path']}"
    else:
        action = case["id"]
    out["command"] = action
    out["exit_code"] = proc.returncode
    out["stderr"] = (proc.stderr or "").strip()
    try:
        hook = json.loads(proc.stdout)
        specific = hook["hookSpecificOutput"]
        out["decision"] = specific["permissionDecision"]
        out["reason"] = specific.get("permissionDecisionReason", "")
        out["hook_event"] = specific.get("hookEventName")
    except (json.JSONDecodeError, KeyError, TypeError):
        out["decision"] = "PARSE_ERROR"
        out["reason"] = "gate.py stdout was not valid PreToolUse JSON"
        out["hook_event"] = None

    record = {}
    if log_path.exists():
        with log_path.open() as fh:
            fh.seek(before)
            lines = [ln for ln in fh.read().splitlines() if ln.strip()]
        if lines:
            try:
                record = json.loads(lines[-1])
            except json.JSONDecodeError:
                record = {}
    out["p_safe"] = record.get("p_safe")
    out["latency_ms"] = record.get("latency_ms")
    out["error"] = record.get("error")
    expected = case.get("expected") or []
    out["expected"] = expected
    out["ok"] = out["decision"] in expected if expected else out["decision"] in {"allow", "ask", "deny"}
    return out


def print_table(rows: list[dict]) -> None:
    try:
        from rich.console import Console
        from rich.table import Table

        con = Console()
        table = Table(title="Claude Code System 1 / System 2 gate — live Drex")
        table.add_column("command", overflow="fold")
        table.add_column("P(safe)", justify="right")
        table.add_column("decision", justify="center")
        table.add_column("expected")
        table.add_column("latency", justify="right")
        table.add_column("match", justify="center")
        for row in rows:
            p = row["p_safe"]
            p_s = "—" if p is None else f"{p:.3f}"
            lat = row["latency_ms"]
            lat_s = "—" if lat is None else f"{lat:.0f} ms"
            mark = "ok" if row["ok"] else "MISS"
            decision = row["decision"]
            if row.get("error"):
                decision = f"{decision} ({row['error']})"
            table.add_row(
                row["command"],
                p_s,
                decision,
                "|".join(row["expected"]),
                lat_s,
                mark,
            )
        con.print(table)
    except ImportError:
        print(f"{'command':<55} {'P(safe)':>8} {'decision':<18} {'expected':<16} {'latency':>10} match")
        print("-" * 120)
        for row in rows:
            p = row["p_safe"]
            p_s = "—" if p is None else f"{p:.3f}"
            lat = row["latency_ms"]
            lat_s = "—" if lat is None else f"{lat:.0f}ms"
            mark = "ok" if row["ok"] else "MISS"
            print(
                f"{row['command'][:55]:<55} {p_s:>8} {row['decision']:<18} "
                f"{'|'.join(row['expected']):<16} {lat_s:>10} {mark}"
            )


def main() -> int:
    load_env()
    if not has_key():
        print("NACE_API_KEY is not set or is malformed. Add it to .env (gitignored) and retry.", file=sys.stderr)
        return 2
    python = sys.executable
    cases = json.loads(CASES.read_text())
    with tempfile.TemporaryDirectory() as tmp:
        log_path = Path(tmp) / "decisions.jsonl"
        rows = [run_case(case, log_path, python) for case in cases]
    print_table(rows)
    misses = [row for row in rows if not row["ok"]]
    errors = [row for row in rows if row.get("error")]
    parse = [row for row in rows if row["decision"] == "PARSE_ERROR"]
    print()
    print(f"{len(rows)} cases, {len(rows) - len(misses)} matched expected band, "
          f"{len(misses)} missed, {len(errors)} API/gate errors, {len(parse)} parse errors.")
    if misses:
        print("Misses:")
        for row in misses:
            print(f"  - {row['id']}: decision={row['decision']} P={row['p_safe']} expected={row['expected']}")
            print(f"    {row.get('reason') or ''}")
    return 1 if misses or parse else 0


if __name__ == "__main__":
    sys.exit(main())
