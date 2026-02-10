import argparse
import subprocess
import sys


def run_command(command: list[str], name: str) -> bool:
    print(f"--- Running {name} ---")
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"{name} failed with return code {result.returncode}")
        return False
    print(f"{name} passed!")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Run quality checks.")
    parser.add_argument(
        "--fix", action="store_true", help="Try to fix issues automatically."
    )
    args = parser.parse_args()

    success = True

    # Ruff check
    ruff_check = ["ruff", "check", "."]
    if args.fix:
        ruff_check.append("--fix")
    success &= run_command(ruff_check, "Ruff Linting")

    # Ruff format
    ruff_format = ["ruff", "format", "."]
    if not args.fix:
        ruff_format.append("--check")
    success &= run_command(ruff_format, "Ruff Formatting")

    # Mypy
    success &= run_command(["mypy", "."], "Mypy Type Checking")

    # Pytest
    success &= run_command(["pytest"], "Pytest")

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
