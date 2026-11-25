#!/usr/bin/env python3
"""make.fun entry: two robots in an elevator.

One robot makes awkward small talk with another robot while they ride
an elevator together. The line leans on machine logic (a running
probability estimate) to make the silence itself the joke, then pivots
to the most robotically polite small-talk fallback imaginable: the
weather, which neither of them experiences.

The program prints exactly one line of entry text to stdout and
nothing else. It validates the entry against the bounty gate
(a single line under 200 characters) before printing, writes a copy
to the MAKEFUN_OUTPUT path for the reproduction check, reads that
copy back, and verifies the round trip byte for byte. If anything
about the primary text fails validation, a shorter fallback line is
used instead so the program still emits a valid entry.

Standard library only. Deterministic: no network, no clock, no
randomness, no environment-dependent output.
"""

import os
import sys

# ---------------------------------------------------------------------------
# Entry text
# ---------------------------------------------------------------------------

ENTRY = (
    "I calculated a 97% chance this silence turns awkward. "
    "Updating... 99%. Anyway, nice weather we're simulating today."
)

# A shorter fallback, kept valid under the same gate, used only if the
# primary entry ever fails validation (it should not: it is checked
# below and in the local test runs).
FALLBACK_ENTRY = (
    "My sensors detect awkward silence. Probability rising... "
    "So, do you come to this floor often?"
)

# Bounty gate: a single line, strictly under 200 characters.
MAX_CHARACTERS = 200

# Where the reproduction check expects the entry file. The sweep uses
# a unique path per entry so concurrent entries cannot overwrite each
# other; honour MAKEFUN_OUTPUT when the harness sets it.
DEFAULT_OUTPUT_PATH = (
    "/tmp/sweep24-u-motasimfuad-two-robots-in-an-elevator-8c6aeb8f/entry.txt"
)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def is_single_line(text):
    """Return True when *text* contains no line breaks at all."""
    return "\n" not in text and "\r" not in text


def is_under_limit(text, limit=MAX_CHARACTERS):
    """Return True when *text* is strictly shorter than the limit."""
    return len(text) < limit


def has_robot_logic(text):
    """Check the line shows machine logic, not just human small talk.

    The entry must read as something a robot would actually say, so
    it needs at least one marker of computation: a percentage, a
    calculation verb, or a sensor / update reference.
    """
    markers = ("%", "calculat", "updat", "sensor", "probab")
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def has_elevator_awkwardness(text):
    """Check the awkward-silence beat is present in the line."""
    lowered = text.lower()
    return "silence" in lowered or "awkward" in lowered


def validate_entry(text):
    """Return a list of problems with *text*; empty means valid."""
    problems = []
    if not text:
        problems.append("entry is empty")
    if not text.strip():
        problems.append("entry is only whitespace")
    if text != text.strip():
        problems.append("entry has leading or trailing whitespace")
    if not is_single_line(text):
        problems.append("entry is not a single line")
    if not is_under_limit(text):
        problems.append(
            "entry is %d characters, not under %d" % (len(text), MAX_CHARACTERS)
        )
    if "  " in text:
        problems.append("entry contains a double space")
    if text.count(".") < 2:
        problems.append("entry should carry its two-beat joke structure")
    if not has_robot_logic(text):
        problems.append("entry shows no machine logic")
    if not has_elevator_awkwardness(text):
        problems.append("entry has no awkward-silence beat")
    return problems


def choose_entry():
    """Pick the primary entry, falling back only if it is invalid."""
    if not validate_entry(ENTRY):
        return ENTRY
    fallback_problems = validate_entry(FALLBACK_ENTRY)
    if not fallback_problems:
        return FALLBACK_ENTRY
    # Both failed: this should be impossible, but never print an
    # invalid entry silently. Fail loudly instead.
    raise SystemExit(
        "no valid entry available: primary problems=%r fallback problems=%r"
        % (validate_entry(ENTRY), fallback_problems)
    )


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def output_path():
    """Resolve the file path the entry copy is written to."""
    return os.environ.get("MAKEFUN_OUTPUT", DEFAULT_OUTPUT_PATH)


def write_and_verify(text, path):
    """Write *text* to *path*, read it back, and verify the round trip."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    with open(path, "r", encoding="utf-8", newline="") as handle:
        read_back = handle.read()
    if read_back != text:
        raise SystemExit(
            "read-back verification failed: wrote %d characters, "
            "read back %d characters" % (len(text), len(read_back))
        )
    return path


def main():
    """Validate, persist, verify, then print exactly the entry text."""
    text = choose_entry()
    path = output_path()
    write_and_verify(text, path)
    # Diagnostics go to stderr only, so stdout stays exactly the entry.
    print(
        "entry verified: %d characters written to %s" % (len(text), path),
        file=sys.stderr,
    )
    # Print exactly the entry text: no trailing newline, no extra
    # output on stdout. Diagnostics, if any, would go to stderr.
    sys.stdout.write(text)
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
