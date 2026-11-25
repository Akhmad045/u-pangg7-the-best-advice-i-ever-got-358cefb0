#!/usr/bin/env python3
"""The Best Advice I Ever Got — one sentence, exactly as received.

The program writes a single sentence to /output/entry.txt: advice an
uncle gave while wiping grease off his hands, about the price of
buying cheap. It checks the competition gate first (1-200 characters,
one line, no leading or trailing whitespace) and refuses to write a
line that fails it.
"""
import argparse
import hashlib
import sys
import tempfile
from pathlib import Path

ENTRY = (
    "My uncle, wiping grease off his hands, said a cheap tool costs "
    "you twice: once when you buy it, and once when it breaks in your hand."
)
DESTINATION = Path("/output/entry.txt")
LIMIT = 200


def advice() -> str:
    """Return the entry sentence, exactly as it goes into the file."""
    return ENTRY


def check(text: str) -> str | None:
    """Return the first gate problem found, or None when the line passes."""
    if not text.strip():
        return "entry is blank"
    if len(text) > LIMIT or len(text) < 1:
        return "length %d outside 1..%d" % (len(text), LIMIT)
    if text.strip() != text:
        return "leading or trailing whitespace"
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in text):
        return "must be a single line with no control characters"
    return None


def write_entry(text: str, where: Path = DESTINATION) -> Path:
    """Write the sentence to the entry file, creating its folder first."""
    where.parent.mkdir(parents=True, exist_ok=True)
    where.write_text(text, encoding="utf-8")
    return where


def summary(text: str) -> str:
    """Chars, bytes, sha256 and gate verdict for the entry sentence."""
    raw = text.encode("utf-8")
    problem = check(text)
    verdict = "OK" if problem is None else "FAIL: " + problem
    return "chars=%d bytes=%d sha256=%s gate=%s" % (
        len(text), len(raw), hashlib.sha256(raw).hexdigest(), verdict)


def run_self_test() -> int:
    """Gate the sentence, probe the boundaries, verify a write round-trip."""
    failures = []
    problem = check(advice())
    if problem is not None:
        failures.append("entry fails its own gate: " + problem)
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / "entry.txt"
        write_entry(advice(), probe)
        if probe.read_bytes() != advice().encode("utf-8"):
            failures.append("round-trip mismatch: written bytes differ")
    cases = [
        ("", False), ("   ", False), ("x" * 201, False),
        ("two\nlines", False), (" padded ", False), ("tab\there", False),
        ("del\x7fchar", False),
        ("x", True), ("y" * 200, True),
    ]
    for probe_text, should_pass in cases:
        passed = check(probe_text) is None
        if passed != should_pass:
            failures.append("probe %r: expected %s, got %s" % (
                probe_text[:20], "pass" if should_pass else "fail",
                "pass" if passed else "fail"))
    if failures:
        print("self-test FAILED")
        for failure in failures:
            print("  - " + failure)
        return 1
    print("self-test OK: " + summary(advice()))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Command-line interface: write the entry, self-test, or describe it."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true",
                        help="check the sentence and gate probes, then exit")
    parser.add_argument("--info", action="store_true",
                        help="print the entry summary without writing it")
    parser.add_argument("--out", default=str(DESTINATION),
                        help="where to write the entry (default: %(default)s)")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    text = advice()
    if args.self_test:
        return run_self_test()
    if args.info:
        print(summary(text))
        return 0
    problem = check(text)
    if problem is not None:
        print("entry fails the gate: " + problem, file=sys.stderr)
        return 1
    write_entry(text, Path(args.out))
    print("wrote %s (%d chars)" % (args.out, len(text)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
