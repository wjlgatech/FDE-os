"""Every fenced demo in skills/snowflake-os/SKILL.md must run with its documented
exit code, and every path it names must exist. Same discipline as the fde-os
master skill: a routing doc that drifts turns the build red instead of quietly
lying to whoever reads it."""
import os
import re
import subprocess
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SKILL_MD = os.path.join(HERE, "..", "SKILL.md")

CMD_RE = re.compile(r"^(python3 |printf )(.+?)(?:\s+#\s*exit\s+(\d+))?$")


def fenced_bash_commands():
    with open(SKILL_MD, encoding="utf-8") as f:
        text = f.read()
    for block in re.findall(r"```bash\n(.*?)```", text, flags=re.S):
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if m := CMD_RE.match(line):
                yield (m.group(1) + m.group(2)).strip(), int(m.group(3) or 0)


class TestSnowflakeOsExamples(unittest.TestCase):
    def test_every_fenced_demo_runs_with_its_documented_exit_code(self):
        cmds = list(fenced_bash_commands())
        self.assertGreaterEqual(len(cmds), 14, "the super tool must keep real demos")
        for cmd, expected in cmds:
            with self.subTest(cmd=cmd[:80]):
                run = subprocess.run(cmd, shell=True, cwd=ROOT,
                                     capture_output=True, text=True, timeout=120)
                self.assertEqual(
                    run.returncode, expected,
                    f"\n$ {cmd}\nexpected exit {expected}, got {run.returncode}\n"
                    f"stdout: {run.stdout[-400:]}\nstderr: {run.stderr[-400:]}")

    def test_referenced_paths_exist(self):
        with open(SKILL_MD, encoding="utf-8") as f:
            text = f.read()
        pattern = r"`((?:skills|workflows|snowflake-os|knowledge)/[\w\-./]+\.(?:py|json|md|yml|html))`"
        found = re.findall(pattern, text)
        self.assertGreater(len(found), 4, "the skill should name its real files")
        for rel in found:
            with self.subTest(path=rel):
                self.assertTrue(os.path.exists(os.path.join(ROOT, rel)),
                                f"SKILL.md references a missing path: {rel}")

    def test_no_networked_command_is_advertised_as_a_demo(self):
        """sync.py is the only networked entry point and must never appear in a
        fenced demo — CI is offline, and a demo that needs the internet is a demo
        that fails for reasons unrelated to the code."""
        for cmd, _ in fenced_bash_commands():
            self.assertNotIn("sync.py fetch", cmd)
            self.assertNotIn("sync.py drift", cmd)


if __name__ == "__main__":
    unittest.main()
