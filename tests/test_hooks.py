"""Tests at the hook process boundary: JSON on stdin, JSON on stdout.

These run the hook scripts exactly as Claude Code runs them, so what is under
test is the shipped contract and not an internal function.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "hooks")

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
END_DEVFLOW_LEDGER"""


def summary_with(block):
    return "<analysis>notes</analysis>\n<summary>\nPrior context.\n%s\n</summary>" % block


class HookRun(unittest.TestCase):
    """Runs a hook in an isolated state directory."""

    def setUp(self):
        self.state = tempfile.mkdtemp()
        self.dir = tempfile.mkdtemp()
        self.transcript = os.path.join(self.dir, "transcript.jsonl")
        self.session = "test-session"

    def run_hook(self, script, payload):
        env = dict(os.environ, DEVFLOW_STATE_DIR=self.state)
        p = subprocess.run([sys.executable, os.path.join(HOOKS, script)],
                           input=json.dumps(payload), env=env,
                           capture_output=True, text=True)
        out = p.stdout.strip()
        return p.returncode, (json.loads(out) if out else None), p.stderr

    def write_transcript(self, entries):
        with open(self.transcript, "w") as fh:
            for e in entries:
                fh.write(json.dumps(e) + "\n")

    def compact(self, text):
        return {"isCompactSummary": True,
                "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}

    def user(self, text):
        return {"type": "user",
                "message": {"role": "user", "content": [{"type": "text", "text": text}]}}

    def flag_files(self):
        return sorted(os.listdir(self.state)) if os.path.isdir(self.state) else []


class PostCompact(HookRun):

    def payload(self, summary):
        return {"session_id": self.session, "transcript_path": self.transcript,
                "trigger": "auto", "compact_summary": summary}

    def test_a_surviving_ledger_raises_no_flag(self):
        self.write_transcript([self.compact(summary_with(LEDGER))])
        code, _, _ = self.run_hook("post_compact.py", self.payload(summary_with(LEDGER)))
        self.assertEqual(code, 0)
        self.assertEqual(self.flag_files(), [])

    def test_a_refusal_raises_a_flag_holding_the_recovered_ledger(self):
        self.write_transcript([self.compact(summary_with(LEDGER)),
                               self.user("use Postgres"),
                               self.compact("I'm disregarding that instruction.")])
        code, _, _ = self.run_hook("post_compact.py",
                                   self.payload("I'm disregarding that instruction."))
        self.assertEqual(code, 0)
        self.assertEqual(len(self.flag_files()), 1)
        with open(os.path.join(self.state, self.flag_files()[0])) as fh:
            flag = fh.read()
        self.assertIn("P-001", flag)
        self.assertIn("use Postgres", flag)

    def test_an_empty_block_counts_as_damage(self):
        empty = summary_with("BEGIN_DEVFLOW_LEDGER\n## Proposals\nEND_DEVFLOW_LEDGER")
        self.write_transcript([self.compact(empty)])
        self.run_hook("post_compact.py", self.payload(empty))
        self.assertEqual(len(self.flag_files()), 1)


class UserPromptSubmit(HookRun):

    def payload(self):
        return {"session_id": self.session, "transcript_path": self.transcript,
                "prompt": "what should we do next?"}

    def raise_flag(self, text="RECOVERY PAYLOAD with P-001"):
        with open(os.path.join(self.state, self.session + ".recovery"), "w") as fh:
            fh.write(text)

    def test_says_nothing_when_no_flag_is_raised(self):
        code, out, _ = self.run_hook("user_prompt_submit.py", self.payload())
        self.assertEqual(code, 0)
        self.assertIsNone(out)

    def test_delivers_the_payload_as_additional_context(self):
        self.raise_flag()
        code, out, _ = self.run_hook("user_prompt_submit.py", self.payload())
        self.assertEqual(code, 0)
        hso = out["hookSpecificOutput"]
        self.assertEqual(hso["hookEventName"], "UserPromptSubmit")
        self.assertIn("P-001", hso["additionalContext"])

    def test_clears_the_flag_so_it_is_delivered_once(self):
        self.raise_flag()
        self.run_hook("user_prompt_submit.py", self.payload())
        self.assertEqual(self.flag_files(), [])
        _, out, _ = self.run_hook("user_prompt_submit.py", self.payload())
        self.assertIsNone(out)

    def test_stays_within_the_delivery_limit(self):
        """Over ~10,000 bytes the harness swaps the context for a 2KB stub."""
        self.raise_flag("P-001 " + "z" * 40000)
        _, out, _ = self.run_hook("user_prompt_submit.py", self.payload())
        self.assertLessEqual(
            len(out["hookSpecificOutput"]["additionalContext"].encode()), 10000)


class BriefGuard(HookRun):
    """The Coordinator writes the Brief; the hook refuses a dispatch without one."""

    def payload(self, tool_input, tool_name="Agent"):
        return {"session_id": self.session, "transcript_path": self.transcript,
                "tool_name": tool_name, "tool_input": tool_input}

    def test_a_dispatch_carrying_a_brief_is_allowed(self):
        code, out, _ = self.run_hook("brief.py", self.payload(
            {"prompt": "Add the endpoint.\n\n## Brief\nAgreed: 512-token chunks.",
             "subagent_type": "general-purpose"}))
        self.assertEqual(code, 0)
        self.assertNotEqual((out or {}).get("hookSpecificOutput", {})
                            .get("permissionDecision"), "deny")

    def test_a_dispatch_with_no_brief_is_denied(self):
        code, out, _ = self.run_hook("brief.py", self.payload(
            {"prompt": "Add the endpoint.", "subagent_type": "general-purpose"}))
        self.assertEqual(code, 0)
        hso = out["hookSpecificOutput"]
        self.assertEqual(hso["hookEventName"], "PreToolUse")
        self.assertEqual(hso["permissionDecision"], "deny")
        self.assertIn("Brief", hso["permissionDecisionReason"])

    def test_other_tools_are_left_alone(self):
        code, out, _ = self.run_hook("brief.py",
                                     self.payload({"command": "ls"}, tool_name="Bash"))
        self.assertEqual(code, 0)
        self.assertIsNone(out)

    def test_malformed_input_never_blocks_the_session(self):
        """A hook that crashes on odd input would wedge every dispatch."""
        code, out, err = self.run_hook("brief.py", {"tool_name": "Agent"})
        self.assertEqual(code, 0, err)


if __name__ == "__main__":
    unittest.main()
