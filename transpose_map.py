#!/usr/bin/env python3
"""Preserve a NetHack tty capture and append a cursor-verified neighborhood.

The default tty map occupies columns 0..79 and screen rows 1..21. Without
cursor metadata or a recognizable gameplay screen, show only the capture.
"""

import argparse
import re
import sys

MAP_WIDTH = 80
MAP_TOP = 1
MAP_HEIGHT = 21
STATUS_RE = re.compile(r"HP:\s*\d+\s*\(\s*\d+\).*Pw:.*AC:")
PAGER_RE = re.compile(r"--More--|\(end\)|\(\d+ of \d+\)", re.IGNORECASE)


def cell_at(lines, row, col):
    if 0 <= row < len(lines) and 0 <= col < len(lines[row]):
        return lines[row][col]
    return " "


def find_player(lines, cursor):
    """Locate the cursor's @ on a normal tty map; do not guess from glyphs."""
    if cursor is None:
        return None
    col, row = cursor
    if not (0 <= col < MAP_WIDTH and MAP_TOP <= row < MAP_TOP + MAP_HEIGHT):
        return None
    if cell_at(lines, row, col) != "@":
        return None
    if not any(STATUS_RE.search(line) for line in lines[MAP_TOP + MAP_HEIGHT:]):
        return None
    if any(PAGER_RE.search(line) for line in lines):
        return None
    # Right-hand text or a question makes the input mode uncertain. Keep
    # the original screen, without labeling it as a modal menu.
    if any(line[MAP_WIDTH:].strip() for line in lines):
        return None
    if lines and ("?" in lines[0] or lines[0].rstrip().endswith(":") or "#" in lines[0]):
        return None
    return row, col


def print_neighborhood(lines, pos):
    row, col = pos
    map_lines = [line[:MAP_WIDTH] for line in lines[MAP_TOP:MAP_TOP + MAP_HEIGHT]]
    row -= MAP_TOP
    print("--- Neighborhood of @ ---")
    for dr in range(-2, 3):
        cells = " ".join(cell_at(map_lines, row + dr, col + dc) for dc in range(-2, 3))
        print(f"W {cells} E" if dr == 0 else f"  {cells}")
    labels = [
        ("NW", -1, -1), ("N", -1, 0), ("NE", -1, 1),
        ("W", 0, -1), ("E", 0, 1),
        ("SW", 1, -1), ("S", 1, 0), ("SE", 1, 1),
    ]
    print(" ".join(
        f"{direction}={cell_at(map_lines, row + dr, col + dc)}"
        for direction, dr, dc in labels
    ))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cursor", nargs=2, type=int, metavar=("X", "Y"),
                        help="zero-based tmux cursor coordinates")
    args = parser.parse_args()
    lines = sys.stdin.read().splitlines()
    # Trim only unused terminal rows at the end. Whitespace between rooms
    # is not a reliable menu boundary; retain the entire original screen.
    while lines and not lines[-1].strip():
        lines.pop()
    for line in lines:
        print(line)
    pos = find_player(lines, args.cursor)
    if pos is not None:
        print_neighborhood(lines, pos)


if __name__ == "__main__":
    main()
