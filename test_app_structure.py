#!/usr/bin/env python3
"""
Test the app.py structure to ensure no buttons are inside forms
"""

import re

def test_app_structure():
    """Test that no st.button() calls are inside st.form() blocks"""
    print("Testing app.py structure...")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Find all form blocks
    form_pattern = r'with st\.form\([^)]+\):(.*?)(?=\n\S|\nif|\ndef|\nclass|\Z)'
    forms = re.findall(form_pattern, content, re.DOTALL)
    
    print(f"Found {len(forms)} form blocks")
    
    issues_found = 0
    
    for i, form_content in enumerate(forms):
        # Check for st.button() inside form (but not st.form_submit_button())
        button_pattern = r'st\.button\('
        buttons = re.findall(button_pattern, form_content)
        
        if buttons:
            print(f"❌ Form {i+1} contains {len(buttons)} st.button() calls")
            issues_found += len(buttons)
        else:
            print(f"✅ Form {i+1} is clean (no st.button() calls)")
    
    if issues_found == 0:
        print("\n✅ All forms are properly structured!")
        print("No st.button() calls found inside st.form() blocks")
    else:
        print(f"\n❌ Found {issues_found} issues with buttons inside forms")
    
    return issues_found == 0

if __name__ == "__main__":
    test_app_structure()