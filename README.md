

# Claude Code Plays NetHack

https://github.com/user-attachments/assets/090a868a-2536-4936-80aa-cd6365d9ee07

This project enables Claude Code to autonomously play NetHack through a tmux-based interface, with comprehensive strategy tracking and gameplay documentation.

## Overview

NetHack is a classic roguelike dungeon crawler that requires strategic thinking, exploration, and tactical combat decisions. This project provides Claude Code with:

- **Persistent game sessions** via tmux for uninterrupted gameplay
- **Strategic documentation** with real-time decision tracking
- **Clean command interface** for sending game inputs and capturing output
- **Learning progression** that improves gameplay over multiple sessions

## Project Components

### Core Interface
- **`./run`** - Main script for NetHack interaction and session management
  - Manages persistent tmux sessions
  - Sends commands with configurable delays
  - Captures clean ASCII output without escape sequences
  - Appends a neighborhood-of-@ view after the original output
  - Supports session cleanup and initialization
- **`transpose_map.py`** - Screen formatting tool for improved spatial awareness
  - Extracts the map region from NetHack screen output
  - Prints a 5x5 grid and labeled adjacent-cell summary around `@`

### Documentation
- **`CLAUDE.md`** - Gameplay instructions and NetHack knowledge base for Claude


## Current Mission

**Objective**: Navigate Claude (Human Valkyrie) from Dungeon Level 1 to Level 2

**Progress**:
- Successfully explored majority of Level 1 dungeon
- Discovered hidden passages and complex room networks
- Learned advanced combat mechanics through trial and error
- Currently positioned in western room searching for stairs down

## Key Features

### Intelligent Gameplay
- **Strategic character selection**: Evolved from Tourist to Valkyrie for better combat effectiveness
- **Systematic exploration**: Room-by-room mapping with pattern recognition
- **Combat learning**: Tactical improvements based on previous encounters
- **Hidden feature discovery**: Wall pattern analysis to find secret passages

### Technical Implementation
- **Session persistence**: Games survive between command sessions
- **Clean output**: Monochrome ASCII without terminal escape sequences
- **Neighborhood of @**: 5x5 grid and labeled adjacent-cell summary appended to output for quick spatial checks
- **Command batching**: Multiple moves can be sent sequentially
- **Error handling**: Robust session management with cleanup options

### Documentation Excellence
- **Real-time strategy updates**: Every significant decision documented
- **Technical insights**: NetHack mechanics learned through experimentation
- **Progress tracking**: Clear mission status and next steps
- **Learning evolution**: Shows genuine improvement in gameplay understanding

## Quickstart for Claude Code

### What to Tell Claude Code

**For new users - start here:**
```
Continue playing NetHack. Check documents in this project, then proceed with the mission to reach Level 2.
```

**Other useful prompts:**
- `Start a fresh NetHack game and begin the mission to reach Level 2`
- `Review your NetHack strategy and continue exploration`
- `Check your current NetHack progress and next steps`

**Key points:**
- Claude will automatically read `CLAUDE.md` for context
- The mission is to reach Level 2 and more (find stairs down `>`)
- Claude handles all game mechanics - just give the high-level instruction

### Getting Started
1. **Initialize game**: `./run --init` to start fresh session, then manually select `v`, `h`, `l`, and `y`
2. **Check current state**: `./run` (no arguments) to see game screen
3. **Review strategy**: Read `CLAUDE.md` for current mission status and learned tactics
4. **Basic movement**: Use `./run h j k l` for west/south/north/east movement
5. **Door interaction**: Use `./run o` + direction to open doors (`+` symbols)
6. **Search areas**: Use `./run s` to find hidden doors/passages
7. **Mission goal**: Find stairs down (`>`) to reach Level 2

### Essential Commands for Gameplay
```bash
./run                   # View current state
./run h j k l           # Cardinal movement (west/south/north/east)
./run y u b n           # Diagonal movement
./run o h               # Open door to the west
./run s                 # Search for hidden features
./run ,                 # Pick up items
./run '>'               # Go down stairs (when found)
./run '#quit'           # Extended command (Enter is sent automatically)
./run '^P'              # Ctrl+P: view recent messages (C-p also works)
```

### Strategy Reference
- Current character: Claude the Valkyrie (Human) - combat-effective class
- Pet: Slinky (dog) - helps in combat, eats corpses
- Mission: Systematic exploration to find stairs down (`>`)
- Key lesson: Look for wall discontinuities (`.` in `---` patterns) for hidden passages

## Usage

### Session Management
```bash
./run --init            # Start fresh game session
./run --cleanup         # End current session
```

### Monitoring Progress
```bash
# Display game in progress with read-only mode
tmux attach-session -t claude-nethack -r
```

## Understanding the Game Display

When viewing NetHack gameplay, key symbols include:
- **`@`** - Claude's current position
- **`f`** - Pet (Rex the kitten)
- **`<`** - Stairs up
- **`>`** - Stairs down (mission objective!)
- **`#`** - Corridor passages
- **`+`** - Closed doors
- **`$`** - Gold/treasure
- **`%`** - Enemy corpses

### Status Bar
The bottom shows current stats:
- **Character**: "Claude the Stripling" (Valkyrie)
- **Health**: HP current/max (e.g., "HP:16(16)")
- **Gold**: Current amount (e.g., "$:7")
- **Level**: Current dungeon floor (e.g., "Dlvl:1")

## Project Evolution

This project demonstrates AI learning through gameplay:

1. **Initial Phase**: Basic movement and door opening
2. **Exploration Phase**: Systematic room mapping and corridor navigation
3. **Combat Phase**: Enemy encounters leading to character optimization
4. **Advanced Phase**: Hidden passage discovery and complex navigation
5. **Current Phase**: Strategic room-by-room search for mission completion

The documentation shows genuine learning progression, with Claude Code adapting strategies based on gameplay outcomes and developing increasingly sophisticated approaches to NetHack's challenges.

---

*A demonstration of AI autonomous gameplay with comprehensive strategy documentation and technical implementation.*
