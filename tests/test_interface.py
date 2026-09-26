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


def gameplay_screen():
    lines = [""] * 24
    lines[2] = "  @"  # Another @ must not be mistaken for the player.
    lines[3] = "       abc"
    lines[4] = "       d@e"
    lines[5] = "       fgh"
    lines[22] = "Player St:18 Dx:12 Co:18 In:8 Wi:10 Ch:10 Lawful"
    lines[23] = "Dlvl:1 $:0 HP:16(16) Pw:1(1) AC:6 Xp:1"
    return lines


class PlayerDetectionTests(unittest.TestCase):
    def test_cursor_selects_player_instead_of_first_at_sign(self):
        output = format_screen(gameplay_screen(), "--cursor", "8", "4")
        self.assertIn("NW=a N=b NE=c W=d E=e SW=f S=g SE=h", output)

    def test_no_cursor_does_not_guess(self):
        self.assertNotIn("Neighborhood", format_screen(gameplay_screen()))

    def test_cursor_elsewhere_does_not_guess(self):
        self.assertNotIn("Neighborhood", format_screen(gameplay_screen(), "--cursor", "9", "4"))

    def test_text_query_is_not_a_player(self):
        output = format_screen(["", "What is @?", "A human or elf."], "--cursor", "8", "1")
        self.assertNotIn("Neighborhood", output)

    def test_prompt_or_panel_suppresses_neighborhood_even_with_map_cursor(self):
        for prompt in ["What direction?", "Name:", "#", "--More--", "(end)", "(1 of 2)"]:
            with self.subTest(prompt=prompt):
                lines = gameplay_screen()
                lines[0] = prompt
                self.assertNotIn("Neighborhood", format_screen(lines, "--cursor", "8", "4"))
        lines = gameplay_screen()
        lines[3] = lines[3].ljust(82) + "Inventory"
        self.assertNotIn("Neighborhood", format_screen(lines, "--cursor", "8", "4"))

    def test_top_map_edge_does_not_include_message_row(self):
        lines = gameplay_screen()
        lines[0] = "message"
        lines[1] = "@."
        output = format_screen(lines, "--cursor", "0", "1")
        self.assertIn("NW=  N=  NE=  W=  E=.", output)


if __name__ == "__main__":
    unittest.main()
