"""Contract and behavior tests for the shared Python quality workflow caller."""

import os
import re
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parent
WORKFLOW_PATH = REPOSITORY_ROOT / ".github" / "workflows" / "quality.yml"


def _indented_block(document, header, indentation):
    """Return the YAML text nested directly below an exact header line."""
    lines = document.splitlines()
    expected_header = f"{' ' * indentation}{header}"

    try:
        start = lines.index(expected_header) + 1
    except ValueError as error:
        raise AssertionError(f"Missing workflow header: {header}") from error

    block = []
    for line in lines[start:]:
        if line and len(line) - len(line.lstrip()) <= indentation:
            break
        block.append(line)
    return "\n".join(block)


def _test_command(document):
    match = re.search(
        r"^\s+test-command:\s+'(?P<command>.*)'\s*$",
        document,
        flags=re.MULTILINE,
    )
    if match is None:
        raise AssertionError("quality.yml must define a single-quoted test-command")
    return match.group("command")


class QualityWorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_has_the_expected_name_and_single_quality_job(self):
        jobs = _indented_block(self.workflow, "jobs:", indentation=0)

        self.assertTrue(self.workflow.startswith("name: Quality\n"))
        self.assertEqual(1, len(re.findall(r"(?m)^  [a-z0-9-]+:$", jobs)))
        self.assertRegex(jobs, r"(?m)^  python-quality:$")

    def test_runs_for_main_pushes_pull_requests_and_manual_dispatches(self):
        triggers = _indented_block(self.workflow, "on:", indentation=0)

        self.assertRegex(triggers, r"(?m)^  push:\n    branches: \[main\]$")
        self.assertRegex(triggers, r"(?m)^  pull_request:$")
        self.assertRegex(triggers, r"(?m)^  workflow_dispatch:$")

    def test_grants_only_read_access_to_repository_contents(self):
        permissions = _indented_block(self.workflow, "permissions:", indentation=0)

        self.assertEqual("contents: read", permissions.strip())

    def test_delegates_to_the_expected_shared_workflow(self):
        job = _indented_block(self.workflow, "python-quality:", indentation=2)

        self.assertRegex(
            job,
            r"(?m)^    uses: "
            r"jesseray718/\.github/\.github/workflows/python-quality\.yml@main$",
        )
        self.assertNotIn("runs-on:", job)
        self.assertNotIn("steps:", job)

    def test_passes_the_supported_python_quality_inputs(self):
        job = _indented_block(self.workflow, "python-quality:", indentation=2)

        self.assertRegex(job, r'(?m)^      python-version: "3\.12"$')
        self.assertRegex(job, r'(?m)^      compile-path: "\."$')
        self.assertEqual(1, len(re.findall(r"(?m)^      test-command:", job)))


class QualityTestCommandBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        cls.test_command = _test_command(workflow)

    def _run_test_command(self, files=None, directories=()):
        with tempfile.TemporaryDirectory() as temporary_directory:
            working_directory = Path(temporary_directory)
            for directory in directories:
                (working_directory / directory).mkdir(parents=True)
            for relative_path, contents in (files or {}).items():
                path = working_directory / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(textwrap.dedent(contents), encoding="utf-8")

            environment = os.environ.copy()
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            return subprocess.run(
                ["bash", "-c", self.test_command],
                cwd=working_directory,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

    def test_skips_cleanly_when_no_python_tests_exist(self):
        result = self._run_test_command(
            {"helper.py": "raise RuntimeError('this is not a test module')\n"}
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("No unittest tests found; skipping test step.", result.stdout)
        self.assertNotIn("Ran ", result.stderr)

    def test_ignores_test_named_directories_and_nonmatching_python_files(self):
        result = self._run_test_command(
            {"checks/quality_test.py": "raise RuntimeError('must not be imported')\n"},
            directories=("test_helpers.py",),
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("No unittest tests found; skipping test step.", result.stdout)

    def test_runs_a_matching_unittest_module(self):
        result = self._run_test_command(
            {
                "test_example.py": """
                    import unittest

                    class ExampleTest(unittest.TestCase):
                        def test_passes(self):
                            self.assertEqual(4, 2 + 2)
                """
            }
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Ran 1 test", result.stderr)
        self.assertIn("OK", result.stderr)
        self.assertNotIn("skipping test step", result.stdout)

    def test_discovers_matching_tests_in_a_package(self):
        result = self._run_test_command(
            {
                "checks/__init__.py": "",
                "checks/test_nested.py": """
                    import unittest

                    class NestedTest(unittest.TestCase):
                        def test_passes(self):
                            self.assertTrue(True)
                """,
            }
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Ran 1 test", result.stderr)
        self.assertIn("test_passes (checks.test_nested.NestedTest)", result.stderr)

    def test_propagates_a_failing_test_exit_status(self):
        result = self._run_test_command(
            {
                "test_failure.py": """
                    import unittest

                    class FailureTest(unittest.TestCase):
                        def test_fails(self):
                            self.fail("intentional regression fixture")
                """
            }
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("FAILED (failures=1)", result.stderr)
        self.assertNotIn("skipping test step", result.stdout)


if __name__ == "__main__":
    unittest.main()
