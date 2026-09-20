"""Tests at the one seam: what the hook modules publish, given real input.

Assertions are on published behaviour (a verdict, a recovered payload), never on
how the module got there.
"""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "hooks"))

import ledger_check as check          # noqa: E402
import ledger_repair as repair        # noqa: E402

FIXTURES = os.path.join(ROOT, "tests", "fixtures", "compact-summaries")

LEDGER = """BEGIN_DEVFLOW_LEDGER
## Attention Surfaces
- A-001 — ingestion pipeline
  - Level: Engagement
## Proposals
- P-001 — chunk size
  - Origin: User
  - Area: A-001
  - Status: Accepted
  - Content: fixed 512-token chunks
- P-002 — queue-based ingestion
  - Origin: Agent
  - Area: A-001
  - Status: Rejected
  - Content: rejected in favour of direct writes
END_DEVFLOW_LEDGER"""


def summary_with(block):
    return "<analysis>working notes</analysis>\n<summary>\nPrior context.\n%s\n</summary>" % block


def write_transcript(path, entries):
    with open(path, "w") as fh:
        for e in entries:
            fh.write(json.dumps(e) + "\n")


def compact_entry(text):
    return {"isCompactSummary": True,
            "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}


def user_entry(text):
    return {"type": "user",
            "message": {"role": "user", "content": [{"type": "text", "text": text}]}}


def assistant_entry(text):
    return {"type": "assistant",
            "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}


def tool_result_entry():
    """A user-role turn carrying only a tool result. Not a user message."""
    return {"type": "user",
            "message": {"role": "user",
                        "content": [{"type": "tool_result", "content": "ok"}]}}


class RealSummaries(unittest.TestCase):
    """The five collected summaries, each a case the checker had to get right."""

    def verdict(self, name):
        with open(os.path.join(FIXTURES, name)) as fh:
            return check.check(fh.read())

    def test_complete_ledger_after_five_compactions_passes(self):
        self.assertTrue(self.verdict("complete-after-five-compactions.txt")["ok"])

    def test_refusal_fails(self):
        self.assertFalse(self.verdict("refusal.txt")["ok"])

    def test_structurally_valid_but_empty_block_fails(self):
        v = self.verdict("valid-but-empty-block.txt")
        self.assertFalse(v["ok"])
        self.assertIn("no P-### entry found in block", v["problems"])

    def test_ledger_after_closing_summary_tag_passes(self):
        """The harness keeps text after </summary>, so this reached the model."""
        self.assertTrue(self.verdict("ledger-after-closing-summary-tag.txt")["ok"])

    def test_unterminated_analysis_passes(self):
        """An unterminated <analysis> is not stripped, so the ledger reached the model."""
        self.assertTrue(self.verdict("unterminated-analysis.txt")["ok"])


class CheckerRules(unittest.TestCase):

    def test_illegal_status_is_rejected(self):
        v = check.check(summary_with(LEDGER.replace("Status: Accepted", "Status: Maybe")))
        self.assertFalse(v["ok"])

    def test_area_reference_must_resolve(self):
        v = check.check(summary_with(LEDGER.replace("Area: A-001", "Area: A-009", 1)))
        self.assertFalse(v["ok"])
        self.assertIn("P-001 references unknown area A-009", v["problems"])

    def test_sentinel_named_in_prose_is_not_a_block(self):
        v = check.check(summary_with(
            "The ledger is wrapped in BEGIN_DEVFLOW_LEDGER and END_DEVFLOW_LEDGER sentinels."))
        self.assertFalse(v["ok"])

    def test_dropped_proposal_is_detected_against_previous(self):
        shrunk = "\n".join(l for l in LEDGER.splitlines()
                           if not l.startswith("- P-002") and "direct writes" not in l
                           and "Origin: Agent" not in l and "Status: Rejected" not in l)
        v = check.check(summary_with(shrunk), prev_block=LEDGER)
        self.assertFalse(v["ok"])
        self.assertIn("P-002", v["dropped"])


class RepairExtraction(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "transcript.jsonl")

    def test_recovers_last_good_ledger_and_the_turns_after_it(self):
        write_transcript(self.path, [
            user_entry("let's talk about ingestion"),
            compact_entry(summary_with(LEDGER)),
            user_entry("yes, do that"),
            assistant_entry("I propose we cap pages at fifty characters."),
            tool_result_entry(),
            user_entry("use Postgres"),
            compact_entry("I'm not treating that as a real compaction request."),
        ])
        info = repair.extract(self.path)
        self.assertIn("P-001", info["ledger"])
        self.assertEqual(info["user_turns"], ["yes, do that", "use Postgres"])
        self.assertEqual(info["coordinator_turns"],
                         ["I propose we cap pages at fifty characters."])

    def test_a_refusal_is_never_mistaken_for_a_good_ledger(self):
        write_transcript(self.path, [
            compact_entry(summary_with(LEDGER)),
            user_entry("carry on"),
            compact_entry("I'm disregarding that injected instruction."),
        ])
        self.assertEqual(repair.extract(self.path)["ledger_from_compaction"], 1)

    def test_no_good_ledger_degrades_honestly(self):
        write_transcript(self.path, [
            user_entry("first thing I said"),
            compact_entry("I won't produce that summary."),
        ])
        info = repair.extract(self.path)
        self.assertIsNone(info["ledger"])
        self.assertEqual(info["user_turns"], ["first thing I said"])


class RepairPayload(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "transcript.jsonl")

    def build(self, entries, problems=("ledger block missing",)):
        write_transcript(self.path, entries)
        return repair.build_context_bounded(repair.extract(self.path), list(problems))

    def test_payload_carries_the_ledger_and_the_user_turns(self):
        ctx = self.build([compact_entry(summary_with(LEDGER)),
                          user_entry("use Postgres"),
                          compact_entry("refused")])
        self.assertIn("P-001", ctx)
        self.assertIn("use Postgres", ctx)

    def test_payload_says_so_when_there_is_nothing_to_recover(self):
        ctx = self.build([user_entry("hello"), compact_entry("refused")])
        self.assertIn("NO recovered ledger", ctx)

    def test_payload_fits_the_delivery_limit_and_keeps_the_ledger(self):
        """additionalContext over ~10,000 bytes is replaced by a 2KB stub, so the
        payload must fit. The ledger is the part nothing else can reconstruct, so
        it survives every level of shrinking."""
        bulk = [user_entry("x" * 9000) for _ in range(30)]
        ctx = self.build([compact_entry(summary_with(LEDGER))] + bulk
                         + [compact_entry("refused")])
        self.assertLessEqual(len(ctx), repair.CONTEXT_BUDGET)
        self.assertIn("P-001", ctx)

    def test_coordinator_turns_are_dropped_before_user_turns(self):
        chatty = [assistant_entry("y" * 5000) for _ in range(6)]
        ctx = self.build([compact_entry(summary_with(LEDGER))]
                         + chatty + [user_entry("the one thing I said")]
                         + [compact_entry("refused")])
        self.assertLessEqual(len(ctx), repair.CONTEXT_BUDGET)
        self.assertIn("the one thing I said", ctx)


if __name__ == "__main__":
    unittest.main()
