#!/usr/bin/env python3
"""
Fountain Setup Parser - Reorganizes Fountain screenplay files by camera setup for efficient filming.
"""

import re
import sys
import argparse
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Setup:
    """Represents a camera setup with its description."""
    letter: str
    description: str
    
    def __eq__(self, other):
        return self.letter == other.letter and self.description == other.description
    
    def __hash__(self):
        return hash((self.letter, self.description))


@dataclass
class SceneContent:
    """Represents content within a scene."""
    setup: Setup
    scene_number: int
    scene_heading: str
    content_lines: List[str] = field(default_factory=list)


class FountainSetupParser:
    """Parses Fountain files and reorganizes content by camera setup."""
    
    def __init__(self):
        self.setup_pattern = re.compile(r'\[\[SETUP\s+([A-Z]):\s*(.+?)\]\]')
        self.scene_number_pattern = re.compile(r'#(\d+)#')
        
    def parse_file(self, file_path: str) -> str:
        """Parse a Fountain file and return reorganized content."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        scenes = self._extract_scenes(content)
        setup_groups = self._group_by_setup(scenes)
        return self._format_output(setup_groups)
    
    def parse_file_as_screenplay(self, file_path: str) -> str:
        """Parse a Fountain file and return as screenplay with setup headers."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        scenes = self._extract_scenes(content)
        return self._format_as_screenplay(scenes)
    
    def _extract_scenes(self, content: str) -> List[SceneContent]:
        """Extract all scenes with their setups and content."""
        lines = content.split('\n')
        scenes = []
        current_scene_number = None
        current_scene_heading = None
        current_setup = None
        current_content = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check for scene heading
            if self._is_scene_heading(line):
                # Save previous content if exists
                if current_setup and current_content:
                    scenes.append(SceneContent(
                        setup=current_setup,
                        scene_number=current_scene_number,
                        scene_heading=current_scene_heading,
                        content_lines=current_content
                    ))
                    current_content = []
                
                # Reset setup when entering new scene
                current_setup = None
                current_scene_heading = line
                scene_number_match = self.scene_number_pattern.search(line)
                if scene_number_match:
                    current_scene_number = int(scene_number_match.group(1))
                else:
                    # For unnumbered scenes, increment from last number
                    current_scene_number = (current_scene_number or 0) + 1
                i += 1
                continue
            
            # Check for setup marker
            setup_match = self.setup_pattern.match(line)
            if setup_match:
                # Save previous content if exists
                if current_setup and current_content:
                    scenes.append(SceneContent(
                        setup=current_setup,
                        scene_number=current_scene_number,
                        scene_heading=current_scene_heading,
                        content_lines=current_content
                    ))
                    current_content = []
                
                current_setup = Setup(
                    letter=setup_match.group(1),
                    description=setup_match.group(2).strip()
                )
                i += 1
                continue
            
            # Collect content lines
            if current_setup:
                current_content.append(line)
            
            i += 1
        
        # Save final content if exists
        if current_setup and current_content:
            scenes.append(SceneContent(
                setup=current_setup,
                scene_number=current_scene_number,
                scene_heading=current_scene_heading,
                content_lines=current_content
            ))
        
        return scenes
    
    def _is_scene_heading(self, line: str) -> bool:
        """Check if a line is a scene heading."""
        line = line.strip()
        if not line:
            return False
        
        # Check for INT./EXT. scene headings
        if line.upper().startswith(('INT.', 'EXT.', 'INT ', 'EXT ', 'I/E.')):
            return True
        
        # Check for section headings starting with .
        if line.startswith('.'):
            return True
        
        return False
    
    def _group_by_setup(self, scenes: List[SceneContent]) -> Dict[str, List[SceneContent]]:
        """Group scenes by setup letter, maintaining chronological order."""
        setup_groups = defaultdict(list)
        
        for scene in scenes:
            setup_groups[scene.setup.letter].append(scene)
        
        # Sort each group by scene number
        for setup_letter in setup_groups:
            setup_groups[setup_letter].sort(key=lambda x: x.scene_number or 0)
        
        return setup_groups
    
    def _get_scene_suffix(self, scene_setup_count: dict, scene_setup_key: tuple) -> str:
        """Generate disambiguation suffix for scene/setup combination."""
        if scene_setup_key not in scene_setup_count:
            scene_setup_count[scene_setup_key] = 0
            return ''
        else:
            scene_setup_count[scene_setup_key] += 1
            count = scene_setup_count[scene_setup_key]
            
            # Generate suffix: A-Z, then AA-ZZ, then AAA-ZZZ
            if count <= 26:
                return chr(ord('A') + count - 1)
            elif count <= 26 + 26*26:
                count -= 26
                first = (count - 1) // 26
                second = (count - 1) % 26
                return chr(ord('A') + first) + chr(ord('A') + second)
            elif count <= 26 + 26*26 + 26*26*26:
                count -= (26 + 26*26)
                first = (count - 1) // (26 * 26)
                second = ((count - 1) // 26) % 26
                third = (count - 1) % 26
                return chr(ord('A') + first) + chr(ord('A') + second) + chr(ord('A') + third)
            else:
                scene_number, setup_letter = scene_setup_key
                raise ValueError(
                    f"Too many variations of Scene {scene_number}, Setup {setup_letter}. "
                    f"Maximum of {26 + 26*26 + 26*26*26} variations supported."
                )
    
    def _format_output(self, setup_groups: Dict[str, List[SceneContent]]) -> str:
        """Format the reorganized content as Fountain."""
        output = []
        
        # Sort setup letters alphabetically
        for i, setup_letter in enumerate(sorted(setup_groups.keys())):
            scenes = setup_groups[setup_letter]
            
            # Add setup divider (except for the first setup)
            if i > 0:
                output.append('---')
                output.append('')
            
            # Add setup header
            output.append(f'# SETUP {setup_letter}')
            output.append('')
            
            # Track scene/setup combinations for disambiguation
            scene_setup_count = {}
            
            # Add each scene's content
            for scene in scenes:
                # Create key for tracking this scene/setup combination
                scene_setup_key = (scene.scene_number, scene.setup.letter)
                
                # Get disambiguation suffix
                suffix = self._get_scene_suffix(scene_setup_count, scene_setup_key)
                
                # Add scene heading with setup description and marker
                scene_label = f'Scene {scene.scene_number}' if scene.scene_number else 'Scene'
                marker = f'#{scene.scene_number}{scene.setup.letter}{suffix}#'
                output.append(f'.[ ] From {scene_label} (SETUP {scene.setup.letter}: {scene.setup.description}) {marker}')
                output.append('')
                
                # Add content lines, removing leading/trailing empty lines and transitions
                content_lines = []
                for line in scene.content_lines:
                    # Skip transition lines (lines ending with "TO:")
                    if line.strip().endswith('TO:'):
                        continue
                    # Skip synopsis lines (lines starting with "=")
                    if line.strip().startswith('='):
                        continue
                    content_lines.append(line)
                
                # Remove leading/trailing empty lines
                while content_lines and not content_lines[0].strip():
                    content_lines = content_lines[1:]
                while content_lines and not content_lines[-1].strip():
                    content_lines = content_lines[:-1]
                
                output.extend(content_lines)
                output.append('')
        
        return '\n'.join(output)
    
    def _format_as_screenplay(self, scenes: List[SceneContent]) -> str:
        """Format scenes as a screenplay with setup headers in chronological order."""
        output = []
        scene_setup_count = {}
        current_scene_number = None
        
        for scene in scenes:
            # Create key for tracking this scene/setup combination
            scene_setup_key = (scene.scene_number, scene.setup.letter)
            
            # Get disambiguation suffix
            suffix = self._get_scene_suffix(scene_setup_count, scene_setup_key)
            
            # Add setup as scene heading, with scene number if we're starting a new scene
            marker = f'#{scene.scene_number}{scene.setup.letter}{suffix}#'
            if scene.scene_number != current_scene_number:
                scene_prefix = f'SCENE {scene.scene_number} - '
                current_scene_number = scene.scene_number
            else:
                scene_prefix = ''
            
            output.append(f'.{scene_prefix}SETUP {scene.setup.letter}: {scene.setup.description} {marker}')
            output.append('')
            
            # Add content lines (keep all content for screenplay readability)
            content_lines = scene.content_lines
            
            # Remove leading/trailing empty lines
            while content_lines and not content_lines[0].strip():
                content_lines = content_lines[1:]
            while content_lines and not content_lines[-1].strip():
                content_lines = content_lines[:-1]
            
            output.extend(content_lines)
            output.append('')
        
        return '\n'.join(output)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Reorganize Fountain screenplay files by camera setup for efficient filming.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Example:
  %(prog)s screenplay.fountain
  
This will parse screenplay.fountain and create:
- SCHEDULE_screenplay.fountain (grouped by setup for filming)
- SETUPSCREENPLAY_screenplay.fountain (chronological with setup headers)
        '''
    )
    
    parser.add_argument(
        'input_file',
        help='Path to the input Fountain file'
    )
    
    
    args = parser.parse_args()
    
    # Generate output filenames
    input_parts = args.input_file.rsplit('/', 1)
    if len(input_parts) == 2:
        directory, filename = input_parts
        schedule_file = f'{directory}/SCHEDULE_{filename}'
        screenplay_file = f'{directory}/SETUPSCREENPLAY_{filename}'
    else:
        schedule_file = f'SCHEDULE_{args.input_file}'
        screenplay_file = f'SETUPSCREENPLAY_{args.input_file}'
    
    try:
        # Parse and reorganize the file
        parser = FountainSetupParser()
        reorganized_content = parser.parse_file(args.input_file)
        
        # Generate screenplay content
        screenplay_content = parser.parse_file_as_screenplay(args.input_file)
        
        # Write both outputs
        with open(schedule_file, 'w', encoding='utf-8') as f:
            f.write(reorganized_content)
        
        with open(screenplay_file, 'w', encoding='utf-8') as f:
            f.write(screenplay_content)
        
        print(f'Successfully reorganized {args.input_file}:')
        print(f'  Schedule: {schedule_file}')
        print(f'  Screenplay: {screenplay_file}')
        
    except FileNotFoundError:
        print(f'Error: Could not find input file "{args.input_file}"', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()