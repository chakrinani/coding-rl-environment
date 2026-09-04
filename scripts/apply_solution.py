"""Apply reference solution files onto a working copy of the agent repo."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def apply_solution(repo_dir: Path, solution_dir: Path) -> None:
    for src in solution_dir.glob("*.py"):
        dest = repo_dir / "app" / src.name
        if not dest.exists():
            raise FileNotFoundError(f"No matching file in repo for solution file: {src.name}")
        shutil.copy2(src, dest)
        print(f"Applied {src.name} -> {dest}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply reference solution to repo copy")
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "environment" / "repo",
        help="Path to repository directory",
    )
    parser.add_argument(
        "--solution",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "solution",
        help="Path to solution directory",
    )
    args = parser.parse_args()
    apply_solution(args.repo, args.solution)


if __name__ == "__main__":
    main()
