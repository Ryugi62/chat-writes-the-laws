import json
import subprocess
from typing import Optional, Tuple


def extract_thread_id(jsonl: str) -> Optional[str]:
    for line in jsonl.splitlines():
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if isinstance(o, dict) and o.get("type") == "thread.started":
            return o.get("thread_id")
    return None


def run_codex(repo: str, prompt: str, timeout: int = 280, effort: str = "") -> Tuple[int, Optional[str], str]:
    """codex exec in the repo (workspace-write sandbox). Returns (exit, session id, raw jsonl)."""
    cmd = ["codex", "exec", "--json", "--sandbox", "workspace-write", "-C", repo]
    if effort:
        cmd += ["-c", 'model_reasoning_effort="%s"' % effort]
    p = subprocess.run(
        cmd + [prompt],
        capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL,
    )
    return p.returncode, extract_thread_id(p.stdout), p.stdout
