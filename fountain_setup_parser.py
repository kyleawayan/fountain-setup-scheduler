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
    
    def _format_output(self, setup_groups: Dict[str, List[SceneContent]]) -> str:
        """Format the reorganized content as Fountain."""
        output = []
        
        # Sort setup letters alphabetically
        for setup_letter in sorted(setup_groups.keys()):
            scenes = setup_groups[setup_letter]
            
            # Add setup heading
            output.append(f'.SETUP {setup_letter}')
            output.append('')
            
            # Add each scene's content
            for scene in scenes:
                # Add synopsis with scene number and full setup description
                scene_label = f'Scene {scene.scene_number}' if scene.scene_number else 'Scene'
                output.append(f'= [ ] From {scene_label} (SETUP {scene.setup.letter}: {scene.setup.description})')
                output.append('')
                
                # Add content lines, removing leading/trailing empty lines and transitions
                content_lines = []
                for line in scene.content_lines:
                    # Skip transition lines (lines ending with "TO:")
                    if line.strip().endswith('TO:'):
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


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Reorganize Fountain screenplay files by camera setup for efficient filming.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Example:
  %(prog)s screenplay.fountain -o reorganized.fountain
  
This will parse screenplay.fountain and create reorganized.fountain with all
content grouped by camera setup (A, B, C, etc.) for efficient filming.
        '''
    )
    
    parser.add_argument(
        'input_file',
        help='Path to the input Fountain file'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='Path to the output file (default: adds "_by_setup" to input filename)'
    )
    
    args = parser.parse_args()
    
    # Generate default output filename if not provided
    if not args.output_file:
        input_parts = args.input_file.rsplit('/', 1)
        if len(input_parts) == 2:
            directory, filename = input_parts
            args.output_file = f'{directory}/SHOTLIST_{filename}'
        else:
            args.output_file = f'SHOTLIST_{args.input_file}'
    
    try:
        # Parse and reorganize the file
        parser = FountainSetupParser()
        reorganized_content = parser.parse_file(args.input_file)
        
        # Write output
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(reorganized_content)
        
        print(f'Successfully reorganized {args.input_file} -> {args.output_file}')
        
    except FileNotFoundError:
        print(f'Error: Could not find input file "{args.input_file}"', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()