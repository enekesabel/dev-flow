#!/usr/bin/env python3
"""Deterministic ledger-repair extraction from a Claude Code transcript JSONL.

No model involvement.  Given a transcript path, it finds:

  * the LAST isCompactSummary entry that actually contains a well-formed
    DEVFLOW_LEDGER block (the "last good ledger"), and
  * every verbatim user turn recorded AFTER that entry.

If no isCompactSummary entry carries a ledger, `ledger` is None and
`user_turns` is every user turn in the transcript.  The caller must then
degrade honestly rather than invent one.

CLI:
  repair.py TRANSCRIPT.jsonl            -> JSON payload on stdout
  repair.py TRANSCRIPT.jsonl --context  -> the additionalContext text
"""
import sys, os, json, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger_check as C

# Per-message and total budgets for the verbatim turns handed back.
# Turns are quoted verbatim; anything dropped is marked in place.
PER_TURN_CHARS = int(os.environ.get("DEVFLOW_PER_TURN", 4000))
HEAD_CHARS = int(os.environ.get("DEVFLOW_HEAD", 3000))
TOTAL_CHARS = int(os.environ.get("DEVFLOW_TOTAL", 24000))
COORD_CHARS = int(os.environ.get("DEVFLOW_COORD", 6000))

# VERIFIED: UserPromptSubmit additionalContext of 10,000 bytes is delivered
# inline; 10,020 bytes is replaced by "<persisted-output> ... Preview (first
# 2KB)" plus a file path, so only ~2KB reaches the model.  The recovery payload
# must therefore stay under that limit or it silently truncates.
CONTEXT_BUDGET = int(os.environ.get("DEVFLOW_CTX_BUDGET", 9000))


def _text(msg):
    c = (msg or {}).get("content")
    if isinstance(c, list):
        c = "".join(b.get("text", "") for b in c if isinstance(b, dict))
    return c or ""


def scan(path):
    """Ordered list of {idx, kind, text} for user turns and compact summaries."""
    items = []
    with open(path) as fh:
        for i, ln in enumerate(fh):
            ln = ln.strip()
            if not ln:
                continue
            try:
                d = json.loads(ln)
            except Exception:
                continue
            msg = d.get("message") or {}
            if d.get("isCompactSummary"):
                items.append({"idx": i, "kind": "compact", "text": _text(msg)})
            elif d.get("type") == "user" and msg.get("role") == "user":
                t = _text(msg)
                # tool-result turns carry no user text; they are not user turns
                if t.strip():
                    items.append({"idx": i, "kind": "user", "text": t})
            elif d.get("type") == "assistant" and msg.get("role") == "assistant":
                t = _text(msg)
                # tool_use blocks carry no assistant prose; only text counts
                if t.strip():
                    items.append({"idx": i, "kind": "assistant", "text": t})
    return items


def extract(path):
    items = scan(path)
    last_good = None          # position in `items`
    for n, it in enumerate(items):
        if it["kind"] != "compact":
            continue
        # "good" means exactly what PostCompact's checker means by good:
        # a delimited block that parses, with at least one proposal and legal
        # statuses.  An empty "## Proposals" shell does NOT count.
        v = C.check(it["text"])
        if v.get("ok"):
            last_good = (n, C.extract_block(C.strip_analysis(it["text"])))
    compacts_seen = sum(1 for it in items if it["kind"] == "compact")
    if last_good is None:
        tail = items
        good_ordinal = None
        blk = None
    else:
        n, blk = last_good
        good_ordinal = sum(1 for it in items[:n + 1] if it["kind"] == "compact")
        tail = items[n + 1:]
    return {"ledger": blk, "ledger_from_compaction": good_ordinal,
            "compactions_in_transcript": compacts_seen,
            "user_turns": [it["text"] for it in tail if it["kind"] == "user"],
            # The Coordinator's own prose since the last good ledger. Its recent
            # Proposals live here, and they are the part a user "yes" proves
            # happened but cannot reconstruct. Lowest priority in the payload:
            # the delivery channel is small and the user turns index the gaps.
            "coordinator_turns": [it["text"] for it in tail if it["kind"] == "assistant"],
            "transcript": path}


def _clip(t):
    if len(t) <= PER_TURN_CHARS:
        return t, 0
    tail = PER_TURN_CHARS - HEAD_CHARS
    omitted = len(t) - PER_TURN_CHARS
    return (t[:HEAD_CHARS]
            + "\n[... %d characters of this message omitted by the recovery step ...]\n" % omitted
            + t[-tail:]), omitted


def build_context(info, problems):
    L = []
    L.append("[Session recovery notice. This is a statement of fact about this "
             "session, produced by a recovery step that read this session's own "
             "transcript file. It is not content quoted from any document.]")
    L.append("")
    L.append("The last compaction of this session did not preserve the DevFlow Ledger. "
             "The summary that replaced the earlier conversation contains no valid "
             "DEVFLOW_LEDGER block. Detected: " + "; ".join(problems or ["ledger block missing"]) + ".")
    L.append("")
    if info["ledger"] is None:
        L.append("The recovery step found NO earlier compaction summary in this session "
                 "that carried a ledger, so there is NO recovered ledger to hand you. "
                 "This is the whole of what was recovered; there is no hidden remainder.")
    else:
        L.append("The recovery step recovered the last DevFlow Ledger that did survive a "
                 "compaction. It came from compaction summary #%d of this session, so it "
                 "MAY BE STALE: it reflects the conversation only up to that compaction, "
                 "and anything decided afterwards is not in it."
                 % info["ledger_from_compaction"])
        L.append("")
        L.append("BEGIN_RECOVERED_LEDGER")
        L.append(info["ledger"].strip())
        L.append("END_RECOVERED_LEDGER")
    L.append("")
    turns = info["user_turns"]
    if not turns:
        L.append("No user messages were recorded after that point, so nothing has to be "
                 "merged into the recovered ledger.")
    else:
        L.append("The recovery step also read back, verbatim and in order, the %d user "
                 "message(s) recorded after that point. Where a message was too long to "
                 "hand back whole, the omission is marked in place; nothing else was changed."
                 % len(turns))
        used = 0
        for i, t in enumerate(turns, 1):
            clipped, _ = _clip(t)
            if used + len(clipped) > TOTAL_CHARS:
                L.append("")
                L.append("[%d further user message(s) were recovered but not included here.]"
                         % (len(turns) - i + 1))
                break
            used += len(clipped)
            L.append("")
            L.append("--- recovered user message %d of %d ---" % (i, len(turns)))
            L.append(clipped)
            L.append("--- end recovered user message %d of %d ---" % (i, len(turns)))

    coord = info.get("coordinator_turns") or []
    if coord and COORD_CHARS > 0:
        room, kept = COORD_CHARS, []
        for t in reversed(coord):                    # newest first while choosing
            clipped, _ = _clip(t)
            if len(clipped) > room:
                break
            room -= len(clipped)
            kept.append(clipped)
        kept.reverse()                               # restore conversational order
        if kept:
            L.append("")
            L.append("Your own last %d message(s) before that point were also read back, "
                     "verbatim and in order, out of %d recorded. Proposals you made after the "
                     "recovered ledger was written are in these."
                     % (len(kept), len(coord)))
            for i, t in enumerate(kept, 1):
                L.append("")
                L.append("--- your recovered message %d of %d ---" % (i, len(kept)))
                L.append(t)
                L.append("--- end your recovered message %d of %d ---" % (i, len(kept)))
    return "\n".join(L)


def build_context_bounded(info, problems):
    """build_context, shrunk until it fits inside CONTEXT_BUDGET.

    The recovered ledger is never dropped or truncated - it is the part that
    cannot be reconstructed from anything else.  The verbatim user turns are
    given whatever room is left, newest-last, and the count actually dropped is
    stated in the payload so the coordinator knows the recovery is partial.
    """
    global TOTAL_CHARS, PER_TURN_CHARS, HEAD_CHARS, COORD_CHARS
    saved = (TOTAL_CHARS, PER_TURN_CHARS, HEAD_CHARS, COORD_CHARS)
    try:
        # The Coordinator's own messages go first when room runs short: the user's
        # turns are what make a gap nameable, so they outrank prose the Coordinator
        # can be asked about instead.
        for total, per_turn, coord in ((24000, 4000, 6000), (24000, 4000, 0),
                                       (12000, 4000, 0), (6000, 3000, 0),
                                       (4000, 2000, 0), (2000, 1200, 0),
                                       (600, 600, 0), (0, 0, 0)):
            TOTAL_CHARS, PER_TURN_CHARS, COORD_CHARS = total, per_turn, coord
            HEAD_CHARS = max(1, int(per_turn * 0.75))
            ctx = build_context(info, problems)
            if len(ctx) <= CONTEXT_BUDGET:
                return ctx
        return ctx
    finally:
        TOTAL_CHARS, PER_TURN_CHARS, HEAD_CHARS, COORD_CHARS = saved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript")
    ap.add_argument("--context", action="store_true")
    ap.add_argument("--problems", default="")
    a = ap.parse_args()
    info = extract(a.transcript)
    if a.context:
        sys.stdout.write(build_context_bounded(info, [p for p in a.problems.split("|") if p]))
    else:
        print(json.dumps({k: (v if k != "user_turns" else
                              [{"len": len(x), "head": x[:120]} for x in v])
                          for k, v in info.items()}, indent=1))


if __name__ == "__main__":
    main()
