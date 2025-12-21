#!/usr/bin/env python3
"""Fix CSS files by removing duplicates and fixing variables"""

import re

def fix_css_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove literal `n strings
    content = content.replace('`n', '')
    
    # Remove duplicate --cr-accent-soft and --cr-bg-elevated lines
    lines = content.split('\n')
    seen_vars = set()
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        # Check if it's a CSS variable declaration
        if '--cr-' in stripped and ':' in stripped:
            var_name = stripped.split(':')[0].strip()
            if var_name in seen_vars:
                continue  # Skip duplicate
            seen_vars.add(var_name)
        cleaned_lines.append(line)
    
    content = '\n'.join(cleaned_lines)
    
    # Now add missing variables properly
    # Fix :root
    if '--cr-bg-elevated' not in content.split(':root')[1].split('}')[0]:
        content = content.replace(
            '--cr-bg-panel: #020617;',
            '--cr-bg-panel: #020617;\n    --cr-bg-elevated: #1e293b;'
        )
    if '--cr-accent-soft' not in content.split(':root')[1].split('}')[0]:
        content = re.sub(
            r'(--cr-accent: #667eea;)',
            r'\1\n    --cr-accent-soft: rgba(102, 126, 234, 0.16);',
            content,
            count=1
        )
    
    # Fix .cr-light-mode
    light_mode_start = content.find('.cr-light-mode {')
    if light_mode_start != -1:
        light_mode_end = content.find('}', light_mode_start)
        light_mode_section = content[light_mode_start:light_mode_end]
        
        if '--cr-bg-elevated' not in light_mode_section:
            content = content.replace(
                '--cr-bg-panel: #ffffff;',
                '--cr-bg-panel: #ffffff;\n    --cr-bg-elevated: #f9fafb;',
                1
            )
        if '--cr-accent-soft' not in light_mode_section:
            # Find the --cr-accent line in light mode and add after it
            pattern = r'(\.cr-light-mode \{[\s\S]*?--cr-accent: #667eea;)'
            replacement = r'\1\n    --cr-accent-soft: rgba(102, 126, 234, 0.1);'
            content = re.sub(pattern, replacement, content, count=1)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed {filepath}")

if __name__ == '__main__':
    import sys
    import os
    base = r'c:\Users\Acer\Desktop\Unify\UNIFY\src\static\styles'
    fix_css_file(os.path.join(base, 'settings.css'))
    fix_css_file(os.path.join(base, 'Transcript.css'))
