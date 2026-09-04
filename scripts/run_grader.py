#!/usr/bin/env python3
"""Run the external grader against a repository copy."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = PROJECT_ROOT / "environment" / "repo"
SOLUTION_DIR = PROJECT_ROOT / "solution"
TESTS_DIR = PROJECT_ROOT / "tests"


def run_pytest(repo_root: Path) -> int:
    env = {**os.environ, "GRADER_REPO_ROOT": str(repo_root)}
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(TESTS_DIR), "-q"],
        cwd=PROJECT_ROOT,
        env=env,
    )
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Grade a webhook receiver repository")
    parser.add_argument(
        "--repo",
        type=Path,
        default=DEFAULT_REPO,
        help="Repository path to grade (default: starting buggy repo)",
    )
    parser.add_argument(
        "--apply-solution",
        action="store_true",
        help="Copy repo to temp dir and apply reference solution before grading",
    )
    args = parser.parse_args()

    if args.apply_solution:
        with tempfile.TemporaryDirectory(prefix="webhook-grader-") as tmp:
            tmp_repo = Path(tmp) / "repo"
            shutil.copytree(args.repo, tmp_repo)
            for src in SOLUTION_DIR.glob("*.py"):
                shutil.copy2(src, tmp_repo / "app" / src.name)
            return run_pytest(tmp_repo)

    return run_pytest(args.repo.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
