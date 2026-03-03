Project Tree:
```
├── .gitignore
├── RAG prompt example.txt
├── README.md
├── install.bat
├── install.py
├── install.sh
├── requirements.txt
├── setup.py
├── skills/
│   └── git2text-extraction/
│       ├── SKILL.md
│       ├── references/
│       │   ├── presets.md
│       │   └── troubleshooting.md
│       └── scripts/
│           └── run_git2text.sh
└── src/
    ├── .globalignore
    ├── __init__.py
    ├── git2text.py
    ├── test_git2text.py
    └── test_skill_git2text_extraction.py
```

# File: .gitignore
```text
.env
output/
*.egg
*.egg-info/
*.eggs/
/src/__pycache__
/src/*.tmp
/dist/
/build/
```
# End of file: .gitignore

# File: RAG prompt example.txt
```text
Objective: Generate a JSON list of relevant files from the provided codebase. This list must contain all the files necessary for a software engineer to use and modify the codebase. Criteria: 
* Include core functionality, architecture and development files. 
* Include the most relevant documentation explaining the above aspects. 
* Include files with relevant examples.
* EXCLUDE non-essential boiler plate code or config files. 
* EXCLUDE non-essential files (e.g., git related files, docker related files, package config, well known standard or common libraries files, etc... ). 
* Output Format: JSON list of filenames, example: ["file1", "file2", "file3"] 

Codebase: 
```
# End of file: RAG prompt example.txt

# File: README.md
```markdown
# Git2Text - Codebase Extraction Utility

Git2Text is a utility that simplifies the process of extracting and formatting the entire structure of a codebase into a single text file. Whether you're working with a local Git project, a remote Git repository, or any other codebase, Git2Text is perfect for copying and pasting your code into ChatGPT or other large language models (LLMs). With Git2Text, you can avoid the hassle of manually copying and pasting the source for LLM consumption.

## Features

- **Extract Complete Codebase**: Convert your entire codebase into a Markdown-formatted text.
- **Support for Local and Remote Repositories**: Work with local directories or clone remote Git repositories on-the-fly.
- **Tree View Representation**: Automatically generate a directory structure to provide context.
- **Code Block Formatting**: Files are formatted with appropriate syntax highlighting for better readability.
- **Easy Copy to Clipboard**: Quickly copy the output for pasting into LLMs like ChatGPT.
- **GLOB Pattern Support**: Use powerful GLOB patterns for fine-grained control over file inclusion and exclusion.
- **.gitignore Integration**: Respect `.gitignore` rules by default, with option to override.
- **Cross-Platform Compatibility**: Works on Windows, macOS, and Linux.

## Prerequisites

- **Python 3.6+**
- **Pathspec** library for `.gitignore` parsing (Install via `pip install pathspec`)
- **Git** (for cloning remote repositories)
- **`xclip` or `xsel` for Clipboard Support on Linux**: If you are using Linux and want clipboard functionality, you need to have either `xclip` or `xsel` installed.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mrauter1/git2text.git
   cd git2text
   ```

### Option 1: Manual Installation

2. Install the package and dependencies:
   ```bash
   python install.py
   ```

   This will install the package and attempt to automatically add the `git2text` executable to your system's PATH.

   If the script cannot automatically modify your PATH, it will prompt you to add it manually or provide instructions for Unix-based systems to create a symlink to `/usr/local/bin`.

### Option 2: Installation Script

Use the provided installation scripts to install the package and ensure `git2text` is added to your system's PATH automatically.

#### Windows
Run the following command in Command Prompt:

```bash
install.bat
```

#### macOS/Linux
Run the following command in your terminal:

```bash
chmod +x install.sh
./install.sh
```

## Usage

Once installed, you can run `git2text` from any terminal or command prompt.

### Running the Script

```bash
git2text <path-or-url> [options]
```

The `<path-or-url>` can be:
- A path to a local directory containing your codebase
- A Git repository URL (e.g., https://github.com/username/repo.git)

### Options

- **`-o, --output`**: Specify the output file path.
- **`-ig, --ignore`**: List of files or directories to ignore (supports GLOB patterns).
- **`-inc, --include`**: List of files or directories to include (supports GLOB patterns). If specified, only these paths will be processed.
- **`-se, --skip-empty-files`**: Skip empty files during extraction.
- **`-cp, --clipboard`**: Copy the generated content to the clipboard.
- **`-igi, --ignoregitignore`**: Ignore the `.gitignore` file when specified.

### Example Usage

#### Extract Entire Codebase from a Local Directory to a Markdown File

```bash
git2text /path/to/local/codebase -o output.md
```

#### Clone and Extract a Remote Git Repository

```bash
git2text https://github.com/username/repo.git -o output.md
```

This command will clone the specified repository to a temporary directory, extract its contents, and save the output to `output.md`.

#### Skip `.gitignore` and Empty Files

```bash
git2text https://github.com/username/repo.git -igi -se -o output.md
```

#### Include Only Specific Files and Copy to Clipboard

```bash
git2text /path/to/codebase -inc "*.py" -cp
```

#### Ignore Specific Files and Directories

```bash
git2text /path/to/codebase -ig "*.log" "__pycache__" -o output.md
```

### .globalignore Support

Git2Text also supports a `.globalignore` file located in the same directory as the `git2text.py` script. This file works similarly to a `.gitignore` file but applies globally across any codebase you process.

If a `.globalignore` file is present, it will be used to exclude files or directories specified in it, in addition to `.gitignore`.

To ignore the `.globalignore` file, use the `-igi` flag:
```bash
git2text /path/to/codebase -igi
```

#### Modifying `.globalignore`
To modify or change the global ignore rules, simply edit the `.globalignore` file located alongside the script. Common entries include ignoring directories like `node_modules/`, `dist/`, and files like `*.log`.

Example `.globalignore`:

```
node_modules/
dist/
*.log
*.tmp
```

## Example Output

The output of **Git2Text** follows a Markdown structure for easy readability. Here's a sample of how it formats the files:

````markdown
├── main.py
├── folder/
│   ├── file.json

# File: main.py
```python
print("Hello, World!")
```
# End of file: main.py
```
# File: folder/file.json
```json
{"name": "example"}
```
# End of file: folder/file.json
````

## Contributing

Feel free to contribute to the project by opening an issue or submitting a pull request. We welcome feedback and suggestions to improve **Git2Text**!

## License

This project is licensed under the MIT License.

## Contact

For any questions or support, please open an issue on the GitHub repository.

```
# End of file: README.md

# File: install.bat
```text
python "%~dp0install.py"
```
# End of file: install.bat

# File: install.py
```python
# File: install.py
import os
import sys
import subprocess
import ctypes
import platform
import sysconfig

def is_admin():
    """Check if the script is running with administrative privileges."""
    if platform.system() == 'Windows':
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.geteuid() == 0

def install_package():
    """Install the package and determine the scripts path."""
    print("Installing the package...")
    try:
        # Determine the directory where install.py is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Absolute path to the package directory
        package_dir = script_dir

        # Ensure pip is available in the current Python interpreter
        try:
            subprocess.run([sys.executable, '-m', 'pip', '--version'], check=True, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print("pip is not available in the current Python environment.")
            print("Please install pip or use a Python interpreter that has pip installed.")
            sys.exit(1)

        # Install the package in editable mode
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', package_dir], check=True)
        print("Package installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing the package: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

    # Determine the possible schemes
    schemes = []

    # Try to find the scripts path where the binary is installed
    binary_name = 'git2text.exe' if platform.system() == 'Windows' else 'git2text'
    scripts_path = None

    # Check standard schemes
    if platform.system() == 'Windows':
        schemes.extend(['nt', 'nt_user', 'nt_venv'])
    else:
        schemes.extend(['posix_prefix', 'posix_user', 'posix_home', 'posix_venv'])

    for scheme in schemes:
        try:
            paths = sysconfig.get_paths(scheme=scheme)
        except KeyError:
            # Scheme not found, skip
            continue
        possible_scripts_path = paths.get('scripts')
        if possible_scripts_path:
            binary_path = os.path.join(possible_scripts_path, binary_name)
            if os.path.exists(binary_path):
                scripts_path = possible_scripts_path
                break

    if not scripts_path:
        print("Warning: Could not find the binary in any standard scripts directories.")
        print(f"Tried schemes: {schemes}")
        return None

    scripts_path = os.path.abspath(scripts_path)
    return scripts_path

def get_environment_variable(variable, scope='user'):
    """Retrieve the value of an environment variable."""
    if platform.system() == 'Windows':
        if scope == 'user':
            return os.environ.get(variable, '')
        elif scope == 'system':
            # Get system environment variable using registry
            import winreg
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
                                    0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, variable)
                return value
            except Exception as e:
                print(f"Error accessing system environment variable {variable}: {e}")
                return ''
    else:
        return os.environ.get(variable, '')

def set_environment_variable(variable, value, scope='user'):
    """Set the value of an environment variable."""
    if platform.system() == 'Windows':
        if scope == 'user':
            command = f'setx {variable} "{value}"'
        elif scope == 'system':
            command = f'setx {variable} "{value}" /M'
        else:
            print("Invalid scope specified.")
            return False
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Successfully updated {variable} in the {scope} environment variables.")
            print("You may need to restart your command prompt or computer for changes to take effect.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while updating {variable}: {e}")
            return False
    else:
        # On Unix-based systems, inform the user to modify their shell profile
        print(f"Please add the following line to your shell profile (~/.bashrc, ~/.zshrc, etc.):")
        print(f'\nexport {variable}="{value}"\n')
        return True

def is_path_in_variable(scripts_path, variable_value):
    """Check if a given path is in the specified environment variable."""
    scripts_path_normalized = os.path.normcase(os.path.normpath(scripts_path.rstrip(os.sep)))
    paths = variable_value.split(os.pathsep)
    paths_normalized = [os.path.normcase(os.path.normpath(p.rstrip(os.sep))) for p in paths]
    return scripts_path_normalized in paths_normalized

def run_as_admin():
    """Re-run the script with administrative privileges."""
    if platform.system() == 'Windows':
        script = sys.argv[0]
        params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
    else:
        args = ['sudo', sys.executable] + sys.argv
        subprocess.check_call(args)

def try_add_path_to_environment_variable(scripts_path, variable, scope):
    """Attempt to add the scripts path to the specified environment variable."""
    if scope == 'user':
        max_path_length = 2047
        path_value = get_environment_variable(variable, scope='user')
    elif scope == 'system':
        max_path_length = 4095
        path_value = get_environment_variable(variable, scope='system')
    else:
        print("Invalid scope specified.")
        return False

    new_path_elements = path_value.split(os.pathsep) if path_value else []
    if scripts_path not in new_path_elements:
        new_path_elements.append(scripts_path)
    new_path = os.pathsep.join(new_path_elements)
    if len(new_path) > max_path_length:
        print(f"Cannot add scripts path to {scope} PATH because it exceeds the maximum length.")
        return False

    print(f"Scripts path is not in the {scope} PATH.")
    privilege_note = " Administrator privileges are required." if scope == 'system' else ""
    choice = input(f"Do you want to add it to the {scope} PATH?{privilege_note} [y/N]: ").strip().lower()
    if choice != 'y':
        print(f"No changes were made to the {scope} PATH.")
        return False

    if scope == 'system' and not is_admin():
        print("Administrator privileges are required to modify the system PATH.")
        run_as_admin()
        sys.exit()

    success = set_environment_variable(variable, new_path, scope)
    return success

def check_and_add_scripts_path_windows(scripts_path):
    """Check and add the scripts path to the PATH environment variable on Windows."""
    user_path = get_environment_variable('PATH', scope='user')
    system_path = get_environment_variable('PATH', scope='system')

    in_user_path = is_path_in_variable(scripts_path, user_path)
    in_system_path = is_path_in_variable(scripts_path, system_path)

    if in_user_path or in_system_path:
        location = 'user PATH' if in_user_path else 'system PATH'
        print(f"Scripts path is already in the {location}. No changes needed.")
        return

    if try_add_path_to_environment_variable(scripts_path, 'PATH', scope='user'):
        print("Scripts path successfully added to the user PATH.")
    elif try_add_path_to_environment_variable(scripts_path, 'PATH', scope='system'):
        print("Scripts path successfully added to the system PATH.")
    else:
        print("The script path was not added to PATH variable. Please consider adding the script path to PATH manually.")
        print(f"Script path: {scripts_path}")

def check_and_create_symlink_unix(scripts_path):
    """Check and create a symlink to git2text in /usr/local/bin on Unix-based systems."""
    git2text_script = os.path.join(scripts_path, 'git2text')
    target_path = '/usr/local/bin/git2text'

    if os.path.exists(target_path):
        print(f"{target_path} already exists.")
        return

    print(f"{target_path} does not exist.")
    choice = input("Do you want to create a symlink to git2text in /usr/local/bin? [y/N]: ").strip().lower()
    if choice != 'y':
        print("No changes were made.")
        return

    if not is_admin():
        print("Root privileges are required to create a symlink in /usr/local/bin.")
        run_as_admin()
        sys.exit()

    try:
        if os.path.islink(target_path) or os.path.exists(target_path):
            overwrite = input(f"A file already exists at {target_path}. Do you want to overwrite it? [y/N]: ").strip().lower()
            if overwrite != 'y':
                print("No changes were made.")
                return
            else:
                os.remove(target_path)
        os.symlink(git2text_script, target_path)
        print(f"Successfully created symlink to git2text at {target_path}")
    except Exception as e:
        print(f"An error occurred while creating symlink: {e}")

def main():
    # Detect if running in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        in_virtual_env = True
    else:
        in_virtual_env = False

    if in_virtual_env:
        print("\nWarning: You are about to install git2text inside a virtual environment.")
        print("The git2text CLI tool will not be available globally once the virtual environment is deactivated.")
        choice = input("Do you want to continue with the installation? [y/N]: ").strip().lower()
        if choice != 'y':
            print("Installation aborted by user.")
            sys.exit(0)

    scripts_path = install_package()
    if scripts_path is None:
        sys.exit(1)
    print(f"Python Scripts path: {scripts_path}")

    if platform.system() == 'Windows':
        check_and_add_scripts_path_windows(scripts_path)
    else:
        check_and_create_symlink_unix(scripts_path)

if __name__ == '__main__':
    main()
```
# End of file: install.py

# File: install.sh
```bash
#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0" || realpath "$0")")
python3 "$SCRIPT_DIR/install.py"
```
# End of file: install.sh

# File: requirements.txt
```text
pathspec>=0.11,<1.0
```
# End of file: requirements.txt

# File: setup.py
```python
from setuptools import setup, find_packages

setup(
    name="git2text",
    version="0.1",
    description="A utility to extract and format a codebase into Markdown format",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Marcelo Rauter",
    author_email="marcelorauter2@gmail.com",
    url="https://github.com/mrauter1/git2text",
    packages=find_packages(where="src"),  # Looks for Python packages in the 'src' directory
    package_dir={"": "src"},  # Specifies that the root package is located in 'src'
    py_modules=['git2text'],  # Since git2text.py is directly under src, we treat it as a module
    install_requires=[
        'pathspec',
    ],
    entry_points={
        'console_scripts': [
            'git2text=git2text:main',  # Points to 'main' inside git2text.py
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
```
# End of file: setup.py

# File: skills/git2text-extraction/SKILL.md
```markdown
---
name: git2text-extraction
description: Use this skill when a user wants to export a local codebase or remote git repository into a single markdown text artifact for LLM context, including include/ignore glob filtering, .gitignore control, and optional clipboard copy.
---

# Git2Text Extraction

## When to use
- User asks to export, flatten, snapshot, or package a repo/folder for LLM ingestion.
- User needs one markdown artifact containing a project tree and file contents.

## Inputs to collect
- Source path or git URL.
- Output file path (`-o`) if the user wants to save output to a file.
- Include globs (`-inc`) and/or ignore globs (`-ig`).
- Whether to ignore `.gitignore` (`-igi`).
- Whether to skip empty files (`-se`).
- Whether to copy output to clipboard (`-cp`).

## Core workflow
1. Confirm source type:
   - Local path exists, or
   - Remote URL ends with `.git` (or is a valid clone URL).
2. Build the command incrementally starting from:
   - `skills/git2text-extraction/scripts/run_git2text.sh <source>`
3. Append options only as requested.
4. Execute command.
5. Validate result:
   - Prefer `--require-output <path>` when `-o` is used.
   - Report the exact command and output path.

## Command templates
- Full export to file:
  - `skills/git2text-extraction/scripts/run_git2text.sh --require-output output.md <source> -o output.md`
- Include-only extraction:
  - `skills/git2text-extraction/scripts/run_git2text.sh --require-output output.md <source> -inc "*.py" -o output.md`
- Ignore patterns:
  - `skills/git2text-extraction/scripts/run_git2text.sh --require-output output.md <source> -ig "*.log" "__pycache__" -o output.md`
- Ignore `.gitignore` and skip empty files:
  - `skills/git2text-extraction/scripts/run_git2text.sh --require-output output.md <source> -igi -se -o output.md`
- Validate command plan only (no execution):
  - `skills/git2text-extraction/scripts/run_git2text.sh --dry-run <source> -inc "*.py" -o output.md`

## References
- Presets and copy-ready command recipes: `references/presets.md`
- Failure modes and fixes: `references/troubleshooting.md`

## Notes
- Prefer small include sets when users care about token budget.
- If user needs clipboard output on Linux, remind them `xclip` or `xsel` may be required.
```
# End of file: skills/git2text-extraction/SKILL.md

# File: skills/git2text-extraction/references/presets.md
```markdown
# Presets

## Minimal local export
```bash
skills/git2text-extraction/scripts/run_git2text.sh --require-output repo_dump.md /path/to/repo -o repo_dump.md
```

## Remote repository export
```bash
skills/git2text-extraction/scripts/run_git2text.sh --require-output repo_dump.md https://github.com/owner/repo.git -o repo_dump.md
```

## Python-only snapshot
```bash
skills/git2text-extraction/scripts/run_git2text.sh --require-output python_only.md /path/to/repo -inc "*.py" -o python_only.md
```

## Docs-only snapshot
```bash
skills/git2text-extraction/scripts/run_git2text.sh --require-output docs_only.md /path/to/repo -inc "*.md" "*.txt" -o docs_only.md
```

## Exclude noisy files
```bash
skills/git2text-extraction/scripts/run_git2text.sh --require-output clean_dump.md /path/to/repo -ig "*.log" "*.tmp" "node_modules/" -o clean_dump.md
```

## Ignore .gitignore and skip empty files
```bash
skills/git2text-extraction/scripts/run_git2text.sh --require-output exhaustive_nonempty.md /path/to/repo -igi -se -o exhaustive_nonempty.md
```

## Clipboard-first workflow
```bash
skills/git2text-extraction/scripts/run_git2text.sh /path/to/repo -inc "*.py" -cp
```

## Validate command only (no execution)
```bash
skills/git2text-extraction/scripts/run_git2text.sh --dry-run /path/to/repo -inc "*.py" -o dry_run.md
```
```
# End of file: skills/git2text-extraction/references/presets.md

# File: skills/git2text-extraction/references/troubleshooting.md
```markdown
# Troubleshooting

## `git2text: command not found`
- Ensure package install completed.
- Re-open shell so updated PATH is loaded.
- The wrapper script auto-falls back to `python -m src.git2text` (or `python3 -m src.git2text`) when `git2text` is not on PATH.
- Use `--dry-run` first to validate command composition without executing.

## Clipboard option fails on Linux
- Install one of:
  - `xclip`
  - `xsel`

## Output file is unexpectedly large
- Narrow scope with `-inc`.
- Add excludes via `-ig`.
- Use `-se` to skip empty files.

## Output validation failed (`--require-output`)
- Confirm you passed `-o <same-path>` in git2text options.
- Ensure destination directory exists and is writable.
- Re-run with `--dry-run` to verify argument order.

## Unexpected files missing
- Check `.gitignore` influence.
- Re-run with `-igi` to bypass `.gitignore` and `.globalignore` handling.

## Slow run on very large repositories
- Use include-first strategy (`-inc`) with only needed extensions.
- Exclude generated directories (`-ig "dist/" "build/" "node_modules/"`).
```
# End of file: skills/git2text-extraction/references/troubleshooting.md

# File: skills/git2text-extraction/scripts/run_git2text.sh
```bash
#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
Usage: run_git2text.sh [--dry-run] [--require-output <path>] <source> [git2text options...]

Options:
  --dry-run                Print composed command without executing git2text.
  --require-output <path>  Validate output file exists and is non-empty after execution.
USAGE
}

is_remote_source() {
  case "$1" in
    http://*|https://*|ssh://*|git@*|*.git)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

DRY_RUN=0
REQUIRE_OUTPUT=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --require-output)
      if [ "$#" -lt 2 ]; then
        echo "Error: --require-output requires a path argument." >&2
        usage
        exit 2
      fi
      REQUIRE_OUTPUT="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      break
      ;;
    *)
      break
      ;;
  esac
done

if [ "$#" -lt 1 ]; then
  usage
  exit 2
fi

SOURCE="$1"
shift

if ! is_remote_source "$SOURCE" && [ ! -e "$SOURCE" ]; then
  echo "Error: source does not exist: $SOURCE" >&2
  exit 2
fi

if command -v git2text >/dev/null 2>&1; then
  CMD=(git2text "$SOURCE" "$@")
elif command -v python >/dev/null 2>&1; then
  CMD=(python -m src.git2text "$SOURCE" "$@")
elif command -v python3 >/dev/null 2>&1; then
  CMD=(python3 -m src.git2text "$SOURCE" "$@")
else
  echo "Error: could not find 'git2text', 'python', or 'python3' to execute git2text." >&2
  exit 127
fi

echo "Running: ${CMD[*]}"

if [ "$DRY_RUN" -eq 1 ]; then
  exit 0
fi

"${CMD[@]}"

if [ -n "$REQUIRE_OUTPUT" ]; then
  if [ ! -s "$REQUIRE_OUTPUT" ]; then
    echo "Error: required output is missing or empty: $REQUIRE_OUTPUT" >&2
    exit 1
  fi
  echo "Validated output: $REQUIRE_OUTPUT"
fi
```
# End of file: skills/git2text-extraction/scripts/run_git2text.sh

# File: src/.globalignore
```text
# Directories
node_modules/
dist/
build/
out/
coverage/
.idea/
.vscode/
.DS_Store
__pycache__/
*.egg-info/
*.eggs/
.env/
.venv/
logs/
tmp/
.cache/
target/
bin/
obj/

# Operating System files
Thumbs.db
.DS_Store
*.swp
*.swo
*.swn

# Dependency directories (language-specific)
vendor/
bower_components/
pip-wheel-metadata/
jspm_packages/

# Compiled binary files
*.class
*.o
*.so
*.dll
*.exe
*.out
*.a
*.dylib

# Compiled source
*.pyc
*.pyo
*.pyd
*.exe
*.app
*.o
*.obj
*.class
*.jar

# Logs and databases
*.log
*.sql
*.sqlite
*.sqlite3
*.db

# Package files
*.gem
*.jar
*.war
*.ear
*.tgz
*.tar.gz
*.zip
*.rar
*.7z

# Archives
*.tar
*.zip
*.gz
*.bz2
*.xz

# IDE-specific files
*.iml
*.ipr
*.iws
*.sublime-workspace
*.sublime-project

# Lock files
package-lock.json
yarn.lock
pipfile.lock
pnpm-lock.yaml

# Others
*.bak
*.tmp
*.temp
*.~*
```
# End of file: src/.globalignore

# File: src/__init__.py
```python

```
# End of file: src/__init__.py

# File: src/git2text.py
```python
# main.py
import os
import sys
import argparse
import subprocess
import io  # To handle in-memory text streams
import tempfile
import shutil
import stat  # For handling file permissions on Windows

try:
    import pathspec  # For parsing .gitignore files
except ImportError:
    pathspec = None  # Will check if pathspec is available later

# --- Helper Functions (mostly unchanged unless noted) ---

def get_language_from_extension(file_path: str) -> str:
    # Mapping of file extensions to Markdown code block language identifiers
    extension_to_language = {
        '.py': 'python', '.js': 'javascript', '.html': 'html', '.css': 'css',
        '.java': 'java', '.cpp': 'cpp', '.c': 'c', '.cs': 'csharp',
        '.rb': 'ruby', '.php': 'php', '.ts': 'typescript', '.json': 'json',
        '.md': 'markdown', '.xml': 'xml', '.sh': 'bash', '.yaml': 'yaml',
        '.yml': 'yaml', '.sql': 'sql', '.go': 'go', '.rs': 'rust',
        '.kt': 'kotlin', '.swift': 'swift', '.pl': 'perl', '.lua': 'lua',
        # Add more mappings as needed
    }
    _, extension = os.path.splitext(file_path)
    return extension_to_language.get(extension.lower(), 'text') # Use lower() for case-insensitivity

# --- Tree Building ---

def build_tree_from_paths(relative_paths: list, git_path: str) -> dict:
    """Builds a directory tree structure from a list of relative file paths."""
    tree_dict = {}
    sorted_paths = sorted(relative_paths) # Sort for consistent tree structure

    for rel_path in sorted_paths:
        # Normalize path separators for internal consistency
        parts = rel_path.replace('\\', '/').split('/')
        current_level = tree_dict
        full_path_so_far = git_path

        # Create directory nodes
        for part in parts[:-1]:
            full_path_so_far = os.path.join(full_path_so_far, part)
            if part not in current_level:
                current_level[part] = {'path': full_path_so_far, 'is_dir': True, 'children': {}}
            # Handle cases where a file might have the same name as an already added directory part (unlikely but possible)
            elif not current_level[part]['is_dir']:
                 # Keep essential warnings
                 print(f"Warning: Path conflict detected for {part}. Treating as directory.")
                 current_level[part]['is_dir'] = True
                 if 'children' not in current_level[part]:
                     current_level[part]['children'] = {}
            current_level = current_level[part]['children']

        # Add the file node
        file_name = parts[-1]
        if file_name: # Ensure there's a filename
            full_file_path = os.path.join(full_path_so_far, file_name)
            current_level[file_name] = {'path': full_file_path, 'is_dir': False} # Files don't have children in this context

    return tree_dict

def write_tree_from_paths(output_handle, tree_dict: dict):
    """Writes the pre-built tree dictionary to the output handle."""
    tree_str = format_tree(tree_dict)
    output_handle.write("Project Tree:\n")
    output_handle.write("```\n") # Use a code block for the tree
    output_handle.write(tree_str.rstrip('\r\n') + '\n')
    output_handle.write("```\n\n")

# Modified build_tree to use ignore_spec
def build_tree(directory, tree_dict, ignore_spec, git_path):
    """Builds the tree dictionary for general case (no -inc), respecting ignore_spec."""
    try:
        items = os.listdir(directory)
    except PermissionError:
        # Keep essential warnings
        print(f"Warning: Permission denied: {directory}. Skipping directory.")
        return
    except FileNotFoundError:
        # Keep essential warnings
        print(f"Warning: Directory not found: {directory}. Skipping.")
        return

    items.sort()
    for item in items:
        path = os.path.join(directory, item)
        relative_path = os.path.relpath(path, git_path)

        # Always ignore .git
        if relative_path == '.git' or relative_path.startswith('.git' + os.sep):
            continue

        # Check against ignore spec
        if ignore_spec and ignore_spec.match_file(relative_path):
            continue
        try:
            # Check dirs with trailing slash, but handle potential errors during isdir check early
            if os.path.isdir(path):
                if ignore_spec and ignore_spec.match_file(relative_path + '/'):
                    continue
                # If not ignored directory:
                tree_dict[item] = {'path': path, 'is_dir': True, 'children': {}}
                build_tree(path, tree_dict[item]['children'], ignore_spec, git_path)
                # Prune empty directories after recursion
                if not tree_dict[item]['children']:
                    del tree_dict[item]
            # Check if it's a file *after* ignore checks (if it wasn't an ignored dir)
            elif os.path.isfile(path): # Check only if it's not an ignored dir
                 tree_dict[item] = {'path': path, 'is_dir': False}
        except OSError as e: # Handle potential errors like broken symlinks or permission errors during isdir/isfile
             # Keep essential warnings
             print(f"Warning: Cannot determine type of or access {path}. Skipping. Error: {e}")
             continue


def format_tree(tree_dict, padding=''):
    """Formats the tree dictionary into a string representation."""
    lines = ''
    if not tree_dict:
        return lines
    items = list(tree_dict.items())
    last_index = len(items) - 1

    for index, (name, node) in enumerate(items):
        connector = '└──' if index == last_index else '├──'
        line_prefix = f"{padding}{connector} "
        lines += f"{line_prefix}{name}"

        if node['is_dir']:
            lines += "/\n"
            new_padding = padding + ("    " if index == last_index else "│   ")
            lines += format_tree(node['children'], new_padding)
        else:
            lines += "\n" # Just the filename on the line

    return lines

# Modified write_tree_to_file to use ignore_spec
def write_full_tree_to_file(directory, output_handle, ignore_spec):
    """Builds and writes the full directory tree, respecting ignores."""
    tree_dict = {}
    # REMOVED print("Building directory tree...")
    build_tree(directory, tree_dict, ignore_spec, directory)
    # REMOVED print("Formatting tree...")
    tree_str = format_tree(tree_dict)
    output_handle.write("Project Tree:\n")
    output_handle.write("```\n") # Use a code block for the tree
    output_handle.write(tree_str.rstrip('\r\n') + '\n')
    output_handle.write("```\n\n")

# --- File Processing ---

def append_to_file_markdown_style(relative_path: str, file_content: str, output_handle) -> None:
    language = get_language_from_extension(relative_path)
    relative_path_display = relative_path.replace('\\', '/') # Consistent separators in output
    output_handle.write(f"# File: {relative_path_display}\n```{language}\n")
    output_handle.write(file_content)
     # Ensure final newline if file doesn't end with one, before closing backticks
    if not file_content.endswith('\n'):
        output_handle.write('\n')
    output_handle.write(f"```\n# End of file: {relative_path_display}\n\n")


def append_file_content(full_path: str, git_path: str, output_handle, skip_empty_files: bool) -> None:
    """Reads a single file and appends its content to the output handle."""
    # Check if the file is empty and should be skipped
    try:
        # Use os.stat to avoid race condition between getsize and open
        file_stat = os.stat(full_path)
        if skip_empty_files and file_stat.st_size == 0:
            # Keep essential warnings/info
            # print(f'Skipping empty file: {os.path.relpath(full_path, git_path)}')
            return
    except OSError as e:
        # Keep essential warnings
        print(f'Warning: Cannot get stat of {full_path}. Skipping file. Error: {e}')
        return

    # Determine the relative path of the file to use as a header
    relative_path = os.path.relpath(full_path, start=git_path)

    # Try to read the file with UTF-8 encoding, skip if it fails
    try:
        with open(full_path, 'r', encoding='utf-8', errors='replace') as f: # Use 'replace' for robustness
            file_content = f.read()
    except PermissionError:
        # Keep essential warnings
        print(f'Warning: Permission denied: {relative_path}. Skipping file.')
        return
    except OSError as e: # Catch other potential file reading errors
         # Keep essential warnings
         print(f'Warning: Error reading {relative_path}. Skipping file. Error: {e}')
         return
    except Exception as e: # Catch unexpected errors
        # Keep essential warnings
        print(f'Warning: Unexpected error reading {relative_path}. Skipping file. Error: {e}')
        return

    # Append the content in Markdown style
    append_to_file_markdown_style(relative_path, file_content, output_handle)


def find_matching_files(git_path: str, include_spec, ignore_spec) -> list:
    """
    Walks the directory tree and returns a list of relative paths that
    match include_spec and do not match ignore_spec.
    Uses pathspec for matching, mimicking gitignore behavior.
    """
    matched_files = []
    # REMOVED print("Scanning files...")
    for root, dirs, files in os.walk(git_path, topdown=True):
        original_dirs = list(dirs)
        dirs[:] = []

        for d in original_dirs:
            dir_full_path = os.path.join(root, d)
            dir_relative_path = os.path.relpath(dir_full_path, git_path).replace('\\', '/')

            if dir_relative_path == '.git' or dir_relative_path.startswith('.git/'):
                continue

            try:
                # Check if the directory itself is ignored (match with trailing slash)
                # Need to ensure it's actually a directory first to avoid errors on non-dirs
                # and apply ignore_spec correctly. Check this *before* deciding to descend.
                is_dir_check = os.path.isdir(dir_full_path) # Check once
            except OSError:
                continue # Skip if cannot check type

            if is_dir_check and ignore_spec and ignore_spec.match_file(dir_relative_path + '/'):
                continue # Don't add to dirs list, os.walk won't descend

            # If not ignored, allow os.walk to descend into it
            dirs.append(d)


        # Process files in the current directory
        for file in files:
            file_full_path = os.path.join(root, file)
            file_relative_path = os.path.relpath(file_full_path, git_path).replace('\\', '/')

            if file_relative_path.startswith('.git/'):
                 continue

            # 1. Check if ignored
            if ignore_spec and ignore_spec.match_file(file_relative_path):
                continue

            # 2. Check if included (only if include_spec is provided)
            if include_spec:
                if include_spec.match_file(file_relative_path):
                    matched_files.append(file_relative_path)
            else:
                 matched_files.append(file_relative_path)

    # REMOVED print(f"Found {len(matched_files)} matching files.")
    return sorted(matched_files)

# --- Clipboard and Git Handling (mostly unchanged) ---

def copy_to_clipboard_content(content: str) -> None:
    """Copy the given content to the clipboard."""
    try:
        if sys.platform == "win32":
            process = subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            process.communicate(input=content.encode('utf-16le')) # Windows clip uses UTF-16LE
        elif sys.platform == "darwin":
            process = subprocess.Popen('pbcopy', stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            process.communicate(input=content.encode('utf-8'))
        elif sys.platform.startswith("linux"):
            try:
                process = subprocess.Popen(['xclip', '-selection', 'clipboard', '-in'], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                process.communicate(input=content.encode('utf-8'))
            except FileNotFoundError:
                try:
                    process = subprocess.Popen(['xsel', '--clipboard', '--input'], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    process.communicate(input=content.encode('utf-8'))
                except FileNotFoundError:
                    # Keep essential warnings/errors
                    print("Clipboard functionality requires 'xclip' or 'xsel'. Please install.")
        else:
            # Keep essential warnings/errors
            print(f"Clipboard functionality not supported on {sys.platform}.")
    except Exception as e:
        # Keep essential warnings/errors
        print(f"Error copying to clipboard: {e}")

def copy_to_clipboard_file(output_file_path: str) -> None:
    """Copy the content of the output file to the clipboard."""
    try:
        with open(output_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        copy_to_clipboard_content(content)
    except FileNotFoundError:
        # Keep essential warnings/errors
        print(f"Error: Output file not found for copying: {output_file_path}")
    except Exception as e:
        # Keep essential warnings/errors
        print(f"Error reading output file for copying: {e}")


def is_git_url(path: str) -> bool:
    """Check if the given path is a git URL."""
    git_url_prefixes = ['http://', 'https://', 'git@', 'ssh://', 'git://', 'file://']
    return any(path.startswith(prefix) for prefix in git_url_prefixes) or path.endswith('.git')


def on_rm_error(func, path, exc_info):
    """Error handler for shutil.rmtree, attempts to fix permissions on Windows."""
    if not os.access(path, os.W_OK) and sys.platform == 'win32':
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
             # Keep essential warnings/errors
             print(f"Error: Failed to change permissions or retry deletion for {path}: {e}")
             raise exc_info[1]
    else:
        raise exc_info[1]


# --- Main Execution Logic ---

def main():
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(
        description='Consolidate project files into a single text file or clipboard, with Git-like filtering.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # Keep epilog for help message
        epilog="""Examples:
  # Process current directory, output to file, copy to clipboard
  %(prog)s . -o output.txt -cp

  # Process specific python files recursively, ignoring empty ones
  %(prog)s . -inc "*.py" --skip-empty-files -o python_code.md

  # Process directory, ignoring logs and build files (like .gitignore)
  %(prog)s /path/to/project -ig "*.log" -ig "build/" -o project_src.txt

  # Clone a repo, process only JS files, copy to clipboard
  %(prog)s https://github.com/user/repo.git -inc "**/*.js" -cp

  # Ignore the project's .gitignore file
  %(prog)s . --ignoregitignore -o everything.txt
"""
    )
    parser.add_argument('path', help='Path to the project directory or a git repository URL.')
    parser.add_argument('-o', '--output', help='Output file path. If omitted, output goes to clipboard.')
    parser.add_argument('-ig', '--ignore', nargs='*', default=[], help='List of patterns to ignore (Git-style). Applied after .gitignore.')
    parser.add_argument('-inc', '--include', nargs='*', default=None, help='List of patterns to include (Git-style). If specified, only matching files are processed.')
    parser.add_argument('-se', '--skip-empty-files', action='store_true', help='Skip files with zero size.')
    parser.add_argument('-cp', '--clipboard', action='store_true', help='Copy the output to clipboard. Default if -o is omitted.')
    parser.add_argument('-igi', '--ignoregitignore', action='store_true', help='Ignore project\'s .gitignore and script\'s .globalignore files.')
    args = parser.parse_args()

    # --- Initial Setup ---
    if pathspec is None and not args.ignoregitignore:
        # Keep essential errors
        print("Error: 'pathspec' library is required for Git-style filtering.")
        print("Install it using 'pip install pathspec'")
        print("Alternatively, use the --ignoregitignore flag to skip .gitignore processing.")
        sys.exit(1)

    git_path_arg = args.path
    temp_dir = None
    original_dir = os.getcwd()

    try:
        # --- Handle Path Argument (Local Dir or Git URL) ---
        if is_git_url(git_path_arg):
            # REMOVED print(f"Cloning repository: {git_path_arg}")
            temp_dir = tempfile.mkdtemp(prefix="git2text_")
            # REMOVED print(f"Cloning into temporary directory: {temp_dir}")
            # Redirect stdout/stderr of git clone to suppress its output
            clone_cmd = ['git', 'clone', '--depth', '1', '--quiet', git_path_arg, temp_dir]
            try:
                # Use DEVNULL to suppress output, check=True handles errors
                subprocess.run(clone_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                git_path = temp_dir
                # REMOVED print("Clone successful.")
            except subprocess.CalledProcessError as e:
                 # Keep essential errors
                print(f'Error cloning repository (ensure URL is correct and you have access): {git_path_arg}')
                # Stderr might be useful for debugging clone issues
                # print(f"Stderr: {e.stderr}") # Optional: uncomment for debugging clone errors
                if temp_dir and os.path.exists(temp_dir):
                     shutil.rmtree(temp_dir, onerror=on_rm_error)
                sys.exit(1)
            except FileNotFoundError:
                 # Keep essential errors
                print("Error: 'git' command not found. Please ensure Git is installed and in your PATH.")
                if temp_dir and os.path.exists(temp_dir):
                     shutil.rmtree(temp_dir, onerror=on_rm_error)
                sys.exit(1)
        elif os.path.isdir(git_path_arg):
            git_path = os.path.abspath(git_path_arg)
            # REMOVED print(f"Processing directory: {git_path}")
        else:
            # Keep essential errors
            print(f'Error: Path not found or not a valid directory/git URL: {git_path_arg}')
            sys.exit(1)

        os.chdir(git_path)

        # --- Build Ignore Specification ---
        all_ignore_patterns = []
        ignore_spec = None

        if not args.ignoregitignore and pathspec:
            gitignore_path = os.path.join(git_path, '.gitignore')
            if os.path.exists(gitignore_path):
                try:
                    with open(gitignore_path, 'r', encoding='utf-8') as f:
                        # REMOVED print("Reading .gitignore")
                        all_ignore_patterns.extend(f.read().splitlines())
                except Exception as e:
                     # Keep essential warnings
                    print(f"Warning: Could not read .gitignore: {e}")

            script_dir = os.path.dirname(os.path.realpath(sys.argv[0])) # Use sys.argv[0] for script path
            globalignore_path = os.path.join(script_dir, '.globalignore')
            if os.path.exists(globalignore_path):
                 try:
                    with open(globalignore_path, 'r', encoding='utf-8') as f:
                         # REMOVED print("Reading .globalignore")
                         all_ignore_patterns.extend(f.read().splitlines())
                 except Exception as e:
                      # Keep essential warnings
                     print(f"Warning: Could not read .globalignore: {e}")

        if args.ignore:
            # REMOVED print(f"Adding command line ignore patterns: {args.ignore}")
            all_ignore_patterns.extend(args.ignore)

        if all_ignore_patterns and pathspec:
            try:
                 cleaned_patterns = [p for p in all_ignore_patterns if p.strip() and not p.strip().startswith('#')]
                 ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', cleaned_patterns)
                 # REMOVED print(f"Compiled {len(cleaned_patterns)} ignore patterns.")
            except Exception as e:
                # Keep essential errors
                print(f"Error creating ignore specification: {e}")
                sys.exit(1)
        # REMOVED elif args.ignoregitignore: print("Ignoring .gitignore, .globalignore files as requested.")


        # --- Build Include Specification (if -inc provided) ---
        include_spec = None
        if args.include is not None:
             if not args.include:
                  # Keep essential warnings
                 print("Warning: -inc flag provided with no patterns. No files will be included.")
                 if pathspec:
                      include_spec = pathspec.PathSpec.from_lines('gitwildmatch', [])
             elif pathspec:
                 # REMOVED print(f"Using include patterns: {args.include}")
                 try:
                     cleaned_patterns = [p for p in args.include if p.strip() and not p.strip().startswith('#')]
                     include_spec = pathspec.PathSpec.from_lines('gitwildmatch', cleaned_patterns)
                     # REMOVED print(f"Compiled {len(cleaned_patterns)} include patterns.")
                 except Exception as e:
                      # Keep essential errors
                     print(f"Error creating include specification: {e}")
                     sys.exit(1)
             else:
                  # Keep essential errors (already checked pathspec earlier, but defensive)
                 print("Error: pathspec needed for --include but not found.")
                 sys.exit(1)


        # --- Find Files to Process ---
        files_to_process = find_matching_files(git_path, include_spec, ignore_spec)
        total_files = len(files_to_process) # Get count here


        # --- Determine Output Mode (File or Clipboard) ---
        # REMOVED output_target_description = ""
        output_to_file = args.output is not None
        copy_to_clip = args.clipboard or not output_to_file

        if output_to_file:
            output_file_path = os.path.abspath(args.output)
            # REMOVED output_target_description = f"file: {output_file_path}"
            output_dir = os.path.dirname(output_file_path)
            if output_dir:
                 try:
                     os.makedirs(output_dir, exist_ok=True)
                 except OSError as e:
                     # Keep essential errors
                     print(f"Error creating output directory {output_dir}: {e}")
                     sys.exit(1)
            try:
                output_handle = open(output_file_path, 'w', encoding='utf-8')
            except OSError as e:
                 # Keep essential errors
                 print(f"Error opening output file {output_file_path} for writing: {e}")
                 sys.exit(1)
        else:
            # REMOVED output_target_description = "clipboard"
            output_handle = io.StringIO()
            output_file_path = None


        # --- Write Output ---
        try:
            # REMOVED print(f"Writing output to {output_target_description}...")

            if files_to_process:
                 tree_dict = build_tree_from_paths(files_to_process, git_path)
                 write_tree_from_paths(output_handle, tree_dict)
            else:
                 # Keep potentially useful info if nothing happens
                 print("No files matched the criteria. Skipping tree generation and file content.")
                 output_handle.write("No files matched the specified criteria.\n\n")

            for i, rel_path in enumerate(files_to_process):
                full_path = os.path.join(git_path, rel_path)
                # REMOVED print(f"Processing [{i+1}/{total_files}]: {rel_path}")
                append_file_content(full_path, git_path, output_handle, args.skip_empty_files)

            # --- Finalize Output ---
            if output_to_file:
                output_handle.close()
                # REMOVED print(f"Successfully wrote output to: {output_file_path}")
                if copy_to_clip:
                    # REMOVED print("Copying file content to clipboard...")
                    copy_to_clipboard_file(output_file_path)
                    # MODIFIED Success Message
                    print(f"{total_files} files copied to clipboard.")
                # else: # No output if not copying to clipboard
                #    pass
            else: # Output was to buffer
                content = output_handle.getvalue()
                output_handle.close()
                if copy_to_clip:
                    # REMOVED print("Copying content to clipboard...")
                    copy_to_clipboard_content(content)
                     # MODIFIED Success Message
                    print(f"{total_files} files copied to clipboard.")
                # else: # Logic ensures copy_to_clip is true here, no need for else


        except Exception as e:
             # Keep essential errors
             print(f"\nError during writing/processing: {e}")
             if output_to_file and 'output_handle' in locals() and not output_handle.closed:
                 output_handle.close()
             import traceback
             traceback.print_exc()
             sys.exit(1)

    finally:
        # --- Cleanup ---
        os.chdir(original_dir)
        if temp_dir:
            # REMOVED print(f"Cleaning up temporary directory: {temp_dir}")
            try:
                shutil.rmtree(temp_dir, onerror=on_rm_error)
            except Exception as e:
                 # Keep essential warnings/errors
                 print(f"Warning: Failed to completely remove temporary directory {temp_dir}: {e}")


if __name__ == '__main__':
    main()
```
# End of file: src/git2text.py

# File: src/test_git2text.py
```python
import unittest
from unittest.mock import patch, mock_open, MagicMock, call, ANY
import os
import sys
import tempfile
import shutil
import io
import stat # For on_rm_error testing
import subprocess # To check for CalledProcessError instance
import gettext # For mocking translation

# Assume the script is named git2text.py and is importable
try:
    import git2text
except ImportError:
    print("ERROR: Could not import git2text.py. Make sure it's in the Python path.")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Failed during import: {e}")
    sys.exit(1)

# --- Test Suite ---

# Create a dummy NullTranslations class to prevent gettext file loading errors
class NullTranslations(gettext.NullTranslations):
    def gettext(self, message):
        return message
    def ngettext(self, msgid1, msgid2, n):
        return msgid1 if n == 1 else msgid2
    # Add other methods if argparse uses them (less likely)
    def lgettext(self, message):
        return message.encode('utf-8') # Or appropriate default encoding
    def lngettext(self, msgid1, msgid2, n):
         return (msgid1 if n == 1 else msgid2).encode('utf-8')


class TestGit2Text(unittest.TestCase):

    def setUp(self):
        """Set up for test methods."""
        self.original_argv = sys.argv
        self.original_cwd = os.getcwd()
        # Create a temporary directory for file system operations
        self.test_dir = tempfile.mkdtemp(prefix="git2text_test_")
        os.chdir(self.test_dir) # Change CWD for relative path testing

        # Create a dummy .globalignore in the test runner's CWD (original CWD)
        self.global_ignore_path = os.path.join(self.original_cwd, '.globalignore')
        self.created_global_ignore = False # Initialize flag
        if os.path.exists(self.global_ignore_path):
            print(f"Warning: .globalignore already exists at {self.global_ignore_path}, tests needing it might behave unexpectedly or skip.")
            # Decide if this should be a skipTest or just a warning
            # self.skipTest(f".globalignore already exists at {self.global_ignore_path}, skipping tests.")
        else:
            try:
                with open(self.global_ignore_path, 'w') as f:
                    f.write("# Global ignore file\n*.bak\n")
                self.created_global_ignore = True
            except OSError as e:
                 print(f"Warning: Could not create dummy .globalignore at {self.global_ignore_path}: {e}. Tests relying on it may fail.")
                 # self.skipTest(f"Could not create dummy .globalignore at {self.global_ignore_path}, skipping tests.")


    def tearDown(self):
        """Tear down after test methods."""
        sys.argv = self.original_argv
        # Change back to the original directory *before* removing test_dir
        os.chdir(self.original_cwd)
        # Remove the temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True) # Use ignore_errors for robustness
        # Remove the dummy .globalignore if we created it
        if self.created_global_ignore:
             if os.path.exists(self.global_ignore_path):
                 try:
                     os.remove(self.global_ignore_path)
                 except OSError:
                     pass # Ignore errors during cleanup

    # --- Helper Methods ---

    def _create_file(self, path, content=""):
        """Helper to create a file with content in the test directory."""
        # Ensure path is relative to self.test_dir
        if os.path.isabs(path):
             raise ValueError("Helper expects relative path within test_dir")
        full_path = os.path.join(self.test_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return full_path

    def _setup_basic_project(self):
        """Creates a standard file structure for testing."""
        self._create_file("main.py", "print('hello')")
        self._create_file("README.md", "# Test Project")
        self._create_file("utils/helper.py", "def add(a, b): return a + b")
        self._create_file("utils/data.txt", "some data")
        self._create_file("config/settings.yaml", "key: value")
        self._create_file("empty_file.txt", "")
        self._create_file(".gitignore", "*.log\nbuild/\n.env\n*.bak") # Add .bak to test global
        self._create_file("app.log", "Error message")
        self._create_file("build/output.bin", "binary data")
        self._create_file("src/feature/component.js", "console.log('feature');")
        self._create_file(".env", "SECRET=123")
        # Add a .git directory which should always be ignored
        os.makedirs(os.path.join(self.test_dir, ".git/objects"), exist_ok=True)
        self._create_file(".git/config", "[core]\n")
        self._create_file("main.bak", "backup content") # To test global ignore

    # --- Test Individual Functions ---

    def test_get_language_from_extension(self):
        self.assertEqual(git2text.get_language_from_extension("file.py"), "python")
        self.assertEqual(git2text.get_language_from_extension("file.Js"), "javascript") # Case test
        self.assertEqual(git2text.get_language_from_extension("file.txt"), "text")
        self.assertEqual(git2text.get_language_from_extension("file.unknown"), "text")
        self.assertEqual(git2text.get_language_from_extension("file_no_ext"), "text")
        self.assertEqual(git2text.get_language_from_extension(".bashrc"), "text")

    def test_is_git_url(self):
        self.assertTrue(git2text.is_git_url("https://github.com/user/repo.git"))
        self.assertTrue(git2text.is_git_url("git@github.com:user/repo.git"))
        self.assertTrue(git2text.is_git_url("ssh://user@host.xz/path/to/repo.git"))
        self.assertTrue(git2text.is_git_url("file:///path/to/repo.git"))
        self.assertFalse(git2text.is_git_url("/local/path/to/repo"))
        self.assertFalse(git2text.is_git_url("."))
        self.assertFalse(git2text.is_git_url("C:\\Users\\Project"))

    @unittest.skipUnless(sys.platform == 'win32', "Test specific to Windows permission handling")
    @patch('os.access', return_value=False) # Mock no write access
    @patch('os.chmod') # Mock chmod
    @patch('os.remove') # Mock the function that failed (e.g., os.remove)
    def test_on_rm_error_permission_windows(self, mock_remove, mock_chmod, mock_access):
        """Test on_rm_error attempts chmod on Windows permission error."""
        dummy_path = "/fake/path"
        dummy_func = mock_remove # The function that failed is os.remove
        exc_info = (PermissionError, PermissionError(f"Access Denied: {dummy_path}"), None)

        # Simulate calling the error handler
        git2text.on_rm_error(dummy_func, dummy_path, exc_info)

        mock_access.assert_called_once_with(dummy_path, os.W_OK)
        mock_chmod.assert_called_once_with(dummy_path, stat.S_IWRITE)
        # Check if the original failing function was called again *by the handler*
        # The *initial* call that failed might not be registered against this specific mock
        # if shutil calls, e.g., an internal unlink first. So, we check that the handler
        # made exactly one call to the function it was given.
        mock_remove.assert_called_once_with(dummy_path) # Check the retry call by the handler


    @patch('os.access', return_value=True) # Mock has write access (or non-windows)
    @patch('os.chmod')
    @patch('os.remove')
    def test_on_rm_error_non_permission(self, mock_remove, mock_chmod, mock_access):
        """Test on_rm_error re-raises non-permission errors."""
        dummy_path = "/fake/path"
        dummy_func = mock_remove
        exc_info = (FileNotFoundError, FileNotFoundError(f"Not Found: {dummy_path}"), None)

        with self.assertRaises(FileNotFoundError):
            git2text.on_rm_error(dummy_func, dummy_path, exc_info)

        if sys.platform == 'win32':
            # On windows, access check happens first
            mock_access.assert_called_once_with(dummy_path, os.W_OK)
        else:
            # On non-windows, access check should NOT happen
             mock_access.assert_not_called()

        # Regardless of platform, chmod and retry should not happen for non-permission error
        mock_chmod.assert_not_called()
        mock_remove.assert_not_called() # Handler should not call func()


    def test_format_tree(self):
        tree = {
            'file1.txt': {'path': '/a/file1.txt', 'is_dir': False},
            'dir1': {'path': '/a/dir1', 'is_dir': True, 'children': {
                'file2.py': {'path': '/a/dir1/file2.py', 'is_dir': False}
            }},
            'dir2': {'path': '/a/dir2', 'is_dir': True, 'children': {}} # Empty dir
        }
        expected = (
            "├── dir1/\n"
            "│   └── file2.py\n"
            "├── dir2/\n"
            "└── file1.txt\n"
        )
        sorted_tree = dict(sorted(tree.items()))
        actual = git2text.format_tree(sorted_tree)
        self.assertEqual(actual.replace('\r\n', '\n'), expected.replace('\r\n', '\n'))

    def test_build_tree_from_paths(self):
        paths = ["README.md", "src/main.py", "src/utils/helpers.py", "config/dev.json"]
        git_path = self.test_dir
        tree = git2text.build_tree_from_paths(paths, git_path)

        self.assertIn("README.md", tree)
        self.assertFalse(tree["README.md"]["is_dir"])
        self.assertIn("src", tree)
        self.assertTrue(tree["src"]["is_dir"])
        self.assertIn("main.py", tree["src"]["children"])
        self.assertFalse(tree["src"]["children"]["main.py"]["is_dir"])
        self.assertIn("utils", tree["src"]["children"])
        self.assertTrue(tree["src"]["children"]["utils"]["is_dir"])
        self.assertIn("helpers.py", tree["src"]["children"]["utils"]["children"])
        # ... rest of assertions ...
        self.assertIn("config", tree)
        self.assertTrue(tree["config"]["is_dir"])
        self.assertIn("dev.json", tree["config"]["children"])
        self.assertFalse(tree["config"]["children"]["dev.json"]["is_dir"])


    # --- Test find_matching_files (Core Logic) ---
    # These tests seem okay based on output, keeping them as is

    def test_find_files_no_filters(self):
        self._setup_basic_project()
        ignore_spec = git2text.pathspec.PathSpec.from_lines('gitwildmatch', ["*.log", "build/", ".env", "*.bak"])
        files = git2text.find_matching_files(self.test_dir, include_spec=None, ignore_spec=ignore_spec)
        expected = sorted([
            ".gitignore", "README.md", "config/settings.yaml", "empty_file.txt",
            "main.py", "src/feature/component.js", "utils/data.txt", "utils/helper.py",
        ])
        files_normalized = sorted([f.replace('\\', '/') for f in files])
        self.assertListEqual(files_normalized, expected)

    def test_find_files_include_py(self):
        self._setup_basic_project()
        ignore_spec = git2text.pathspec.PathSpec.from_lines('gitwildmatch', ["*.log", "build/", ".env", "*.bak"])
        include_spec = git2text.pathspec.PathSpec.from_lines('gitwildmatch', ["*.py"])
        files = git2text.find_matching_files(self.test_dir, include_spec=include_spec, ignore_spec=ignore_spec)
        expected = sorted(["main.py", "utils/helper.py"])
        files_normalized = sorted([f.replace('\\', '/') for f in files])
        self.assertListEqual(files_normalized, expected)

    def test_find_files_include_subdir_files(self):
        self._setup_basic_project()
        ignore_spec = git2text.pathspec.PathSpec.from_lines('gitwildmatch', ["*.log", "build/", ".env", "*.bak"])
        include_spec = git2text.pathspec.PathSpec.from_lines('gitwildmatch', ["utils/*"])
        files = git2text.find_matching_files(self.test_dir, include_spec=include_spec, ignore_spec=ignore_spec)
        expected = sorted(["utils/data.txt", "utils/helper.py"])
        files_normalized = sorted([f.replace('\\', '/') for f in files])
        self.assertListEqual(files_normalized, expected)

    def test_find_files_ignore_overrides_include(self):
        self._setup_basic_project()
        self._create_file("utils/temp.log", "temp log")
        ignore_spec = git2text.pathspec.PathSpec.from_lines('gitwildmatch', ["*.log", "build/", ".env", "*.bak"])
        include_spec = git2text.pathspec.PathSpec.from_lines('gitwildmatch', ["utils/*"])
        files = git2text.find_matching_files(self.test_dir, include_spec=include_spec, ignore_spec=ignore_spec)
        expected = sorted(["utils/data.txt", "utils/helper.py"])
        files_normalized = sorted([f.replace('\\', '/') for f in files])
        self.assertListEqual(files_normalized, expected)

    def test_find_files_git_dir_ignored(self):
        self._setup_basic_project()
        ignore_spec = None
        include_spec = git2text.pathspec.PathSpec.from_lines('gitwildmatch', ["**/*"])
        files = git2text.find_matching_files(self.test_dir, include_spec=include_spec, ignore_spec=ignore_spec)
        for f in files:
            self.assertFalse(f.replace('\\', '/').startswith('.git/'), f"File inside .git listed: {f}")
            self.assertFalse(f == '.git', f"'.git' directory listed as file")


    # --- Test Main Function Logic (Integration Style) ---

    # Patch gettext for consistency
    @patch('gettext.translation', return_value=NullTranslations())
    def test_main_local_path_output_file(self, mock_gettext):
        """Test main with local path and output to file."""
        self._setup_basic_project()
        output_filename = "my_output.md"
        sys.argv = ["git2text.py", self.test_dir, "-o", output_filename]

        with patch('git2text.copy_to_clipboard_file') as mock_copy_file, \
             patch('git2text.copy_to_clipboard_content') as mock_copy_content:
            git2text.main()

            # Assertions
            # Output file path is now relative to original CWD because main changes back
            output_filepath = os.path.join(self.test_dir, output_filename)
            self.assertTrue(os.path.exists(output_filepath))

            with open(output_filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for key elements
            self.assertIn("Project Tree:", content)
            self.assertIn("main.py", content) # In tree
            # Check specific file content sections are absent/present
            self.assertNotIn("# File: app.log", content)
            self.assertNotIn("# File: build/output.bin", content) # Check file content section is ignored
            self.assertNotIn("# File: main.bak", content)
            self.assertIn("# File: main.py", content)
            self.assertIn("print('hello')", content)
            self.assertIn("# File: utils/helper.py", content)
            self.assertIn("def add(a, b): return a + b", content)

            mock_copy_file.assert_not_called()
            mock_copy_content.assert_not_called()

    # Patch gettext for consistency
    @patch('gettext.translation', return_value=NullTranslations())
    @patch('git2text.copy_to_clipboard_content')
    def test_main_local_path_clipboard_default(self, mock_copy_content, mock_gettext):
        """Test main defaults to clipboard when -o is omitted."""
        self._setup_basic_project()
        sys.argv = ["git2text.py", self.test_dir] # No -o

        git2text.main()

        mock_copy_content.assert_called_once()
        content = mock_copy_content.call_args[0][0]
        self.assertIn("Project Tree:", content)
        self.assertIn("main.py", content)
        self.assertNotIn("# File: app.log", content)
        self.assertIn("# File: main.py", content)

    # Patch gettext for consistency
    @patch('gettext.translation', return_value=NullTranslations())
    @patch('git2text.copy_to_clipboard_file')
    def test_main_local_path_output_file_and_clipboard(self, mock_copy_file, mock_gettext):
        """Test main writes to file and copies with -o and -cp."""
        self._setup_basic_project()
        output_filename = "out_cp.txt"
        sys.argv = ["git2text.py", self.test_dir, "-o", output_filename, "-cp"]

        git2text.main()

        output_filepath = os.path.join(self.test_dir, output_filename)
        self.assertTrue(os.path.exists(output_filepath))
        mock_copy_file.assert_called_once_with(output_filepath)

    # Patch gettext for consistency
    @patch('gettext.translation', return_value=NullTranslations())
    def test_main_include_option(self, mock_gettext):
        """Test -inc option selects only specified files."""
        self._setup_basic_project()
        output_filename = "include_test.txt"
        sys.argv = ["git2text.py", self.test_dir, "-o", output_filename, "-inc", "*.py", "README.md"]

        git2text.main()
        output_filepath = os.path.join(self.test_dir, output_filename)
        with open(output_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check tree (uses file names)
        self.assertIn("main.py", content)
        self.assertIn("helper.py", content)
        self.assertIn("README.md", content)
        self.assertNotIn("data.txt", content)
        self.assertNotIn("settings.yaml", content)

        # Check file contents sections
        self.assertIn("# File: main.py", content)
        self.assertIn("# File: utils/helper.py", content)
        self.assertIn("# File: README.md", content)
        self.assertNotIn("# File: utils/data.txt", content)

    # Patch gettext for consistency
    @patch('gettext.translation', return_value=NullTranslations())
    def test_main_ignore_option(self, mock_gettext):
        """Test -ig option adds to default ignores."""
        self._setup_basic_project()
        output_filename = "ignore_test.txt"
        sys.argv = ["git2text.py", self.test_dir, "-o", output_filename, "-ig", "*.py"]

        git2text.main()
        output_filepath = os.path.join(self.test_dir, output_filename)
        with open(output_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check .py files are gone (tree and content)
        self.assertNotIn("main.py", content)
        self.assertNotIn("helper.py", content)
        self.assertNotIn("# File: main.py", content)
        self.assertNotIn("# File: utils/helper.py", content)

        # Check other files still exist
        self.assertIn("README.md", content)
        self.assertIn("# File: README.md", content)
        self.assertIn("data.txt", content) # In tree
        self.assertIn("# File: utils/data.txt", content) # In content

        # Check .gitignore ignores still work
        self.assertNotIn("# File: app.log", content)

    # Patch gettext for consistency
    @patch('gettext.translation', return_value=NullTranslations())
    def test_main_ignore_gitignore_flag(self, mock_gettext):
        """Test -igi flag ignores .gitignore and .globalignore."""
        self._setup_basic_project()
        output_filename = "ignore_gi_test.txt"
        sys.argv = ["git2text.py", self.test_dir, "-o", output_filename, "--ignoregitignore"]

        git2text.main()
        output_filepath = os.path.join(self.test_dir, output_filename)
        with open(output_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check files normally ignored are NOW included
        self.assertIn("app.log", content) # Tree
        self.assertIn("# File: app.log", content) # Content
        self.assertIn("build/output.bin", content)
        self.assertIn("# File: build/output.bin", content)
        self.assertIn(".env", content)
        self.assertIn("# File: .env", content)
        self.assertIn("main.bak", content)
        self.assertIn("# File: main.bak", content)
        self.assertIn("main.py", content)

    # Patch gettext for consistency
    @patch('gettext.translation', return_value=NullTranslations())
    def test_main_skip_empty_files(self, mock_gettext):
        """Test -se flag skips empty files."""
        self._setup_basic_project()
        output_filename = "skip_empty_test.txt"
        sys.argv = ["git2text.py", self.test_dir, "-o", output_filename, "--skip-empty-files"]

        git2text.main()
        output_filepath = os.path.join(self.test_dir, output_filename)
        with open(output_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check empty file IS in the tree structure
        self.assertIn("empty_file.txt", content)
        # Check empty file content section is NOT present
        self.assertNotIn("# File: empty_file.txt", content)
        self.assertNotIn("# End of file: empty_file.txt", content)

        # Check non-empty files are still present
        self.assertIn("main.py", content)
        self.assertIn("# File: main.py", content)

    # Patch gettext for consistency
    @patch('gettext.translation', return_value=NullTranslations())
    def test_main_path_not_found(self, mock_gettext):
        """Test main exits if local path doesn't exist."""
        bad_path = os.path.join(self.test_dir, "non_existent_dir")
        sys.argv = ["git2text.py", bad_path]

        with self.assertRaises(SystemExit) as cm:
            git2text.main()
        self.assertEqual(cm.exception.code, 1)

    @patch('git2text.pathspec', None) # Simulate pathspec not being installed
    @patch('gettext.translation', return_value=NullTranslations()) # Still need gettext patch
    def test_main_no_pathspec_and_gitignore_required(self, mock_gettext):
        """Test main exits if pathspec needed but not installed."""
        self._setup_basic_project() # Creates .gitignore
        sys.argv = ["git2text.py", self.test_dir]

        with self.assertRaises(SystemExit) as cm:
             git2text.main()
        self.assertEqual(cm.exception.code, 1)

    @patch('git2text.pathspec', None) # Simulate pathspec not installed
    @patch('gettext.translation', return_value=NullTranslations()) # Still need gettext patch
    def test_main_no_pathspec_but_ignoregitignore_ok(self, mock_gettext):
        """Test main proceeds without pathspec if -igi is used."""
        self._setup_basic_project()
        output_filename = "no_pathspec_ok.txt"
        sys.argv = ["git2text.py", self.test_dir, "-o", output_filename, "--ignoregitignore"]

        # Use specific mocks for file operations to avoid overly broad mocks
        with patch('builtins.open', mock_open(read_data="file content")) as mock_file_open, \
             patch('os.path.getsize', return_value=10): # Mock getsize for non-empty check
            git2text.main()
            output_filepath = os.path.join(self.test_dir, output_filename)
            # Check that the output file was attempted to be opened for writing
            self.assertIn(call(output_filepath, 'w', encoding='utf-8'), mock_file_open.call_args_list)


# --- Run Tests ---
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```
# End of file: src/test_git2text.py

# File: src/test_skill_git2text_extraction.py
```python
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "git2text-extraction"
SCRIPT_PATH = SKILL_ROOT / "scripts" / "run_git2text.sh"
SKILL_MD = SKILL_ROOT / "SKILL.md"
PRESETS_MD = SKILL_ROOT / "references" / "presets.md"
TROUBLE_MD = SKILL_ROOT / "references" / "troubleshooting.md"


class TestGit2TextExtractionSkill(unittest.TestCase):
    def test_skill_files_exist(self):
        self.assertTrue(SKILL_MD.exists())
        self.assertTrue(PRESETS_MD.exists())
        self.assertTrue(TROUBLE_MD.exists())
        self.assertTrue(SCRIPT_PATH.exists())

    def test_skill_frontmatter_and_links(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("name: git2text-extraction", content)
        self.assertIn("description:", content)
        self.assertIn("references/presets.md", content)
        self.assertIn("references/troubleshooting.md", content)

    def test_run_script_usage_without_source(self):
        result = subprocess.run([str(SCRIPT_PATH)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage:", result.stderr)

    def test_run_script_dry_run_local_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "out.md"
            result = subprocess.run(
                [
                    str(SCRIPT_PATH),
                    "--dry-run",
                    tmpdir,
                    "-inc",
                    "*.py",
                    "-o",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(
            "Running: git2text" in result.stdout
            or "Running: python -m src.git2text" in result.stdout
            or "Running: python3 -m src.git2text" in result.stdout
        )

    def test_run_script_exec_with_fake_git2text_and_output_check(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "repo"
            source_dir.mkdir()
            out_file = Path(tmpdir) / "result.md"

            bin_dir = Path(tmpdir) / "bin"
            bin_dir.mkdir()
            fake_exe = bin_dir / "git2text"
            fake_exe.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "OUT=''\n"
                "while [ \"$#\" -gt 0 ]; do\n"
                "  if [ \"$1\" = '-o' ]; then OUT=\"$2\"; shift 2; continue; fi\n"
                "  shift\n"
                "done\n"
                "echo '# fake output' > \"$OUT\"\n",
                encoding="utf-8",
            )
            fake_exe.chmod(fake_exe.stat().st_mode | stat.S_IEXEC)

            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}:{env['PATH']}"
            result = subprocess.run(
                [
                    str(SCRIPT_PATH),
                    "--require-output",
                    str(out_file),
                    str(source_dir),
                    "-o",
                    str(out_file),
                ],
                capture_output=True,
                text=True,
                env=env,
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(out_file.exists())
            self.assertGreater(out_file.stat().st_size, 0)
            self.assertIn("Validated output:", result.stdout)


if __name__ == "__main__":
    unittest.main()
```
# End of file: src/test_skill_git2text_extraction.py

