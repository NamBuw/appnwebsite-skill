#!/usr/bin/env python3
"""Minimal stdlib-only fixture script supporting --help."""

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sample minimal skill helper script using Python 3 stdlib only."
    )
    parser.add_argument("--check", action="store_true", help="Run sample check.")
    args = parser.parse_args()
    if args.check:
        print("OK: sample check passed")
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
