import os
import sys

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Read settings file
    with open('config/settings.py', 'r') as f:
        content = f.read()
    
    print("🔍 Checking config/settings.py...")
    
    # Check for problematic lines
    problematic_lines = []
    
    if "AUTH_USER_MODEL = 'users." in content:
        print("❌ Found: AUTH_USER_MODEL = 'users...'")
        print("   This should be removed or changed to 'auth.User'")
        problematic_lines.append("AUTH_USER_MODEL")
    
    if "'users'" in content and "'users'" not in "'shipments'":
        print("❌ Found: 'users' in INSTALLED_APPS")
        problematic_lines.append("'users' in INSTALLED_APPS")
    
    if "'users'" in content and not any(x in content for x in ["'users'", "# 'users'", "#'users'"]):
        print("❌ 'users' mentioned in settings but not in INSTALLED_APPS")
    
    # Show INSTALLED_APPS section
    lines = content.split('\n')
    in_installed_apps = False
    print("\n📦 Current INSTALLED_APPS:")
    for i, line in enumerate(lines):
        if 'INSTALLED_APPS' in line and '=' in line:
            in_installed_apps = True
            print(f"Line {i+1}: {line}")
            continue
        if in_installed_apps:
            if line.strip().startswith(']'):
                in_installed_apps = False
                print(f"Line {i+1}: {line}")
                break
            if line.strip() and not line.strip().startswith('#'):
                print(f"Line {i+1}: {line}")
    
    if problematic_lines:
        print(f"\n🚨 Found {len(problematic_lines)} issues:")
        for issue in problematic_lines:
            print(f"  • {issue}")
        print("\n💡 Fix these in config/settings.py and run again.")
    else:
        print("\n✅ No issues found in settings.py!")
        
except FileNotFoundError:
    print("❌ config/settings.py not found!")
except Exception as e:
    print(f"❌ Error: {e}")