"""Offline regression tests; no live tmux server or NetHack game is used."""

from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def format_screen(lines, *args):
    return subprocess.run(
        [sys.executable, "-B", str(ROOT / "transpose_map.py"), *args],
        input="\n".join(lines) + "\n", text=True, capture_output=True, check=True,
    ).stdout


class ScreenPreservationTests(unittest.TestCase):
    def test_panel_beyond_column_80_does_not_consume_map(self):
        line = "  |....@....|".ljust(82) + "Inventory"
        self.assertEqual(format_screen([line]), line + "\n")

    def test_text_crossing_column_80_is_not_split_or_labeled_modal(self):
        line = "  |....@....|".ljust(78) + "Coins and other possessions"
        self.assertEqual(format_screen([line]), line + "\n")

    def test_internal_blank_rows_keep_their_coordinates(self):
        lines = ["A message", "", "", "  -----", "", "  -----", "", ""]
        self.assertEqual(format_screen(lines), "\n".join(lines[:-2]) + "\n")


if __name__ == "__main__":
    unittest.main()
