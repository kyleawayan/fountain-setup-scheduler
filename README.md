# Fountain Setup Scheduler

A Python CLI tool that reorganizes Fountain screenplay files by camera setup for efficient filming.

## Overview

This tool parses Fountain screenplay files containing camera setup annotations and reorganizes the content by setup letter (A, B, C, etc.). This allows film crews to shoot all scenes using the same camera setup together, regardless of their position in the script.

## Motivation

This tool was created for small-scale video production, particularly for solo creators making content for TikTok, YouTube Shorts, Instagram Reels, and similar platforms. When you're a one-person crew, constantly moving camera setups is time-consuming and disrupts creative flow. 

By reorganizing your script to group all shots from the same camera angle/position together, you can:
- Set up once, shoot multiple scenes
- Minimize equipment adjustments
- Maintain consistent lighting and framing
- Work more efficiently as a solo filmmaker

Instead of following script order and moving your tripod 20 times, you can shoot all "Setup A" content, then move once to "Setup B", and so on.

## Installation

No installation required. Just ensure you have Python 3 installed on your system.

## Usage

```bash
./fountain_setup_parser.py input.fountain -o output.fountain
```

Or with Python:

```bash
python3 fountain_setup_parser.py input.fountain -o output.fountain
```

If no output file is specified, the tool will create a file with "SHOTLIST_" prepended to the input filename:

```bash
./fountain_setup_parser.py screenplay.fountain
# Creates: SHOTLIST_screenplay.fountain
```

## Input Format

The tool looks for setup markers in your Fountain file using the format:

```fountain
[[SETUP A: Description of camera setup]]
```

Example:

```fountain
INT. STUDIO - DAY #1#

[[SETUP A: Tripod behind booth for wide coverage]]
Character walks into frame.

[[SETUP B: Handheld close-up]]
Insert shot of hands working.
```

## Output Format

The tool reorganizes content by setup letter, with clear sections and trackable scene headings:

```fountain
# SETUP A

.[ ] From Scene 1 (SETUP A: Tripod behind booth for wide coverage) #1A#

Character walks into frame.

.[ ] From Scene 2 (SETUP A: Tripod behind booth for wide coverage) #2A#

Character delivers dialogue.

---

# SETUP B

.[ ] From Scene 1 (SETUP B: Handheld close-up) #1B#

Insert shot of hands working.
```

### Scene Numbering

Each scene heading includes a unique marker in the format `#SceneNumberSetupLetter#`:
- `#1A#` = Scene 1, Setup A
- `#1B#` = Scene 1, Setup B  
- `#2A#` = Scene 2, Setup A

This allows quick reference to both the original scene number and the camera setup.

## Features

- Groups all content by setup letter (A, B, C, etc.)
- Maintains chronological order within each setup
- Includes checkboxes `[ ]` for tracking completed shots
- Adds scene/setup markers (e.g., `#1A#`, `#2B#`) for easy reference
- Preserves all dialogue, action lines, and sound effects
- Removes transition lines ("CUT TO:", "FADE TO:", etc.) as they don't apply to reorganized content
- Includes full setup descriptions for context
- Handles multiple setup variations (e.g., "SETUP A: wide" vs "SETUP A: close")

## Example Workflow

1. Write your screenplay with setup annotations
2. Run the parser to generate a shooting schedule organized by setup
3. Film all "SETUP A" shots together, then all "SETUP B" shots, etc.
4. Reference scene numbers to maintain story continuity during editing

## License

MIT
