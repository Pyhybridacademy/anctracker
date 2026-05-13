#!/usr/bin/env python
import os
import re

def fix_settings_file():
    settings_file = 'config/settings.py'
    
    if not os.path.exists(settings_file):
        print(f"❌ {settings_file} not found!")
        return False
    
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Fix AUTH_USER_MODEL line
    content = re.sub(
        r"AUTH_USER_MODEL\s*=\s*['\"]users\.CustomUser['\"]",
        "# AUTH_USER_MODEL = 'auth.User'  # Using default Django user",
        content
    )
    
    # Remove 'users' from INSTALLED_APPS
    lines = content.split('\n')
    new_lines = []
    in_installed_apps = False
    
    for line in lines:
        if 'INSTALLED_APPS' in line and '=' in line:
            in_installed_apps = True
            new_lines.append(line)
        elif in_installed_apps:
            if "'users'" in line and not line.strip().startswith('#'):
                # Comment out the line or remove it
                new_lines.append(f"# {line}  # Removed: users app doesn't exist")
            elif line.strip() == ']':
                in_installed_apps = False
                new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    new_content = '\n'.join(new_lines)
    
    # Write fixed content
    with open(settings_file, 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed settings.py file!")
    print("\nChanges made:")
    print("1. Commented out/removed AUTH_USER_MODEL = 'users.CustomUser'")
    print("2. Removed 'users' from INSTALLED_APPS")
    
    return True

if __name__ == '__main__':
    if fix_settings_file():
        print("\n🎉 Now try running:")
        print("python manage.py makemigrations")
        print("python manage.py migrate")
    else:
        print("Failed to fix settings file.")