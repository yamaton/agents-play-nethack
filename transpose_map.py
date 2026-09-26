#!/usr/bin/env python3
"""Format NetHack screen output for LLM consumption.

Processes raw tmux capture output into:
1. Original screen, preserving all columns and internal blank rows
2. Neighborhood of @ (5x5 grid + labeled 3x3)
"""

import sys

MAP_WIDTH = 80

STATUS_MARKERS = ["Dlvl:", "HP:", "Pw:", "AC:", "Xp:"]


def is_status_line(line):
    return any(m in line for m in STATUS_MARKERS)


def is_map_line(line):
    """Heuristic: map lines contain wall, corridor, or dungeon feature characters."""
    s = line.strip()
    if not s:
        return False
    has_wall = "|" in s or ("--" in s and not s.startswith("--More"))
    has_corridor = "#" in s
    has_player = "@" in s
    has_stairs = ">" in s or "<" in s
    return has_wall or has_corridor or has_player or has_stairs


def extract_map(lines):
    """Return the contiguous map region as a list of strings."""
    first = None
    last = None
    for i, line in enumerate(lines):
        if is_status_line(line):
            continue
        if is_map_line(line):
            if first is None:
                first = i
            last = i
    if first is None:
        return []
    return lines[first : last + 1]


def find_player(map_lines):
    """Find the (row, col) position of @ in the map, or None."""
    for r, line in enumerate(map_lines):
        c = line.find("@")
        if c != -1:
            return r, c
    return None


def cell_at(map_lines, r, c):
    """Get the character at (r, c), or space if out of bounds."""
    if 0 <= r < len(map_lines) and 0 <= c < len(map_lines[r]):
        return map_lines[r][c]
    return " "


def print_neighborhood(map_lines):
    """Print a 5x5 grid around @ and label the 8 adjacent cells."""
    pos = find_player(map_lines)
    if pos is None:
        return
    pr, pc = pos
    print("--- Neighborhood of @ ---")
    for dr in range(-2, 3):
        cells = " ".join(cell_at(map_lines, pr + dr, pc + dc) for dc in range(-2, 3))
        if dr == 0:
            print(f"W {cells} E")
        else:
            print(f"  {cells}")
    labels = [
        ("NW", -1, -1), ("N", -1, 0), ("NE", -1, 1),
        ("W", 0, -1), ("E", 0, 1),
        ("SW", 1, -1), ("S", 1, 0), ("SE", 1, 1),
    ]
    print(" ".join(f"{d}={cell_at(map_lines, pr+dr, pc+dc)}" for d, dr, dc in labels))


def main():
    raw_lines = sys.stdin.read().splitlines()
    # Trim only unused terminal rows at the end. Whitespace between rooms
    # is not a reliable menu boundary; retain the entire original screen.
    while raw_lines and not raw_lines[-1].strip():
        raw_lines.pop()
    for line in raw_lines:
        print(line)

    # Right-hand text makes the input mode uncertain. Do not invent a modal
    # label or a neighborhood while such a panel is visible.
    if not any(line[MAP_WIDTH:].strip() for line in raw_lines):
        extracted = extract_map(raw_lines)
        if extracted and find_player(extracted):
            print_neighborhood(extracted)


if __name__ == "__main__":
    main()
