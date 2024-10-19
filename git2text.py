# main.py
import os
import sys
import argparse
import glob
import fnmatch
import subprocess

def get_language_from_extension(file_path: str) -> str:
    # Mapping of file extensions to Markdown code block language identifiers
    extension_to_language = {
        '.py': 'python',
        '.js': 'javascript',
        '.html': 'html',
        '.css': 'css',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.rb': 'ruby',
        '.php': 'php',
        '.ts': 'typescript',
        '.json': 'json',
        '.md': 'markdown',
        '.xml': 'xml',
        '.sh': 'bash',
    }
    _, extension = os.path.splitext(file_path)
    return extension_to_language.get(extension, 'text')

def build_tree_from_included_files(include_files: list, git_path: str) -> dict:
    tree_dict = {}
    for file_path in include_files:
        parts = file_path.replace('\\', '/').split('/')
        current_level = tree_dict

        for part in parts[:-1]:  # Directory parts
            if part not in current_level:
                current_level[part] = {'path': '', 'is_dir': True, 'children': {}}
            current_level = current_level[part]['children']

        # Add the file itself
        file_name = parts[-1]
        if file_name:  # Ensure there's a filename to add
            current_level[file_name] = {'path': os.path.join(git_path, file_path), 'is_dir': False}

    return tree_dict

def write_tree_to_file_with_included_files(git_path: str, output_file_path: str, include_files: list):
    tree_dict = build_tree_from_included_files(include_files, git_path)
    tree_str = format_tree(tree_dict)
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(tree_str.rstrip('\r\n') + '\n\n')

def build_tree(directory, padding, tree_dict, ignore_dirs, git_path):
    items = os.listdir(directory)
    items.sort()  # Sort the items to have a consistent order
    for item in items:
        path = os.path.join(directory, item)
        if os.path.isdir(path) and not ignore_dir(path, ignore_dirs, git_path):
            tree_dict[item] = {'path': path, 'is_dir': True, 'children': {}}
            build_tree(path, padding + "    ", tree_dict[item]['children'], ignore_dirs, git_path)
        elif os.path.isfile(path):
            tree_dict[item] = {'path': path, 'is_dir': False}

def format_tree(tree_dict, padding=''):
    lines = ''
    last_item = list(tree_dict.keys())[-1] if tree_dict else None  # Identify the last item for correct piping
    for name, node in tree_dict.items():
        connector = '└──' if name == last_item else '├──'
        if node['is_dir']:
            lines += f"{padding}{connector} {name}/\n"
            lines += format_tree(node['children'], padding + ("    " if name == last_item else "│   "))
        else:
            lines += f"{padding}{connector} {name}\n"
    return lines

def write_tree_to_file(directory, output_file_path, ignore_dirs):
    tree_dict = {}
    build_tree(directory, '', tree_dict, ignore_dirs, directory)  # pass the correct directory path
    tree_str = format_tree(tree_dict)
    with open(output_file_path, 'w', encoding='utf-8') as output_file:  # open with 'w' to write the tree
        output_file.write(tree_str.rstrip('\r\n') + '\n\n')  # write the tree followed by two newlines

def append_to_file_markdown_style(relative_path: str, file_content: str, output_file) -> None:
    language = get_language_from_extension(relative_path)
    # Write the header with the relative path and the file content wrapped in a code block
    output_file.write(f"# File: {relative_path}\n```{language}\n{file_content}\n```\n# End of file: {relative_path}\n\n")

def ignore_dir(dir_path: str, ignore_dirs: list, git_path: str) -> bool:
    relative_path = os.path.relpath(dir_path, git_path)
    for pattern in ignore_dirs:
        if fnmatch.fnmatch(relative_path, pattern):
            return True
    return False

def ignore_file(file_path: str, ignore_files: list, git_path: str) -> bool:
    relative_path = os.path.relpath(file_path, git_path)
    for pattern in ignore_files:
        if fnmatch.fnmatch(relative_path, pattern):
            return True
    return False

def append_to_single_file(file_path: str, git_path: str, output_file_path: str, skip_empty_files: bool) -> None:
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

    # Open the output file and append the content
    with open(output_file_path, 'a', encoding='utf-8') as output_file:
        append_to_file_markdown_style(relative_path, file_content, output_file)

def process_path(git_path: str, ignore_files: list, ignore_dirs: list, output_file_path: str, skip_empty_files: bool) -> None:
    for root, dirs, files in os.walk(git_path, topdown=True):
        # Apply filtering on the directories
        dirs[:] = [d for d in dirs if not ignore_dir(os.path.join(root, d), ignore_dirs, git_path)]

        for file in files:
            full_path = os.path.join(root, file)
            if ignore_file(full_path, ignore_files, git_path):
                print(f'Skipping ignored file: {file}')
                continue
            append_to_single_file(full_path, git_path, output_file_path, skip_empty_files)

def process_files(git_path: str, output_file_path: str, skip_empty_files: bool, include_files: list) -> None:
    for relative_path in include_files:
        full_path = os.path.join(git_path, relative_path.replace('/', os.sep))  # Ensure platform compatibility

        if not os.path.exists(full_path):
            print(f'Warning: File does not exist: {relative_path}')
            continue  # Skip non-existing files

        if skip_empty_files and os.path.getsize(full_path) == 0:
            print(f'Skipping empty file: {relative_path}')
            continue  # Skip empty files

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except UnicodeDecodeError:
            print(f'Warning: Could not decode {relative_path}. Skipping file.')
            continue

        # Open the output file and append the content
        with open(output_file_path, 'a', encoding='utf-8') as output_file:
            append_to_file_markdown_style(relative_path, file_content, output_file)
            
def copy_to_clipboard(output_file_path: str) -> None:
    """Copy the content of the output file to the clipboard."""
    if sys.platform == "win32":
        # On Windows, use the clip command with UTF-16LE encoding
        with open(output_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Encode the content to UTF-16LE as clip expects Unicode input
            process = subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True)
            process.communicate(input=content.encode('utf-16le'))
    elif sys.platform == "darwin":
        # On macOS, use the pbcopy command with UTF-8 encoding
        with open(output_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            process = subprocess.Popen('pbcopy', stdin=subprocess.PIPE)
            process.communicate(input=content.encode('utf-8'))
    else:
        print(f"Clipboard functionality is not supported on {sys.platform}.")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Process some files and directories.')
    parser.add_argument('path', help='Path to the git project directory.')
    parser.add_argument('-o', '--output', help='Output file path.')
    parser.add_argument('-if', '--ignore-files', nargs='*', help='List of files to ignore (supports glob patterns).')
    parser.add_argument('-id', '--ignore-dirs', nargs='*', help='List of directories to ignore (supports glob patterns).')
    parser.add_argument('-inc', '--include-files', nargs='*', help='List of files to include (supports glob patterns). If specified, only these files will be included.')
    parser.add_argument('-se', '--skip-empty-files', action='store_true', help='Skip empty files.')
    parser.add_argument('-cp', '--clipboard', action='store_true', help='Copy the output file content to clipboard.')
    args = parser.parse_args()

    git_path = args.path
    if not os.path.isdir(git_path):
        print(f'Path not found or not a directory: {git_path}')
        sys.exit(1)

    if args.output:
        output_file_path = args.output
    else:
        output_file_name = os.path.basename(git_path.rstrip(os.sep)) + '.md'
        output_file_path = os.path.join('.', 'output', output_file_name)

    output_dir = os.path.dirname(output_file_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Ensure the output file is empty at the start
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    ignore_files = args.ignore_files if args.ignore_files is not None else []
    ignore_dirs = args.ignore_dirs if args.ignore_dirs is not None else []
    include_files = args.include_files if args.include_files is not None else None
    skip_empty_files = args.skip_empty_files

    if include_files is not None:
        # Use glob to expand patterns
        expanded_include_files = []
        for pattern in include_files:
            matched_files = glob.glob(os.path.join(git_path, pattern), recursive=True)
            expanded_include_files.extend([os.path.relpath(f, git_path) for f in matched_files if os.path.isfile(f)])
        include_files = expanded_include_files

        # Since include_files is specified, ignore ignore_files and ignore_dirs flags
        write_tree_to_file_with_included_files(git_path, output_file_path, include_files)
        process_files(git_path, output_file_path, skip_empty_files, include_files)
    else:
        # Use ignore patterns
        write_tree_to_file(git_path, output_file_path, ignore_dirs)
        process_path(git_path, ignore_files, ignore_dirs, output_file_path, skip_empty_files)
        
    # If the flag --clipboard is set, copy the output to the clipboard
    if args.clipboard:
        copy_to_clipboard(output_file_path)
        print(f"The content of {output_file_path} has been copied to the clipboard.")        

    print(f"All contents have been written to: {output_file_path}")

if __name__ == '__main__':
    main()
