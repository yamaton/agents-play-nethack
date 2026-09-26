# NetHack Agent Instructions

These instructions apply to any agent that can run shell commands. Play the
game when asked to play; a code review or development task is not a request
to start or reset a game.

## Development

- Use `uv` for Python commands. The formatter declares its dependencies inline.
- Run `uv run --locked python -B -m unittest discover -s tests -v` after changes.
- Check shell changes with `bash -n run` and `shellcheck run` when available.
- Tests use an isolated tmux stub; do not reset a live game for testing.

## Mission
When playing, explore the dungeon, descend levels, and survive. The initial
goal is Dungeon Level 2+, unless the user specifies another goal. Inspect the
live screen for current progress; these instructions do not record a run's state.

## How to Play

### Running the Game
- `./run --init` — launch NetHack (kills the existing tmux session; may restore a save)
- `./run` — view an existing game (no input sent, no automatic session creation)
- `./run h` — send one action and inspect the resulting screen
- `./run --batch o h` — explicitly send a known sequence, capturing after each argument
- `./run --cleanup` — kill the tmux session

Initialization requests a human Valkyrie. Read and answer any character or
restore prompts individually; do not blindly send a fixed selection sequence.
Observe an existing session before deciding whether to initialize it. Save
with `S` and answer any confirmation before ending a game you want to keep.

### Action Discipline
- Prefer one key per call, then inspect messages, HP, and the input prompt.
- Multiple action arguments require `--batch`. Batch mode records intermediate
  screens but continues automatically, even if a prompt appears. Use it only
  for a known input sequence; avoid it during exploration or combat.
- One literal argument can also contain multiple keystrokes, such as `5k` or
  a text answer. These do not provide intermediate observations either.
- A nonzero exit status means input or observation failed. Read the error and
  re-observe before retrying: earlier inputs may already have taken effect.
- Use one controller per game; simultaneous drivers can interleave inputs.

### Output Format
`./run` prints:
1. **Original screen** — complete text, map, and status, preserving columns and internal blank rows
2. **Neighborhood of @**, when verified — a 5x5 visual grid and labeled adjacent cells (e.g. `NW=. N=< NE=\| W=. E=. SW=. S=. SE=.`)

The helper uses the tmux cursor, the standard tty map area, and the status line
to locate the player. It omits the neighborhood on recognized prompts, pagers,
right-hand panels, or uncertain screens. It never chooses the first `@` merely
because it appears in the capture. Unsupported layouts or player glyphs may
also omit the helper; the original screen remains available.

Read the actual prompt before moving. Use `Space` for a `--More--` pager and
`Escape` to cancel when appropriate. Right-hand text alone does not prove that
a modal menu is open, and a neighborhood is not proof that movement is safe.

### Reading the Output
- **Neighborhood line**: the quickest way to check adjacent cells — read `NW=` `N=` `NE=` etc. directly
- **5x5 grid**: for slightly wider spatial context (2 cells in each direction)
- **Original map**: for full-map W/E and N/S awareness and overall layout

### Key Commands
- `h j k l` — move W/S/N/E
- `y u b n` — move NW/NE/SW/SE
- `o` + direction — open a door
- `s` — search for hidden doors/passages (repeat multiple times)
- `,` — pick up item
- `>` — descend stairs (must be standing on `>`)
- `S` — save and quit
- `.` — wait one turn
- `i` — inventory
- `/` — look at things (opens a submenu, see below)
- `#command` — extended command, e.g. `./run '#quit'` (Enter is sent automatically)
- `^P` — message history, one message back per press: `./run '^P'` or `./run C-p`
  (use after batched moves to catch messages that scrolled by, e.g. what hit you)
- `Space` — dismiss "--More--" prompts
- `Escape` — cancel a command

### The `/` (Look) Command
Use `./run '/'`, inspect the submenu, then send its option in a separate call:
- `o` — nearby objects (e.g. `./run o` at that submenu)
- `O` — all objects shown on map
- `m` — nearby monsters
- `M` — all monsters shown on map
- `i` — something you're carrying
- `?` — identify a symbol by typing it

Output can show items/monsters with their map coordinates. Follow the displayed pager prompt.
Use this regularly for situational awareness instead of building custom tools.

### Map Symbols
- `@` — usual player glyph; other creatures can share it
- `d` / `f` — dog / cat classes; identify the creature before assuming it is your pet
- `.` — floor
- `#` — corridor
- `-` — horizontal wall
- `\|` — vertical wall (NOTE: escape as `\|` in markdown tables!)
- `+` — closed door
- `<` — stairs up
- `>` — stairs down (descend target)
- `$` — gold
- `?` — scroll
- `!` — potion
- `)` — weapon
- `[` — armor
- `%` — corpse / food

## Gameplay Knowledge

### Character
- Default to a human Valkyrie for straightforward melee combat unless directed otherwise.
- Read actual attributes, inventory, and HP from the current game.

### Dungeon Exploration
- Every game has a randomly generated layout; never assume previous maps apply
- Explore systematically: clear each room, follow every corridor
- Use `s` (search) repeatedly near walls to find hidden doors/passages
- Look for wall discontinuities (`.` symbols breaking `---` patterns)
- Open doors render as `-` or `|` (matching passage direction), nearly identical
  to wall glyphs in monochrome — scrutinize walls for out-of-place characters
- Small starting rooms often have hidden exits — search all walls

### Combat
- Move into enemies to attack (automatic melee)
- Pets help fight and eat corpses
- Monitor HP; retreat when low
- Check messages after each exchange; do not assume an encounter is harmless.

### Formatting Pitfall
When writing markdown tables that contain the pipe character `|`, always escape it as `\|`. Otherwise the table rendering breaks and the cell appears empty.
