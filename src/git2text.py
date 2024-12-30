import os
import sys
import argparse
import glob
import fnmatch
import subprocess
import io  # To handle in-memory text streams
import tempfile
import shutil
import stat  # For handling file permissions on Windows

try:
    import pathspec  # For parsing .gitignore files
except ImportError:
    pathspec = None  # Will check if pathspec is available

def get_language_from_extension(file_path: str) -> str:
    """
    Determine the language for syntax highlighting based on the file extension.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The language identifier for Markdown code blocks.
    """
    extension_to_language = {
        '.abap': 'abap',
        '.ads': 'ada',
        '.adb': 'ada',
        '.as': 'actionscript',
        '.asciidoc': 'asciidoc',
        '.adoc': 'asciidoc',
        '.asm': 'assembly',
        '.s': 'assembly',
        '.ahk': 'autohotkey',
        '.bat': 'batch',
        '.bats': 'batch',
        '.c': 'c',
        '.h': 'c',
        '.cs': 'csharp',
        '.clj': 'clojure',
        '.cljs': 'clojure',
        '.coffee': 'coffeescript',
        '.cpp': 'cpp',
        '.hpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.css': 'css',
        '.d': 'd',
        '.dart': 'dart',
        '.diff': 'diff',
        '.patch': 'diff',
        '.dockerfile': 'dockerfile',
        '.ex': 'elixir',
        '.exs': 'elixir',
        '.elm': 'elm',
        '.erl': 'erlang',
        '.hrl': 'erlang',
        '.go': 'go',
        '.groovy': 'groovy',
        '.gradle': 'groovy',
        '.hs': 'haskell',
        '.lhs': 'haskell',
        '.html': 'html',
        '.htm': 'html',
        '.xhtml': 'html',
        '.hbs': 'handlebars',
        '.ini': 'ini',
        '.java': 'java',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.json': 'json',
        '.jl': 'julia',
        '.kt': 'kotlin',
        '.kts': 'kotlin',
        '.less': 'less',
        '.lua': 'lua',
        '.md': 'markdown',
        '.mkd': 'markdown',
        '.matlab': 'matlab',
        '.m': 'matlab',
        '.nix': 'nix',
        '.mli': 'ocaml',
        '.ml': 'ocaml',
        '.php': 'php',
        '.pl': 'perl',
        '.pm': 'perl',
        '.ps1': 'powershell',
        '.psm1': 'powershell',
        '.proto': 'protobuf',
        '.py': 'python',
        '.r': 'r',
        '.rb': 'ruby',
        '.rs': 'rust',
        '.sass': 'sass',
        '.scss': 'scss',
        '.scala': 'scala',
        '.sh': 'bash',
        '.bash': 'bash',
        '.sql': 'sql',
        '.swift': 'swift',
        '.tex': 'tex',
        '.toml': 'toml',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.vb': 'vbnet',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.zig': 'zig',
    }

    _, extension = os.path.splitext(file_path)
    return extension_to_language.get(extension, 'text')

def build_tree_from_included_paths(include_list: list, git_path: str) -> dict:
    """
    Build a tree structure from the included paths.

    Args:
        include_list (list): List of paths to include.
        git_path (str): The base path of the git repository.

    Returns:
        dict: A dictionary representing the tree structure.
    """
    tree_dict = {}
    for path in include_list:
        path = path.replace('\\', '/')
        parts = path.split('/')
        current_level = tree_dict

        for part in parts[:-1]:  # Directory parts
            if part not in current_level:
                current_level[part] = {'path': '', 'is_dir': True, 'children': {}}
            current_level = current_level[part]['children']

        # Add the file or directory itself
        name = parts[-1]
        if name:  # Ensure there's a name to add
            full_path = os.path.join(git_path, path)
            is_dir = os.path.isdir(full_path)
            current_level[name] = {'path': full_path, 'is_dir': is_dir, 'children': {}}
            # If it's a directory, build its tree
            if is_dir:
                build_tree(full_path, current_level[name]['children'], [], git_path)
    return tree_dict

def write_tree_to_file_with_included_paths(git_path: str, output_handle, include_list: list):
    """
    Write the tree structure to the output file based on included paths.

    Args:
        git_path (str): The base path of the git repository.
        output_handle: The file handle to write the output.
        include_list (list): List of paths to include.
    """
    tree_dict = build_tree_from_included_paths(include_list, git_path)
    tree_str = format_tree(tree_dict)
    output_handle.write(tree_str.rstrip('\r\n') + '\n\n')

def build_tree(directory, tree_dict, ignore_list, git_path, gitignore_spec=None):
    """
    Recursively build a tree structure of the directory.

    Args:
        directory: The directory to build the tree from.
        tree_dict: The dictionary to store the tree structure.
        ignore_list: List of paths to ignore.
        git_path: The base path of the git repository.
        gitignore_spec: The gitignore specification.
    """
    try:
        items = os.listdir(directory)
    except PermissionError:
        print(f"Warning: Permission denied: {directory}. Skipping directory.")
        return
    items.sort()  # Sort the items to have a consistent order
    for item in items:
        path = os.path.join(directory, item)
        try:
            is_dir = os.path.isdir(path)
            is_file = os.path.isfile(path)
        except PermissionError:
            print(f"Warning: Permission denied: {path}. Skipping.")
            continue
        if is_dir and not should_ignore(path, ignore_list, git_path, gitignore_spec):
            tree_dict[item] = {'path': path, 'is_dir': True, 'children': {}}
            build_tree(path, tree_dict[item]['children'], ignore_list, git_path, gitignore_spec)
        elif is_file:
            if not should_ignore(path, ignore_list, git_path, gitignore_spec):
                tree_dict[item] = {'path': path, 'is_dir': False}

def format_tree(tree_dict, padding=''):
    """
    Format the tree structure into a string.

    Args:
        tree_dict: The dictionary representing the tree structure.
        padding: The padding for the tree structure.

    Returns:
        str: The formatted tree structure.
    """
    lines = ''
    if not tree_dict:
        return lines
    last_index = len(tree_dict) - 1
    for index, (name, node) in enumerate(tree_dict.items()):
        connector = '└──' if index == last_index else '├──'
        if node['is_dir']:
            lines += f"{padding}{connector} {name}/\n"
            new_padding = padding + ("    " if index == last_index else "│   ")
            lines += format_tree(node['children'], new_padding)
        else:
            lines += f"{padding}{connector} {name}\n"
    return lines

def write_tree_to_file(directory, output_handle, ignore_list, gitignore_spec=None):
    """
    Write the tree structure to the output file.

    Args:
        directory: The directory to build the tree from.
        output_handle: The file handle to write the output.
        ignore_list: List of paths to ignore.
        gitignore_spec: The gitignore specification.
    """
    tree_dict = {}
    build_tree(directory, tree_dict, ignore_list, directory, gitignore_spec)
    tree_str = format_tree(tree_dict)
    output_handle.write(tree_str.rstrip('\r\n') + '\n\n')  # write the tree followed by two newlines

def append_to_file_markdown_style(relative_path: str, file_content: str, output_handle) -> None:
    """
    Append the file content to the output file in Markdown style.

    Args:
        relative_path (str): The relative path of the file.
        file_content (str): The content of the file.
        output_handle: The file handle to write the output.
    """
    language = get_language_from_extension(relative_path)
    # Write the header with the relative path and the file content wrapped in a code block
    output_handle.write(f"# File: {relative_path}\n```{language}\n{file_content}\n```\n# End of file: {relative_path}\n\n")

def should_ignore(path: str, ignore_list: list, git_path: str, gitignore_spec=None) -> bool:
    """
    Check if the path should be ignored based on the ignore list and gitignore specification.

    Args:
        path (str): The path to check.
        ignore_list (list): List of paths to ignore.
        git_path (str): The base path of the git repository.
        gitignore_spec: The gitignore specification.

    Returns:
        bool: True if the path should be ignored, False otherwise.
    """
    relative_path = os.path.relpath(path, git_path)
    # Always ignore the .git folder
    if relative_path == '.git' or relative_path.startswith('.git' + os.sep):
        return True
    if gitignore_spec:
        # Append '/' to directories to match gitignore directory patterns
        match_path = relative_path + '/' if os.path.isdir(path) else relative_path
        if gitignore_spec.match_file(match_path):
            return True
    for pattern in ignore_list:
        if fnmatch.fnmatch(relative_path, pattern):
            return True
    return False

def append_to_single_file(file_path: str, git_path: str, output_handle, skip_empty_files: bool) -> None:
    """
    Append the content of a single file to the output file.

    Args:
        file_path (str): The path to the file.
        git_path (str): The base path of the git repository.
        output_handle: The file handle to write the output.
        skip_empty_files (bool): Whether to skip empty files.
    """
    # Check if the file is empty and should be skipped
    if skip_empty_files and os.path.getsize(file_path) == 0:
        print(f'Skipping empty file: {file_path}')
        return

    # Determine the relative path of the file to use as a header
    relative_path = os.path.relpath(file_path, start=git_path)

    # Try to read the file with UTF-8 encoding, skip if it fails
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except UnicodeDecodeError:
        print(f'Warning: Could not decode {file_path}. Skipping file.')
        return
    except PermissionError:
        print(f'Warning: Permission denied: {file_path}. Skipping file.')
        return

    # Append the content in Markdown style
    append_to_file_markdown_style(relative_path, file_content, output_handle)

def process_path(git_path: str, ignore_list: list, output_handle, skip_empty_files: bool, gitignore_spec=None) -> None:
    """
    Process all files and directories in the given path.

    Args:
        git_path (str): The base path of the git repository.
        ignore_list (list): List of paths to ignore.
        output_handle: The file handle to write the output.
        skip_empty_files (bool): Whether to skip empty files.
        gitignore_spec: The gitignore specification.
    """
    for root, dirs, files in os.walk(git_path, topdown=True, onerror=lambda e: print(f"Warning: {e.strerror}: {e.filename}. Skipping.")):
        # Apply filtering on the directories
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_list, git_path, gitignore_spec)]

        for file in files:
            full_path = os.path.join(root, file)
            if should_ignore(full_path, ignore_list, git_path, gitignore_spec):
                print(f'Skipping ignored file: {file}')
                continue
            append_to_single_file(full_path, git_path, output_handle, skip_empty_files)

def process_include_list(git_path: str, output_handle, skip_empty_files: bool, include_list: list) -> None:
    """
    Process files and directories from the include list.

    Args:
        git_path (str): The base path of the git repository.
        output_handle: The file handle to write the output.
        skip_empty_files (bool): Whether to skip empty files.
        include_list (list): List of paths to include.
    """
    for relative_path in include_list:
        full_path = os.path.join(git_path, relative_path.replace('/', os.sep))  # Ensure platform compatibility

        if not os.path.exists(full_path):
            print(f'Warning: Path does not exist: {relative_path}')
            continue  # Skip non-existing paths

        if os.path.isfile(full_path):
            append_to_single_file(full_path, git_path, output_handle, skip_empty_files)
        elif os.path.isdir(full_path):
            # Recursively process directory
            for root, dirs, files in os.walk(full_path, onerror=lambda e: print(f"Warning: {e.strerror}: {e.filename}. Skipping.")):
                for file in files:
                    file_full_path = os.path.join(root, file)
                    append_to_single_file(file_full_path, git_path, output_handle, skip_empty_files)
        else:
            print(f'Warning: Path is neither a file nor a directory: {relative_path}')

def copy_to_clipboard_content(content: str) -> None:
    """
    Copy the given content to the clipboard.

    Args:
        content (str): The content to copy to the clipboard.
    """
    if sys.platform == "win32":
        # On Windows, use the clip command with UTF-16LE encoding
        process = subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True)
        process.communicate(input=content.encode('utf-16le'))
    elif sys.platform == "darwin":
        # On macOS, use the pbcopy command with UTF-8 encoding
        process = subprocess.Popen('pbcopy', stdin=subprocess.PIPE)
        process.communicate(input=content.encode('utf-8'))
    elif sys.platform.startswith("linux"):
        # On Linux, try xclip or xsel
        try:
            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
            process.communicate(input=content.encode('utf-8'))
        except FileNotFoundError:
            try:
                process = subprocess.Popen(['xsel', '--clipboard', '--input'], stdin=subprocess.PIPE)
                process.communicate(input=content.encode('utf-8'))
            except FileNotFoundError:
                print("Clipboard functionality requires 'xclip' or 'xsel' to be installed on Linux.")
    else:
        print(f"Clipboard functionality is not supported on {sys.platform}.")

def copy_to_clipboard_file(output_file_path: str) -> None:
    """
    Copy the content of the output file to the clipboard.

    Args:
        output_file_path (str): The path to the output file.
    """
    with open(output_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    copy_to_clipboard_content(content)

def is_git_url(path: str) -> bool:
    """
    Check if the given path is a git URL.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the path is a git URL, False otherwise.
    """
    git_url_prefixes = ['http://', 'https://', 'git@', 'ssh://', 'git://']
    return any(path.startswith(prefix) for prefix in git_url_prefixes)

def on_rm_error(func, path, exc_info):
    """
    Error handler for shutil.rmtree.

    If the error is due to an access error (read-only file),
    it attempts to add write permission and then retries.

    If the error is for another reason, it re-raises the error.

    Args:
        func: The function that raised the error.
        path: The path that caused the error.
        exc_info: The exception information.
    """
    if not os.access(path, os.W_OK):
        # Attempt to add write permission and retry
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Process some files and directories.')
    parser.add_argument('path', help='Path to the git project directory or a git repository URL.')
    parser.add_argument('-o', '--output', help='Output file path.')
    parser.add_argument('-ig', '--ignore', nargs='*', help='List of files or directories to ignore (supports glob patterns).')
    parser.add_argument('-inc', '--include', nargs='*', help='List of files or directories to include (supports glob patterns). If specified, only these paths will be included.')
    parser.add_argument('-se', '--skip-empty-files', action='store_true', help='Skip empty files.')
    parser.add_argument('-cp', '--clipboard', action='store_true', help='Copy the output file content to clipboard.')
    parser.add_argument('-igi', '--ignoregitignore', action='store_true', help='Ignore .gitignore and .globalignore files.')
    args = parser.parse_args()

    git_path = args.path
    temp_dir = None  # To keep track if we need to clean up a temp directory

    try:
        # Check if git_path is a directory
        if os.path.isdir(git_path):
            # Proceed as before
            pass
        else:
            # Not a directory; check if it's a git URL
            if is_git_url(git_path):
                # Clone the repository to a temporary directory
                temp_dir = tempfile.mkdtemp()
                clone_cmd = ['git', 'clone', git_path, temp_dir]
                try:
                    subprocess.check_call(clone_cmd)
                    git_path = temp_dir
                except subprocess.CalledProcessError as e:
                    print(f'Error cloning repository: {e}')
                    sys.exit(1)
            else:
                print(f'Path not found or not a directory or a git URL: {git_path}')
                sys.exit(1)

        output_file_provided = False
        if args.output:
            output_file_provided = True
            output_file_path = args.output
        else:
            output_file_path = None  # No output file by default

        ignore_list = args.ignore if args.ignore is not None else []
        include_list = args.include if args.include is not None else None
        skip_empty_files = args.skip_empty_files

        gitignore_spec = None
        if not args.ignoregitignore:
            if pathspec is None:
                print("Error: 'pathspec' module is required to parse the .gitignore and .globalignore files.")
                print("Install it using 'pip install pathspec' or add the -igi flag to ignore .gitignore and .globalignore.")
                sys.exit(1)
            gitignore_patterns = []

            # Read .gitignore file in git_path
            gitignore_path = os.path.join(git_path, '.gitignore')
            if os.path.exists(gitignore_path):
                with open(gitignore_path, 'r') as f:
                    gitignore_patterns.extend(f.read().splitlines())
            # else:
            #    print(f'Warning: .gitignore file not found in {git_path}')

            # Read .globalignore file in script directory
            script_dir = os.path.dirname(os.path.realpath(__file__))
            globalignore_path = os.path.join(script_dir, '.globalignore')
            if os.path.exists(globalignore_path):
                with open(globalignore_path, 'r') as f:
                    gitignore_patterns.extend(f.read().splitlines())
            else:
                print(f'Warning: .globalignore file not found in {script_dir}')

            if gitignore_patterns:
                gitignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', gitignore_patterns)
        else:
            print("Ignoring .gitignore and .globalignore files as per the --ignoregitignore flag.")

        # Determine the writing mode based on whether an output file is provided
        if output_file_path:
            # Ensure the output directory exists
            output_dir = os.path.dirname(output_file_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            # Open the output file for writing
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                if include_list is not None:
                    # Use glob to expand patterns
                    expanded_include_list = []
                    for pattern in include_list:
                        matched_paths = glob.glob(os.path.join(git_path, pattern), recursive=True)
                        expanded_include_list.extend([os.path.relpath(p, git_path) for p in matched_paths])
                    include_list = expanded_include_list

                    # Since include_list is specified, ignore the ignore_list
                    write_tree_to_file_with_included_paths(git_path, output_file, include_list)
                    process_include_list(git_path, output_file, skip_empty_files, include_list)
                else:
                    # Use ignore patterns
                    write_tree_to_file(git_path, output_file, ignore_list, gitignore_spec)
                    process_path(git_path, ignore_list, output_file, skip_empty_files, gitignore_spec)

                # If the flag --clipboard is set, copy the output to the clipboard
                if args.clipboard:
                    copy_to_clipboard_file(output_file_path)
                    print(f"The content of {output_file_path} has been copied to the clipboard.")

                print(f"All contents have been written to: {output_file_path}")
        else:
            # No output file provided; collect content in-memory and copy to clipboard by default
            output_buffer = io.StringIO()
            if include_list is not None:
                # Use glob to expand patterns
                expanded_include_list = []
                for pattern in include_list:
                    matched_paths = glob.glob(os.path.join(git_path, pattern), recursive=True)
                    expanded_include_list.extend([os.path.relpath(p, git_path) for p in matched_paths])
                include_list = expanded_include_list

                # Since include_list is specified, ignore the ignore_list
                write_tree_to_file_with_included_paths(git_path, output_buffer, include_list)
                process_include_list(git_path, output_buffer, skip_empty_files, include_list)
            else:
                # Use ignore patterns
                write_tree_to_file(git_path, output_buffer, ignore_list, gitignore_spec)
                process_path(git_path, ignore_list, output_buffer, skip_empty_files, gitignore_spec)

            # Get the content from the buffer
            content = output_buffer.getvalue()
            output_buffer.close()

            # Copy the content to the clipboard
            copy_to_clipboard_content(content)
            print("The content has been copied to the clipboard.")
    finally:
        # Clean up the temporary directory if we cloned a repo
        if temp_dir:
            shutil.rmtree(temp_dir, onerror=on_rm_error)

if __name__ == '__main__':
    main()
