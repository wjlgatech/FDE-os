"""The master skill's demos must never rot: every fenced bash command in
skills/fde-os/SKILL.md is executed here with its documented exit code asserted.
A demo that drifts (renamed script, changed example, different exit) turns the
build red — the routing doc stays honest by construction."""
import os
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SKILL_MD = os.path.join(HERE, "..", "SKILL.md")

CMD_RE = re.compile(r"^(python3 |printf )(.+?)(?:\s+#\s*exit\s+(\d+))?$")


def fenced_bash_commands():
    """Yield (command, expected_exit) for every command line in bash fences."""
    with open(SKILL_MD, encoding="utf-8") as f:
        text = f.read()
    for block in re.findall(r"```bash\n(.*?)```", text, flags=re.S):
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = CMD_RE.match(line)
            if m:
                cmd = (m.group(1) + m.group(2)).strip()
                expected = int(m.group(3)) if m.group(3) else 0
                yield cmd, expected


class TestMasterExamples(unittest.TestCase):
    def test_every_fenced_demo_runs_with_its_documented_exit_code(self):
        cmds = list(fenced_bash_commands())
        self.assertGreaterEqual(len(cmds), 12, "the master skill must keep real demos")
        for cmd, expected in cmds:
            with self.subTest(cmd=cmd[:80]):
                run = subprocess.run(cmd, shell=True, cwd=ROOT,
                                     capture_output=True, text=True, timeout=120)
                self.assertEqual(
                    run.returncode, expected,
                    f"\n$ {cmd}\nexpected exit {expected}, got {run.returncode}\n"
                    f"stdout: {run.stdout[-400:]}\nstderr: {run.stderr[-400:]}")

    def test_routing_table_names_only_real_paths(self):
        with open(SKILL_MD, encoding="utf-8") as f:
            text = f.read()
        for rel in re.findall(r"`((?:skills|workflows|take-home)/[\w\-./]+\.(?:py|json|md))`",
                              text):
            with self.subTest(path=rel):
                self.assertTrue(os.path.exists(os.path.join(ROOT, rel)),
                                f"SKILL.md references a missing path: {rel}")


if __name__ == "__main__":
    unittest.main()
