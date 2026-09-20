#!/usr/bin/env python3
"""PreToolUse on the Agent tool: refuse a dispatch that carries no Brief.

The hook cannot write the Brief. A Brief is Plan Alignment output scoped to the
task, and that lives in the Coordinator's context, not anywhere a hook can read.
So the Coordinator composes it and this hook holds it to that.

Denying is the point: it returns the dispatch to the Coordinator with the reason,
and the Coordinator rewrites it with the Brief attached.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import hook_common as H   # noqa: E402

AGENT_TOOLS = ("Agent", "Task")
MARKER = "## Brief"

REASON = (
    "This dispatch carries no Brief, so the Worker would start without knowing what "
    "you and the user agreed. Add a '## Brief' section to the prompt holding every "
    "Accepted and Rejected Proposal that bears on this task, at the Specificity the "
    "user established, and what is explicitly out of scope. Leave out identifiers and "
    "Attention Surfaces. Then dispatch again."
)


def main():
    data = H.read_input()
    if data.get("tool_name") not in AGENT_TOOLS:
        return

    tool_input = data.get("tool_input") or {}
    prompt = tool_input.get("prompt") or ""
    if MARKER.lower() in prompt.lower():
        return

    H.emit({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": REASON}})


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Failing open lets an unbriefed dispatch through, which is better than
        # wedging every dispatch in the session.
        pass
