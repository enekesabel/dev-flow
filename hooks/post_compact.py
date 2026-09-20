#!/usr/bin/env python3
"""PostCompact: check that the Ledger survived, and stage a recovery if it did not.

PostCompact cannot return additionalContext, so this hook cannot tell the
Coordinator anything. It writes a flag instead, which user_prompt_submit.py
delivers on the next turn.

It also cannot repair in the same cycle: SessionStart(compact) has already run
by the time this fires, about 40ms earlier.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import hook_common as H          # noqa: E402
import ledger_check as check     # noqa: E402
import ledger_repair as repair   # noqa: E402


def previous_ledger(transcript_path, current_summary):
    """The last good Ledger recorded BEFORE this compaction.

    The current summary may already be in the transcript, so it is excluded by
    value: comparing a Ledger against itself would report no drops.
    """
    if not transcript_path or not os.path.exists(transcript_path):
        return None
    prev = None
    for text in check.compact_summaries_from_transcript(transcript_path):
        if text == current_summary:
            continue
        if check.check(text).get("ok"):
            prev = check.extract_block(check.strip_analysis(text))
    return prev


def main():
    data = H.read_input()
    summary = data.get("compact_summary")
    if not summary:
        return

    transcript = data.get("transcript_path")
    verdict = check.check(summary, prev_block=previous_ledger(transcript, summary))
    if verdict.get("ok"):
        return

    info = repair.extract(transcript) if transcript and os.path.exists(transcript) else {
        "ledger": None, "ledger_from_compaction": None,
        "compactions_in_transcript": 0, "user_turns": [], "coordinator_turns": []}
    payload = repair.build_context_bounded(info, verdict.get("problems") or [])

    with open(H.flag_path(data.get("session_id")), "w") as fh:
        fh.write(payload)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # A hook that dies here must not take the session with it.
        pass
