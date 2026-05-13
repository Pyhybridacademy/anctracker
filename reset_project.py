#!/usr/bin/env python
import os
import shutil
import sys

def reset_project():
    print("🚀 Resetting Logistics Project...")
    
    # Files and folders to delete
    to_delete = [
        'db.sqlite3',
        '__pycache__',
        'core/__pycache__',
        'core/migrations/__pycache__',
        'shipments/__pycache__',
        'shipments/migrations/__pycache__',
        'pages/__pycache__',
        'pages/migrations/__pycache__',
        'config/__pycache__',
    ]
    
    # Delete files
    for item in to_delete:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
                print(f"🗑️  Deleted directory: {item}")
            else:
                os.remove(item)
                print(f"🗑️  Deleted file: {item}")
    
    # Create fresh migration directories
    migrations_dirs = [
        'core/migrations',
        'shipments/migrations',
        'pages/migrations'
    ]
    
    for dir_path in migrations_dirs:
        os.makedirs(dir_path, exist_ok=True)
        # Create __init__.py in migrations directories
        init_file = os.path.join(dir_path, '__init__.py')
        with open(init_file, 'w') as f:
            pass
        print(f"📁 Created: {dir_path}/")
    
    print("\n✅ Reset complete!")
    print("\nNow run these commands:")
    print("1. python manage.py makemigrations")
    print("2. python manage.py migrate")
    print("3. python manage.py createsuperuser")
    print("4. python manage.py setup_initial_data")
    print("5. python manage.py runserver")

if __name__ == '__main__':
    reset_project()