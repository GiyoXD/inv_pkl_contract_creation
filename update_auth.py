#!/usr/bin/env python3
"""
Script to update all pages with enhanced authentication
"""

import os
import re
from pathlib import Path

def update_page_auth(file_path, page_name, admin_required=False):
    """Update a single page file with enhanced authentication"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match the old authentication imports and setup
        old_pattern = r'from login import[^)]*\)\s*\n\s*# --- Authentication Check ---\s*\nuser_info = check_authentication\(\)\s*\nif not user_info:\s*\n\s*st\.stop\(\)\s*\n(?:.*?if user_info\[\'role\'\] != \'admin\':\s*\n\s*st\.error\(.*?\)\s*\n\s*st\.stop\(\)\s*\n)?(?:.*?st\.set_page_config\([^)]*\)\s*\n)?(?:.*?show_user_info\(\)\s*\nshow_logout_button\(\)\s*\n)?'
        
        # New authentication setup
        admin_setup = f"""from auth_wrapper import setup_page_auth, show_session_status

# --- Enhanced Authentication Setup ---
user_info = setup_page_auth(
    page_title="{page_name}", 
    page_name="{page_name}",
    admin_required={admin_required},
    layout="wide"
)

# Show session status in sidebar
show_session_status()
"""
        
        regular_setup = f"""from auth_wrapper import setup_page_auth, show_session_status

# --- Enhanced Authentication Setup ---
user_info = setup_page_auth(
    page_title="{page_name}", 
    page_name="{page_name}",
    layout="wide"
)

# Show session status in sidebar
show_session_status()
"""
        
        new_setup = admin_setup if admin_required else regular_setup
        
        # Try to replace the old pattern
        new_content = re.sub(old_pattern, new_setup, content, flags=re.MULTILINE | re.DOTALL)
        
        # If no replacement was made, try a simpler pattern
        if new_content == content:
            # Look for just the authentication check part
            simple_pattern = r'# --- Authentication Check ---\s*\nuser_info = check_authentication\(\)\s*\nif not user_info:\s*\n\s*st\.stop\(\)'
            
            if re.search(simple_pattern, content):
                # Replace just the authentication check
                new_content = re.sub(simple_pattern, f"""# --- Enhanced Authentication Setup ---
user_info = setup_page_auth(
    page_title="{page_name}", 
    page_name="{page_name}",
    admin_required={admin_required},
    layout="wide"
)

# Show session status in sidebar
show_session_status()""", content)
                
                # Also need to update the import
                import_pattern = r'from login import[^)]*\)'
                new_content = re.sub(import_pattern, 'from auth_wrapper import setup_page_auth, show_session_status', new_content)
        
        # Write the updated content back
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Updated {file_path}")
            return True
        else:
            print(f"⚠️  No changes needed for {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Update all page files"""
    pages_dir = Path("pages")
    
    # Define pages and their requirements
    page_configs = {
        "1_Verify_Data_To_Insert.py": ("Add Invoice", False),
        "997_Invoice Explorer.py": ("Invoice Explorer", False),
        "998_Database_Manager.py": ("Database Manager", True),
        "999_Guide.py": ("User Guide", False),
    }
    
    updated_count = 0
    
    for filename, (page_name, admin_required) in page_configs.items():
        file_path = pages_dir / filename
        if file_path.exists():
            if update_page_auth(file_path, page_name, admin_required):
                updated_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n🎉 Updated {updated_count} page files with enhanced authentication!")

if __name__ == "__main__":
    main()