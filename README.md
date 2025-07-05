# Fountain Shot List Parser

A Python CLI tool that reorganizes Fountain screenplay files by camera setup for efficient filming.

## Overview

This tool parses Fountain screenplay files containing camera setup annotations and reorganizes the content by setup letter (A, B, C, etc.). This allows film crews to shoot all scenes using the same camera setup together, regardless of their position in the script.

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

The tool reorganizes content by setup letter, maintaining scene context:

```fountain
.SETUP A

= From Scene 1 (SETUP A: Tripod behind booth for wide coverage)

Character walks into frame.

.SETUP B

= From Scene 1 (SETUP B: Handheld close-up)

Insert shot of hands working.
```

## Features

- Groups all content by setup letter (A, B, C, etc.)
- Maintains chronological order within each setup
- Preserves all dialogue, action lines, and sound effects
- Removes transition lines ("CUT TO:", "FADE TO:", etc.) as they don't apply to reorganized content
- Includes full setup descriptions for context
- Handles multiple setup variations (e.g., "SETUP A: wide" vs "SETUP A: close")

## Example Workflow

1. Write your screenplay with setup annotations
2. Run the parser to generate a shot list organized by setup
3. Film all "SETUP A" shots together, then all "SETUP B" shots, etc.
4. Reference scene numbers to maintain story continuity during editing

## License

MIT