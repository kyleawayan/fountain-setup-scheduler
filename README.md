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
./fountain_setup_parser.py screenplay.fountain
```

Or with Python:

```bash
python3 fountain_setup_parser.py screenplay.fountain
```

This automatically creates two output files:
- `SCHEDULE_screenplay.fountain` - Reorganized by camera setup for efficient filming
- `SETUPSCREENPLAY_screenplay.fountain` - Chronological screenplay with setup headers

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

## Output Formats

The tool creates two complementary files:

### Schedule Format (`SCHEDULE_*.fountain`)
Reorganized by camera setup for efficient filming:

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

### Screenplay Format (`SETUPSCREENPLAY_*.fountain`)
Chronological script with setup headers:

```fountain
.SCENE 1 - SETUP A: Tripod behind booth for wide coverage #1A#

Character walks into frame.

.SETUP B: Handheld close-up #1B#

Insert shot of hands working.

.SCENE 2 - SETUP A: Tripod behind booth for wide coverage #2A#

Character delivers dialogue.
```

### Scene Numbering

Each scene heading includes a unique marker in the format `#SceneNumberSetupLetter[Suffix]#`:
- `#1A#` = Scene 1, Setup A (first occurrence)
- `#1B#` = Scene 1, Setup B  
- `#2A#` = Scene 2, Setup A

When the same scene has multiple segments with the same setup letter (but different descriptions), disambiguation suffixes are added:
- `#1A#` = First occurrence of Scene 1, Setup A
- `#1AA#` = Second occurrence of Scene 1, Setup A
- `#1AB#` = Third occurrence of Scene 1, Setup A
- ... continues through `#1AZ#`, then `#1AAA#`, `#1AAB#`, etc.

This allows quick reference to both the original scene number and the camera setup while handling complex scenes with multiple setup variations.

## Features

- Groups all content by setup letter (A, B, C, etc.)
- Maintains chronological order within each setup
- Includes checkboxes `[ ]` for tracking completed shots
- Adds scene/setup markers (e.g., `#1A#`, `#2B#`) for easy reference
- Preserves all dialogue, action lines, and sound effects
- Removes transition lines ("CUT TO:", "FADE TO:", etc.) as they don't apply to reorganized content
- Includes full setup descriptions for context
- Handles multiple setup variations with automatic disambiguation (e.g., "SETUP A: wide" vs "SETUP A: close")
- Supports up to 18,278 variations per scene/setup combination using suffix system (A-Z, AA-ZZ, AAA-ZZZ)

## Example Workflow

1. Write your screenplay with setup annotations
2. Run the parser: `python3 fountain_setup_parser.py screenplay.fountain`
3. Use `SCHEDULE_screenplay.fountain` on set to film all "SETUP A" shots together, then all "SETUP B" shots, etc.
4. Use `SETUPSCREENPLAY_screenplay.fountain` as a readable script reference
5. Reference scene markers (e.g., `#1A#`, `#2B#`) to maintain story continuity during editing

## Known Issues

- **SETUPSCREENPLAY format**: Content that appears before the first scene heading in the original screenplay (such as title pages, character lists, or opening credits) is not included in the SETUPSCREENPLAY output. Only content within scenes with setup annotations is processed.

## License

MIT
