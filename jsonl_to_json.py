#!/usr/bin/env python3
"""Convert UTF-8 JSONL objects to one JSON array without overwriting files."""
import argparse
import json
import sys
from pathlib import Path


def reject_constant(value):
    raise ValueError("non-JSON numeric constant: " + value)


def load_records(source):
    records = []
    with source.open("r", encoding="utf-8-sig") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line, parse_constant=reject_constant)
            except ValueError as exc:
                raise ValueError(f"{source.name}:{line_number}: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"{source.name}:{line_number}: expected a JSON object")
            records.append(record)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 JSONL source file")
    parser.add_argument("output", type=Path, help="New destination file; must not exist")
    args = parser.parse_args()
    try:
        # Fully validate and serialize before opening the destination.
        rendered = json.dumps(load_records(args.input), ensure_ascii=False, indent=2)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(rendered + "\n")
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
