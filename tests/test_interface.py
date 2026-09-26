"""Offline regression tests; no live tmux server or NetHack game is used."""

from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
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
        self.assertIn("--- Neighborhood: player at x=9, y=3 ---", output)
        self.assertIn("      7  8  9 10 11\n", output)
        self.assertIn(" y=3     d  @  e   \n", output)
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
        self.assertIn("player at x=1, y=0", output)
        self.assertNotIn("y=-", output)
        self.assertIn("NW=  N=  NE=  W=  E=.", output)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="nethack-interface-test-")
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.log = self.directory / "calls.jsonl"
        self.env = dict(os.environ, PATH=self.tmp.name + os.pathsep + os.environ["PATH"],
                        TEST_LOG=str(self.log), TEST_SCREEN="\n".join(gameplay_screen()),
                        TEST_FAIL="", TEST_SESSION_EXISTS="1")
        stub = self.directory / "tmux"
        stub.write_text(f"#!{sys.executable}\n" + '''import json, os, sys
with open(os.environ["TEST_LOG"], "a") as log:
    log.write(json.dumps(sys.argv[1:]) + "\\n")
command = sys.argv[1]
if command == os.environ["TEST_FAIL"]:
    print(command + " failed", file=sys.stderr)
    sys.exit(7)
if command == "has-session":
    sys.exit(0 if os.environ["TEST_SESSION_EXISTS"] == "1" else 1)
if command == "capture-pane":
    print(os.environ["TEST_SCREEN"])
if command == "display-message":
    print("8 4")
''')
        stub.chmod(0o755)
        sleep = self.directory / "sleep"
        sleep.write_text("#!/bin/sh\nexit 0\n")
        sleep.chmod(0o755)

    def run_interface(self, *args):
        return subprocess.run(["bash", str(ROOT / "run"), *args], env=self.env,
                              text=True, capture_output=True)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_input_and_observation_failures_are_nonzero_and_stop(self):
        for command, args in [
            ("send-keys", ["Escape"]), ("set-buffer", ["h"]),
            ("paste-buffer", ["h"]), ("capture-pane", []),
            ("display-message", ["--neighborhood"]),
        ]:
            with self.subTest(command=command):
                self.env["TEST_FAIL"] = command
                result = self.run_interface(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(command + " failed", result.stderr)
                self.assertEqual(self.calls()[-1][0], command)
                self.assertNotIn("Neighborhood", result.stdout)

    def test_session_mutation_failures_are_nonzero_and_stop(self):
        for command, args in [
            ("kill-session", ["--cleanup"]), ("kill-session", ["--init"]),
            ("new-session", ["--init"]), ("set-option", ["--init"]),
        ]:
            with self.subTest(command=command, args=args):
                self.env["TEST_FAIL"] = command
                self.env["TEST_SESSION_EXISTS"] = "0" if command in ("new-session", "set-option") else "1"
                result = self.run_interface(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.calls()[-1][0], command)

    def test_default_observation_is_plain_and_does_not_query_cursor(self):
        self.env["TEST_FAIL"] = "display-message"
        result = self.run_interface()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, self.env["TEST_SCREEN"] + "\n")
        self.assertEqual([call[0] for call in self.calls()], ["capture-pane"])

    def test_optional_neighborhood_uses_cursor_metadata(self):
        result = self.run_interface("--neighborhood")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("NW=a N=b NE=c W=d E=e SW=f S=g SE=h", result.stdout)
        self.assertEqual([call[0] for call in self.calls()], ["capture-pane", "display-message"])

    def test_optional_neighborhood_after_action_does_not_send_flag(self):
        result = self.run_interface("--neighborhood", "h")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--- Neighborhood: player at x=9, y=3 ---", result.stdout)
        self.assertEqual([call[-1] for call in self.calls() if call[0] == "set-buffer"], ["h"])

    def test_multiple_actions_require_explicit_batch_before_any_input(self):
        result = self.run_interface("h", "j")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--batch", result.stderr)
        self.assertEqual(self.calls(), [])

    def test_batch_captures_between_actions(self):
        result = self.run_interface("--batch", "h", "j")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([call[0] for call in self.calls()],
                         ["set-buffer", "paste-buffer", "capture-pane"] * 2)
        self.assertEqual(result.stdout,
                         "--- Action 1/2: 'h' ---\n" + self.env["TEST_SCREEN"] + "\n"
                         "--- Action 2/2: 'j' ---\n" + self.env["TEST_SCREEN"] + "\n")

    def test_batch_labels_escape_control_characters_without_changing_input(self):
        action = "name\n\t\x1b'"
        result = self.run_interface("--batch", action)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines()[0],
                         "--- Action 1/1: $'name\\n\\t\\E\\'' ---")
        self.assertEqual([call[-1] for call in self.calls() if call[0] == "set-buffer"], [action])

    def test_optional_neighborhood_applies_to_each_batch_capture(self):
        result = self.run_interface("--neighborhood", "--batch", "h", "j")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("--- Neighborhood: player at x=9, y=3 ---"), 2)

    def test_batch_stops_on_failed_action(self):
        self.env["TEST_FAIL"] = "paste-buffer"
        result = self.run_interface("--batch", "h", "j")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual([call[0] for call in self.calls()], ["set-buffer", "paste-buffer"])
        self.assertEqual(result.stdout, "--- Action 1/2: 'h' ---\n")

    def test_init_does_not_type_or_dismiss_startup_prompts(self):
        result = self.run_interface("--init")
        self.assertEqual(result.returncode, 0, result.stderr)
        commands = [call[0] for call in self.calls()]
        self.assertIn("new-session", commands)
        self.assertNotIn("paste-buffer", commands)
        self.assertNotIn("send-keys", commands)

    def test_invalid_options_do_not_touch_tmux(self):
        for args in [("--batch",), ("--unknown",), ("--init", "h"), ("--cleanup", "h")]:
            with self.subTest(args=args):
                self.assertEqual(self.run_interface(*args).returncode, 2)
                self.assertEqual(self.calls(), [])

    def test_extended_command_appends_return_before_observation(self):
        result = self.run_interface("#quit")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([call[-1] for call in self.calls() if call[0] == "set-buffer"],
                         ["#quit", "\r"])
        self.assertEqual([call[0] for call in self.calls()],
                         ["set-buffer", "paste-buffer"] * 2 + ["capture-pane"])


if __name__ == "__main__":
    unittest.main()
