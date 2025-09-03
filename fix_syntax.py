#!/usr/bin/env python3
"""
Script to fix syntax issues in the deal hub Python file.
This script will:
1. Fix HTML templates mixed with Python code
2. Handle Unicode characters properly
3. Ensure proper string quoting
"""

import re
import sys

def fix_deal_hub_syntax():
    """Fix syntax issues in deal hub.py"""
    
    # Read the file
    with open('deal hub .py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the remaining HTML template sections that aren't properly quoted
    # Pattern 1: Fix template sections that start with {% extends 'base.html' %} but aren't in strings
    
    # Find and fix the property template end
    content = re.sub(
        r"(PROPERTY_HOME_TEMPLATE = r'''.*?)(\n# Enhanced templates - templates/base\.html with navigation\n<!DOCTYPE html)",
        r"\1'''\n\n\2",
        content,
        flags=re.DOTALL
    )
    
    # Fix the second HTML document
    content = re.sub(
        r"(# Enhanced templates - templates/base\.html with navigation\n)(<!DOCTYPE html.*?</html>)",
        r"\1ENHANCED_BASE_TEMPLATE = r'''\2'''",
        content,
        flags=re.DOTALL
    )
    
    # Fix any remaining template sections that aren't properly quoted
    # Find {% extends 'base.html' %} that aren't in strings
    lines = content.split('\n')
    fixed_lines = []
    in_template = False
    template_start_line = None
    
    for i, line in enumerate(lines):
        # Check if this is a template comment followed by template code
        if line.strip().startswith('# templates/') and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line.startswith('{% extends') and 'TEMPLATE = ' not in line:
                # This is an unquoted template section
                template_name = line.split('/')[-1].replace('.html', '').replace('-', '_').upper() + '_TEMPLATE'
                fixed_lines.append(line)
                template_line = template_name + " = r'''{% extends 'base.html' %}"
                fixed_lines.append(template_line)
                in_template = True
                template_start_line = i + 1
                continue
        
        if in_template and line.strip() == '{% endblock %}':
            fixed_lines.append('{% endblock %}\'\'\'')
            in_template = False
            template_start_line = None
            continue
        
        if not in_template or template_start_line == i:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Write the fixed content back
    with open('deal hub .py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed syntax issues in deal hub.py")

if __name__ == '__main__':
    fix_deal_hub_syntax()