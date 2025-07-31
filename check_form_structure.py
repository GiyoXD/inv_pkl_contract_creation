#!/usr/bin/env python3
"""
Better check for form structure
"""

def check_form_structure():
    """Check form structure more accurately"""
    print("Checking form structure...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        if 'with st.form(' in line:
            form_indent = len(line) - len(line.lstrip())
            print(f"Form starts at line {i} with {form_indent} spaces indentation")
            
            # Look for the end of this form block
            form_ended = False
            for j in range(i, len(lines)):
                next_line = lines[j]
                if next_line.strip():  # Non-empty line
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    # Form ends when we find a line at the same or less indentation
                    if next_indent <= form_indent and j > i:
                        print(f"Form ends at line {j+1}")
                        form_ended = True
                        
                        # Check for buttons between form start and end
                        buttons_in_form = []
                        for k in range(i, j):
                            check_line = lines[k]
                            if 'st.button(' in check_line and 'st.form_submit_button(' not in check_line:
                                buttons_in_form.append(k+1)
                        
                        if buttons_in_form:
                            print(f"❌ Found st.button() at lines: {buttons_in_form}")
                        else:
                            print("✅ No st.button() found inside form")
                        
                        break
            
            if not form_ended:
                print("⚠️  Could not determine form end")

if __name__ == "__main__":
    check_form_structure()