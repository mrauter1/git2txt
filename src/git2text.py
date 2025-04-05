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