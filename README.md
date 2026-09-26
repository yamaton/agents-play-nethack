# Agents Play NetHack

A small tmux interface that lets a terminal-capable agent play NetHack. The
agent sends an action, reads the screen, and decides what to do next. The
same commands work across coding-agent harnesses.

The project originally demonstrated gameplay with Claude Code:
https://github.com/user-attachments/assets/090a868a-2536-4936-80aa-cd6365d9ee07

## Setup

Install NetHack, tmux, Bash, and `uv`, with `nethack` and `tmux` on `PATH`.
The formatter uses Python 3.13+ and the standard library. `uv` selects the
interpreter from its inline script metadata; no Python packages are required.
The project manifest and `uv.lock` likewise declare no third-party dependencies.

Read [AGENTS.md](AGENTS.md) for gameplay and development instructions. If your
harness does not automatically discover it, explicitly ask the agent to read it.

Start with a prompt such as:

> Read AGENTS.md, inspect the current game, and play toward Dungeon Level 2.
> If no game exists, initialize one and answer the startup prompts.

## Commands

```bash
./run --init             # Launch NetHack; replaces the existing tmux session
./run                    # Observe an existing session without sending input
./run --neighborhood     # Opt in to the neighborhood and adjacent-cell labels
./run h                  # Move west, then inspect the result
./run o                  # Request opening a door; inspect the direction prompt
./run h                  # Answer that prompt with west
./run s                  # Search nearby cells
./run ','                # Pick up items
./run '>'                # Descend while standing on downstairs
./run Space              # Advance a pager when prompted
./run Escape             # Cancel a command
./run '^P'               # Recent messages; C-p also works
./run '#quit'            # Extended command; Enter is appended automatically
./run S                  # Save and quit; answer any subsequent prompt
./run --cleanup          # Kill the tmux session
```

`--init` requests a human Valkyrie but may restore an existing save. It does
not delete save files or automatically dismiss startup prompts. Read the
screen and answer each prompt as it appears. Plain `./run` never starts or
resets a session; if none exists, initialize explicitly.

Only one action argument is accepted by default. `./run o h` now fails before
sending input. An intentional sequence uses `./run --batch o h`, which prints
the screen after each argument. It still continues automatically when a prompt
appears, so prefer separate calls during exploration and combat. A single
argument such as `5k` or literal text also sends multiple keystrokes without
intermediate observation.

Failures return a nonzero status. Some input may already have reached the game
before a later operation fails; re-observe before deciding whether to retry.

## Reading the screen

`run` preserves the complete capture, including messages, menus, status, and
internal blank rows. It removes only unused blank terminal rows at the end.
It does not split text at guessed menu boundaries or label arbitrary right-hand
text as a modal prompt.

The default output is just the original screen. For extra spatial detail, put
`--neighborhood` first: `./run --neighborhood`, `./run --neighborhood h`, or
`./run --neighborhood --batch o h`. The option applies only to that invocation.

With this option, when the cursor points to `@` in the standard tty map and the
status is visible, the formatter can append a 5×5 neighborhood and labeled adjacent cells.
Recognized prompts, pagers, and right-hand panels suppress this helper. It also
stays absent when the cursor, layout, or player glyph cannot be verified.
Always read the actual prompt before choosing an action.

For a saved capture, explicit cursor coordinates are zero-based **X Y**:

```bash
uv run --script transpose_map.py --cursor 8 4 < capture.txt
```

Without `--cursor`, the formatter preserves the screen and omits the neighborhood.

## Session persistence and monitoring

The detached tmux game survives individual agent shell calls. The historical
session name `claude-nethack` and character name `Claude` are retained for
compatibility with existing sessions and saves; they do not require a particular
agent harness. Only one controller should send input to a game at a time.

```bash
tmux attach-session -t claude-nethack -r
```

On tmux versions that reject `send-keys` while a read-only viewer is attached,
Escape and control-key actions can fail. Detach the viewer or attach normally
before retrying those actions. The runner reports the failure.

The agent's execution environment must permit access to the tmux socket and
NetHack's save directory. A terminal host such as herdr does not remove those
sandbox requirements.

## Development checks

```bash
uv run --locked python -B -m unittest discover -s tests -v
bash -n run
shellcheck run
```

The tests use fixtures and a temporary tmux stub, so they neither start NetHack
nor touch live sessions. `--locked` verifies that the project manifest and
lockfile agree before running the standard-library test suite.

For a longer game, keep run-specific observations in a separate notes file,
including character, dungeon level, current objective, and unresolved risks.
Reconcile those notes with the live screen when resuming; maps and pets vary
between games.
