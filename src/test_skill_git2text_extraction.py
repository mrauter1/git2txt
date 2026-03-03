import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "git2text-extraction"
SCRIPT_PATH = SKILL_ROOT / "scripts" / "run_git2text.sh"
SKILL_MD = SKILL_ROOT / "SKILL.md"
PRESETS_MD = SKILL_ROOT / "references" / "presets.md"
TROUBLE_MD = SKILL_ROOT / "references" / "troubleshooting.md"


class TestGit2TextExtractionSkill(unittest.TestCase):
    def test_skill_files_exist(self):
        self.assertTrue(SKILL_MD.exists())
        self.assertTrue(PRESETS_MD.exists())
        self.assertTrue(TROUBLE_MD.exists())
        self.assertTrue(SCRIPT_PATH.exists())

    def test_skill_frontmatter_and_links(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("name: git2text-extraction", content)
        self.assertIn("description:", content)
        self.assertIn("references/presets.md", content)
        self.assertIn("references/troubleshooting.md", content)

    def test_run_script_usage_without_source(self):
        result = subprocess.run([str(SCRIPT_PATH)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage:", result.stderr)

    def test_run_script_dry_run_local_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "out.md"
            result = subprocess.run(
                [
                    str(SCRIPT_PATH),
                    "--dry-run",
                    tmpdir,
                    "-inc",
                    "*.py",
                    "-o",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(
            "Running: git2text" in result.stdout
            or "Running: python -m src.git2text" in result.stdout
            or "Running: python3 -m src.git2text" in result.stdout
        )

    def test_run_script_exec_with_fake_git2text_and_output_check(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "repo"
            source_dir.mkdir()
            out_file = Path(tmpdir) / "result.md"

            bin_dir = Path(tmpdir) / "bin"
            bin_dir.mkdir()
            fake_exe = bin_dir / "git2text"
            fake_exe.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "OUT=''\n"
                "while [ \"$#\" -gt 0 ]; do\n"
                "  if [ \"$1\" = '-o' ]; then OUT=\"$2\"; shift 2; continue; fi\n"
                "  shift\n"
                "done\n"
                "echo '# fake output' > \"$OUT\"\n",
                encoding="utf-8",
            )
            fake_exe.chmod(fake_exe.stat().st_mode | stat.S_IEXEC)

            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}:{env['PATH']}"
            result = subprocess.run(
                [
                    str(SCRIPT_PATH),
                    "--require-output",
                    str(out_file),
                    str(source_dir),
                    "-o",
                    str(out_file),
                ],
                capture_output=True,
                text=True,
                env=env,
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(out_file.exists())
            self.assertGreater(out_file.stat().st_size, 0)
            self.assertIn("Validated output:", result.stdout)


if __name__ == "__main__":
    unittest.main()
