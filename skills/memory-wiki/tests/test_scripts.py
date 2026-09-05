from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run_script(name: str, *args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPTS / name), *(str(arg) for arg in args)],
        capture_output=True,
        check=False,
        text=True,
    )


class ProjectScriptsTest(unittest.TestCase):
    def test_init_and_lint_writing_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "article"
            result = run_script("init_project.py", project, "--mode", "writing", "--title", "Useful Memory")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((project / "wiki/sources").is_dir())

            lint = run_script("lint_project.py", project)
            self.assertEqual(lint.returncode, 0, lint.stdout + lint.stderr)
            self.assertIn("seed.md is not frozen", lint.stdout)

    def test_seed_file_is_frozen_during_init(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            seed = root / "idea.md"
            seed.write_text("# Idea\n\nMy original view.\n", encoding="utf-8")
            project = root / "article"

            result = run_script(
                "init_project.py",
                project,
                "--mode",
                "writing",
                "--title",
                "Idea",
                "--seed-file",
                seed,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            lint = run_script("lint_project.py", project)
            self.assertEqual(lint.returncode, 0, lint.stdout + lint.stderr)
            self.assertNotIn("not frozen", lint.stdout)

            (project / "seed.md").write_text("changed\n", encoding="utf-8")
            lint = run_script("lint_project.py", project)
            self.assertEqual(lint.returncode, 1)
            self.assertIn("changed after it was frozen", lint.stdout)

    def test_freeze_rejects_template_and_accepts_completed_seed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "feature"
            init = run_script(
                "init_project.py",
                project,
                "--mode",
                "building",
                "--title",
                "Add search",
                "--target-repo",
                ROOT,
            )
            self.assertEqual(init.returncode, 0, init.stderr)
            rejected = run_script("freeze_seed.py", project)
            self.assertEqual(rejected.returncode, 2)

            (project / "seed.md").write_text(
                "# Add search\n\n## Problem\nNo search.\n\n## Acceptance criteria\n\n- [ ] Query returns matches.\n",
                encoding="utf-8",
            )
            frozen = run_script("freeze_seed.py", project)
            self.assertEqual(frozen.returncode, 0, frozen.stderr)
            self.assertEqual(len(frozen.stdout.strip()), 64)
            lint = run_script("lint_project.py", project)
            self.assertEqual(lint.returncode, 0, lint.stdout + lint.stderr)

    def test_init_refuses_nonempty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "existing"
            project.mkdir()
            (project / "keep.txt").write_text("keep", encoding="utf-8")
            result = run_script("init_project.py", project, "--mode", "writing", "--title", "No")
            self.assertEqual(result.returncode, 2)
            self.assertEqual((project / "keep.txt").read_text(encoding="utf-8"), "keep")

    def test_lint_rejects_missing_selected_source_page(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            seed = root / "seed-input.md"
            seed.write_text("# Seed\n", encoding="utf-8")
            project = root / "article"
            init = run_script(
                "init_project.py",
                project,
                "--mode",
                "writing",
                "--title",
                "Article",
                "--seed-file",
                seed,
            )
            self.assertEqual(init.returncode, 0, init.stderr)
            (project / "sources/index.yaml").write_text(
                """schema_version: 1
sources:
  - id: missing
    title: Missing page
    type: article
    locator: https://example.com
    authority: primary
    summary: A source without its page.
    page: wiki/sources/missing.md
    status: selected
""",
                encoding="utf-8",
            )
            lint = run_script("lint_project.py", project)
            self.assertEqual(lint.returncode, 1)
            self.assertIn("selected page does not exist", lint.stdout)

    def test_readiness_and_mode_transitions_are_guarded(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            seed = root / "seed.md"
            seed.write_text("# Article seed\n\nA real point of view.\n", encoding="utf-8")
            project = root / "article"
            init = run_script(
                "init_project.py",
                project,
                "--mode",
                "writing",
                "--title",
                "Article",
                "--seed-file",
                seed,
            )
            self.assertEqual(init.returncode, 0, init.stderr)

            for status in ("researching", "distilled", "critiqued"):
                advanced = run_script(
                    "advance_project.py",
                    project,
                    status,
                    "--reason",
                    f"ready for {status}",
                )
                self.assertEqual(advanced.returncode, 0, advanced.stderr)

            not_ready = run_script(
                "advance_project.py",
                project,
                "ready",
                "--reason",
                "critique is incomplete",
            )
            self.assertEqual(not_ready.returncode, 2)

            (project / "guideline.md").write_text("# Guideline\n\nA complete plan.\n", encoding="utf-8")
            (project / "critique.md").write_text(
                "# Critique\n\n## Reflection\n\nPassed.\n\n## Decision review\n\nChoices resolved.\n",
                encoding="utf-8",
            )
            ready = run_script(
                "advance_project.py",
                project,
                "ready",
                "--reason",
                "plan passed critique and lint",
            )
            self.assertEqual(ready.returncode, 0, ready.stderr)

            wrong_mode = run_script(
                "advance_project.py",
                project,
                "implemented",
                "--reason",
                "wrong last mile",
            )
            self.assertEqual(wrong_mode.returncode, 2)
            rendered = run_script(
                "advance_project.py",
                project,
                "rendered",
                "--reason",
                "draft rendered",
            )
            self.assertEqual(rendered.returncode, 0, rendered.stderr)


if __name__ == "__main__":
    unittest.main()
