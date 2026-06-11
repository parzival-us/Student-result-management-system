#!/usr/bin/env python3
"""
Setup verification script for Student Result Management System.
Checks dependencies and creates necessary directories.
"""

import sys
import subprocess
import os

def check_python_version():
    """Ensure Python 3.8+ is being used."""
    if sys.version_info < (3, 8):
        print(f"[ERROR] Python 3.8+ required. You have {sys.version}")
        return False
    print(f"[OK] Python version: {sys.version.split()[0]}")
    return True

def check_and_install_dependencies():
    """Check for required packages and install if missing."""
    required = {
        'matplotlib': 'matplotlib>=3.7.0',
        'fpdf': 'fpdf2>=2.7.0',
    }

    missing = []
    for module_name, package_spec in required.items():
        try:
            __import__(module_name)
            print(f"[OK] {package_spec} installed")
        except ImportError:
            print(f"[MISSING] {package_spec} NOT found")
            missing.append(package_spec)

    if missing:
        print(f"\n[INFO] Installing {len(missing)} missing package(s)...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("[OK] Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("[ERROR] Failed to install dependencies. Run: pip install -r requirements.txt")
            return False
    return True

def create_directories():
    """Create necessary directories."""
    dirs = ['exports', 'gui']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print(f"[OK] Directories ready")

def main():
    print("Checking Student Result Management System setup...\n")

    if not check_python_version():
        return False

    print()
    if not check_and_install_dependencies():
        return False

    print()
    create_directories()

    print("\nSetup check complete! You can now run: python main.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
