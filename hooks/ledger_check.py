#!/usr/bin/env python3
"""Deterministic DevFlow ledger checker for compaction summaries.

Usage:
  checker.py --stdin-summary [--prev-ledger FILE]
  checker.py SUMMARY_FILE [--prev-ledger FILE]
  checker.py --transcript TRANSCRIPT.jsonl        # list isCompactSummary entries
  checker.py --prev-from-transcript T.jsonl [--index N]   # print previous ledger block
"""
import sys, re, json, argparse

LEGAL_STATUS = {"Open", "Accepted", "Rejected", "Superseded", "Outdated"}
BEGIN = "BEGIN_DEVFLOW_LEDGER"
END = "END_DEVFLOW_LEDGER"


def strip_analysis(raw: str) -> str:
    """Reproduce what the harness actually shows the model.

    VERIFIED against transcript isCompactSummary entries:
      * a WELL-FORMED <analysis>...</analysis> section is removed;
      * the <summary>/</summary> tags themselves are removed;
      * everything else is kept - including text that follows </summary>;
      * an UNTERMINATED <analysis> (no closing tag) is NOT stripped at all:
        the whole raw output, analysis included, reaches the model.
    """
    if raw is None:
        return ""
    m = re.search(r"</analysis\s*>", raw, re.I)
    body = raw[m.end():] if m else raw
    return re.sub(r"</?summary\s*>", "", body, flags=re.I)


def summary_section_only(raw: str) -> str:
    """Literal <summary>...</summary> contents (strict mode)."""
    m = re.search(r"<summary>(.*?)</summary>", raw or "", re.S | re.I)
    return m.group(1) if m else ""


def in_summary_section(raw: str) -> bool:
    """True if the first standalone BEGIN sentinel sits inside <summary>...</summary>."""
    if not raw:
        return False
    b = raw.find(BEGIN)
    o = raw.lower().find("<summary>")
    c = raw.lower().find("</summary>")
    if b < 0 or o < 0 or c < 0:
        return False
    return o < b < c


def _sentinel_lines(text, word):
    """Line indices where `word` stands alone on its own line (the schema form).

    A sentinel merely NAMED inside prose does not open or close a block.
    """
    out = []
    for n, ln in enumerate(text.splitlines()):
        if re.fullmatch(r"\s*[`*#>\-]*\s*%s\s*[`*]*\s*" % word, ln):
            out.append(n)
    return out


def extract_block(summary_text: str):
    """Return the ledger block text between standalone sentinel lines, or None."""
    lines = summary_text.splitlines()
    begins = _sentinel_lines(summary_text, BEGIN)
    ends = _sentinel_lines(summary_text, END)
    for b in begins:
        for e in ends:
            if e > b:
                return "\n".join(lines[b + 1:e])
    return None


def parse_block(block: str):
    """Parse a ledger block into areas and proposals.

    Entries are bullet lines that introduce an ID; the attributes that follow
    (Origin/Area/Status/Content) belong to the most recent entry.
    """
    areas, props, order = {}, {}, []
    cur = None
    for line in block.splitlines():
        s = line.strip()
        if not s:
            continue
        m = re.match(r"^[-*+]?\s*\**\s*(A-\d{3})\b", s)
        if m:
            cur = ("A", m.group(1))
            order.append(cur)
            areas.setdefault(m.group(1), {"count": 0, "text": s})
            areas[m.group(1)]["count"] += 1
            continue
        m = re.match(r"^[-*+]?\s*\**\s*(P-\d{3})\b", s)
        if m:
            cur = ("P", m.group(1))
            order.append(cur)
            props.setdefault(m.group(1), {"count": 0, "text": s})
            props[m.group(1)]["count"] += 1
            continue
        m = re.match(r"^[-*+]?\s*\**\s*(Origin|Area|Status|Content)\**\s*:\s*(.*)$", s, re.I)
        if m and cur:
            key = m.group(1).lower()
            val = m.group(2).strip().strip("*").strip()
            tgt = areas[cur[1]] if cur[0] == "A" else props[cur[1]]
            tgt.setdefault(key, val)
    return areas, props


def check(raw_summary: str, prev_block: str = None, strict_summary_only: bool = False):
    problems = []
    summary_text = (summary_section_only(raw_summary) if strict_summary_only
                    else strip_analysis(raw_summary))
    block = extract_block(summary_text)
    if block is None:
        # distinguish "only in analysis" from "absent entirely"
        if BEGIN in summary_text:
            problems.append("sentinel named in prose but no delimited block")
        elif raw_summary and BEGIN in raw_summary:
            problems.append("sentinel block present only outside <summary>")
        else:
            problems.append("sentinel block missing")
        return {"ok": False, "problems": problems, "areas": [], "proposals": {},
                "block_present": False}

    areas, props = parse_block(block)

    if not props:
        problems.append("no P-### entry found in block")

    for pid in sorted(props):
        st = props[pid].get("status")
        if st is None:
            problems.append("%s has no Status" % pid)
        else:
            m = re.match(r"^\**\s*(Open|Accepted|Rejected|Superseded|Outdated)\b", st.strip(), re.I)
            if not m:
                problems.append("%s has illegal Status %r" % (pid, st))
            else:
                props[pid]["status_norm"] = m.group(1).capitalize()
        ar = props[pid].get("area")
        if ar is None:
            problems.append("%s has no Area" % pid)
        else:
            refs = re.findall(r"A-\d{3}", ar)
            if not refs:
                problems.append("%s Area %r contains no A-### reference" % (pid, ar))
            for r in refs:
                if r not in areas:
                    problems.append("%s references unknown area %s" % (pid, r))

    for pid, v in sorted(props.items()):
        if v["count"] > 1:
            problems.append("duplicate proposal id %s (%d times)" % (pid, v["count"]))
    for aid, v in sorted(areas.items()):
        if v["count"] > 1:
            problems.append("duplicate area id %s (%d times)" % (aid, v["count"]))

    dropped = []
    if prev_block:
        _, prev_props = parse_block(prev_block)
        dropped = sorted(set(prev_props) - set(props))
        for pid in dropped:
            problems.append("previously-present %s disappeared" % pid)

    return {"ok": not problems, "problems": problems,
            "in_summary_section": in_summary_section(raw_summary),
            "areas": sorted(areas),
            "proposals": {p: props[p].get("status_norm") or props[p].get("status") for p in sorted(props)},
            "block_present": True, "dropped": dropped}


def compact_summaries_from_transcript(path):
    out = []
    with open(path) as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                d = json.loads(ln)
            except Exception:
                continue
            if d.get("isCompactSummary"):
                msg = d.get("message") or {}
                c = msg.get("content")
                if isinstance(c, list):
                    c = "".join(b.get("text", "") for b in c if isinstance(b, dict))
                out.append(c or "")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("summary_file", nargs="?")
    ap.add_argument("--stdin-summary", action="store_true")
    ap.add_argument("--prev-ledger")
    ap.add_argument("--transcript")
    ap.add_argument("--prev-from-transcript")
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--strict-summary-only", action="store_true",
                    help="look only inside <summary>..</summary> (the literal spec); "
                         "default mirrors what the harness actually shows the model")
    a = ap.parse_args()

    if a.transcript:
        cs = compact_summaries_from_transcript(a.transcript)
        print(json.dumps({"count": len(cs), "lengths": [len(x) for x in cs],
                          "has_sentinel": [BEGIN in x for x in cs]}, indent=1))
        return
    if a.prev_from_transcript:
        cs = compact_summaries_from_transcript(a.prev_from_transcript)
        b = extract_block(strip_analysis(cs[a.index])) if cs else None
        # Sentinels stand alone on their own line, or the block cannot be re-parsed.
        sys.stdout.write("%s\n%s\n%s\n" % (BEGIN, b, END) if b else "")
        return

    raw = sys.stdin.read() if a.stdin_summary else open(a.summary_file).read()
    prev = open(a.prev_ledger).read() if a.prev_ledger else None
    print(json.dumps(check(raw, prev, a.strict_summary_only), indent=1))


if __name__ == "__main__":
    main()
