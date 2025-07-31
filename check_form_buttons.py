#!/usr/bin/env python3
"""
Simple check for buttons inside forms
"""

def check_form_buttons():
    """Check if there are any st.button() calls inside forms"""
    print("Checking for buttons inside forms...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open('app.py', 'r', encoding='latin-1') as f:
            lines = f.readlines()
    
    in_form = False
    form_start_line = 0
    issues = []
    
    for i, line in enumerate(lines, 1):
        # Check for form start
        if 'with st.form(' in line:
            in_form = True
            form_start_line = i
            print(f"Form starts at line {i}")
        
        # Check for form end (dedented line or end of file)
        elif in_form and line.strip() and not line.startswith('    ') and not line.startswith('\t'):
            in_form = False
            print(f"Form ends around line {i}")
        
        # Check for st.button() inside form
        if in_form and 'st.button(' in line and 'st.form_submit_button(' not in line:
            issues.append(f"Line {i}: st.button() found inside form (started at line {form_start_line})")
    
    if issues:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n✅ No st.button() calls found inside forms!")
        return True

if __name__ == "__main__":
    check_form_buttons()