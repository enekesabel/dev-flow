"""Shared plumbing for the DevFlow hooks.

A hook that raises wedges the thing it hooks, so every entry point here reads
tolerantly and fails open.
"""
import json
import os
import sys
import tempfile

# VERIFIED: UserPromptSubmit additionalContext of 10,000 bytes is delivered
# inline. At 10,020 it is replaced by a "<persisted-output>" stub with a 2KB
# preview, so a payload over the limit mostly does not reach the model.
DELIVERY_LIMIT = 10000


def read_input():
    try:
        return json.loads(sys.stdin.read() or "{}")
    except Exception:
        return {}


def state_dir():
    d = os.environ.get("DEVFLOW_STATE_DIR") or os.path.join(
        tempfile.gettempdir(), "devflow-state")
    os.makedirs(d, exist_ok=True)
    return d


def flag_path(session_id):
    safe = "".join(c for c in str(session_id or "session") if c.isalnum() or c in "-_")
    return os.path.join(state_dir(), (safe or "session") + ".recovery")


def emit(obj):
    sys.stdout.write(json.dumps(obj))


def fit_to_delivery_limit(text):
    """Trim to what the harness will actually hand the model, marking the cut."""
    data = (text or "").encode("utf-8")
    if len(data) <= DELIVERY_LIMIT:
        return text
    note = b"\n\n[Recovery payload truncated to fit the delivery limit.]"
    return (data[:DELIVERY_LIMIT - len(note)].decode("utf-8", "ignore")
            + note.decode())
