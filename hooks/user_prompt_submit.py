#!/usr/bin/env python3
"""UserPromptSubmit: hand the staged recovery to the Coordinator, once.

This carries a fact. The duty to act on it lives in the Coordinator's agent
definition, because a hook cannot deliver authority.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import hook_common as H   # noqa: E402


def main():
    data = H.read_input()
    path = H.flag_path(data.get("session_id"))
    if not os.path.exists(path):
        return

    with open(path) as fh:
        payload = fh.read()

    if payload.strip():
        H.emit({"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": H.fit_to_delivery_limit(payload)}})
        sys.stdout.flush()

    # Cleared only after the payload is out. Clearing first would lose the whole
    # recovery if anything failed between the two, and it is unrecoverable.
    # Delivered once: left in place it would repeat the notice every turn.
    try:
        os.remove(path)
    except OSError:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
