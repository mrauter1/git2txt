#!/usr/bin/env python3
"""
Git2Text Setup Verification Script
--------------------------------
This script verifies the system requirements and dependencies for Git2Text.
It checks:
- Python version
- Git installation
- Pathspec library
- Clipboard support (platform-specific)
- PATH configuration

Usage:
    python git2text_setup.py [--install]

Options:
    --install    Automatically install missing dependencies where possible
"""

import sys
import subprocess
import platform
import argparse
from pathlib import Path
import os
import site

class Git2TextSetup:
    def __init__(self, auto_install=False):
        self.auto_install = auto_install
        self.requirements = {
            'python': False,
            'git': False,
            'pathspec': False,
            'clipboard': False
        }

    def check_python_version(self):
        """Verify Python version meets minimum requirements (3.6+)."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 6):
            print("❌ Python version must be 3.6 or higher")
            print(f"Current version: {sys.version}")
            return False
        print(f"✅ Python version {version.major}.{version.minor}.{version.micro} detected")
        self.requirements['python'] = True
        return True

    def check_git(self):
        """Verify Git is installed and accessible."""
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True, check=True)
            print(f"✅ Git is installed ({result.stdout.strip()})")
            self.requirements['git'] = True
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Git is not installed")
            if self.auto_install:
                print("Please install Git manually from: https://git-scm.com/downloads")
            return False

    def check_pathspec(self):
        """Verify pathspec library is installed, install if missing and auto_install is True."""
        try:
            import pathspec
            print(f"✅ pathspec library is installed (version {pathspec.__version__})")
            self.requirements['pathspec'] = True
            return True
        except ImportError:
            print("❌ pathspec library is missing")
            if self.auto_install:
                print("Installing pathspec...")
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pathspec'], check=True)
                    print("✅ pathspec installed successfully")
                    self.requirements['pathspec'] = True
                    return True
                except subprocess.CalledProcessError:
                    print("❌ Failed to install pathspec")
            print("Please run: pip install pathspec")
            return False

    def check_clipboard_support(self):
        """Verify clipboard support for the current platform."""
        system = platform.system()
        if system == "Linux":
            xclip = self._check_linux_clipboard_tool('xclip', '-version')
            xsel = self._check_linux_clipboard_tool('xsel', '--version')
            
            if xclip or xsel:
                self.requirements['clipboard'] = True
                return True
            else:
                print("⚠️  Neither xclip nor xsel is installed")
                if self.auto_install:
                    print("To install clipboard support, run either:")
                    print("  sudo apt-get install xclip")
                    print("  sudo apt-get install xsel")
                return False
        else:
            print(f"✅ Native clipboard support available for {system}")
            self.requirements['clipboard'] = True
            return True

    def _check_linux_clipboard_tool(self, tool, version_flag):
        """Helper method to check Linux clipboard tools."""
        try:
            subprocess.run([tool, version_flag], capture_output=True, check=True)
            print(f"✅ {tool} is installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_path_configuration(self):
        """Verify and optionally fix PATH configuration."""
        scripts_path = site.USER_SITE.replace('site-packages', 'Scripts')
        if platform.system() != 'Windows':
            scripts_path = site.USER_BASE + '/bin'

        paths = os.environ.get('PATH', '').split(os.pathsep)
        if scripts_path in paths:
            print("✅ Scripts directory is in PATH")
            return True
        
        print("⚠️  Scripts directory is not in PATH:", scripts_path)
        if self.auto_install:
            self._add_to_path(scripts_path)
        else:
            print(f"Add this directory to your PATH: {scripts_path}")
        return False

    def _add_to_path(self, scripts_path):
        """Add scripts directory to PATH."""
        system = platform.system()
        if system == "Windows":
            try:
                subprocess.run(['setx', 'PATH', f"%PATH%;{scripts_path}"], check=True)
                print("✅ Added scripts directory to PATH")
                print("Please restart your terminal for changes to take effect")
            except subprocess.CalledProcessError:
                print("❌ Failed to add to PATH automatically")
                print(f"Please add manually: {scripts_path}")
        else:
            shell = os.path.basename(os.environ.get('SHELL', '/bin/bash'))
            rc_file = f"~/.{shell}rc"
            print(f"Add the following line to {rc_file}:")
            print(f'export PATH="$PATH:{scripts_path}"')

    def run_checks(self):
        """Run all verification checks."""
        print("=== Git2Text Setup Verification ===\n")
        
        self.check_python_version()
        self.check_git()
        self.check_pathspec()
        self.check_clipboard_support()
        self.check_path_configuration()
        
        print("\n=== Summary ===")
        if all(self.requirements.values()):
            print("✅ All core requirements met!")
            print("\nGit2Text is ready to use. Try:")
            print("  git2text --help")
        else:
            print("❌ Some requirements are not met:")
            for req, status in self.requirements.items():
                if not status:
                    print(f"  - Missing: {req}")
            print("\nPlease address the issues above before using Git2Text")

def main():
    parser = argparse.ArgumentParser(description="Git2Text Setup Verification")
    parser.add_argument('--install', action='store_true', 
                       help='Attempt to install missing dependencies automatically')
    args = parser.parse_args()

    setup = Git2TextSetup(auto_install=args.install)
    setup.run_checks()

if __name__ == "__main__":
    main()