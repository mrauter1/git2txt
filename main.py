from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

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
        parts = file_path.split('/')
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

def build_tree(directory, padding, tree_dict, ignore_dirs):
    items = os.listdir(directory)
    items.sort()  # Sort the items to have a consistent order
    for item in items:
        path = os.path.join(directory, item)
        if os.path.isdir(path) and not ignore_dir(path, ignore_dirs, directory):
            tree_dict[item] = {'path': path, 'is_dir': True, 'children': {}}
            build_tree(path, padding + "    ", tree_dict[item]['children'], ignore_dirs)
        elif not os.path.isdir(path):
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
    build_tree(directory, '', tree_dict, ignore_dirs)  # pass the correct directory path
    tree_str = format_tree(tree_dict)
    with open(output_file_path, 'w', encoding='utf-8') as output_file:  # open with 'w' to write the tree
        output_file.write(tree_str.rstrip('\r\n') + '\n\n')  # write the tree followed by two newlines

def append_to_file_markdown_style(relative_path: str, file_content: str, output_file) -> None:
    language = get_language_from_extension(relative_path)
    # Write the header with the relative path and the file content wrapped in a code block
    output_file.write(f"# File: {relative_path}\n```{language}\n{file_content}\n```\n# End of file: {relative_path}\n\n")

def ignore_dir(dir_path: str, ignore_dirs: list, git_path: str) -> bool:
    # Convert dir_path to an absolute path for comparison
    dir_path_abs = os.path.abspath(dir_path)
    for _dir in ignore_dirs:
        # Construct the absolute path for the ignored directory
        _dir_abs = os.path.abspath(os.path.join(git_path, _dir))
        # Check if dir_path_abs starts with the constructed absolute ignored directory

        if dir_path_abs.startswith(_dir_abs):
            return True
    return False

def ignore_file(file_path: str, ignore_files: list, git_path: str) -> bool:
    # Convert file_path to an absolute path for comparison
    file_path_abs = file_path
    for ignore_file in ignore_files:
        # Construct the absolute path for the ignored file
        ignore_file_abs = os.path.abspath(os.path.join(git_path, ignore_file.replace('\\', os.sep)))
        # Check if file_path_abs matches the constructed absolute ignored file path
        if file_path_abs == ignore_file_abs:
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
            # Check if file's parent dir is to be ignored, continue if true
            if any(ignore_dir(os.path.join(root, d), ignore_dirs, git_path) for d in dirs):
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

def main():
    ignore_files = os.environ.get('IGNORE_FILES', '').split(',')
    ignore_dirs = os.environ.get('IGNORE_DIRS', '').split(',')

    skip_empty_files = os.environ.get('SKIP_EMPTY_FILES', 'false').upper() == 'TRUE'

    # Determine git_path either from environment variable or command-line argument
    git_path = os.environ.get('GIT_PROJECT_DIRECTORY', '')
    if '-path' in sys.argv:
        path_index = sys.argv.index('-path') + 1
        if path_index < len(sys.argv):
            git_path = sys.argv[path_index]
    if not os.path.isdir(git_path):
        print(f'Path not found or not a directory: {git_path}')
        sys.exit(1)        

    save_directory = os.environ.get('SAVE_DIRECTORY', '.')
    if not os.path.isdir(save_directory):
        os.makedirs(save_directory, exist_ok=True)

    output_file_name = os.path.basename(git_path.rstrip(os.sep)) + '.md'
    output_file_path = os.path.join(save_directory, output_file_name)

    # Ensure the output file is empty at the start
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    include_files = [
        "main.py",
        "backend/server.py",
        "backend/utils.py",
        "gpt_researcher/__init__.py",
        "gpt_researcher/config/config.py",
        "gpt_researcher/config/__init__.py",
        "gpt_researcher/context/compression.py",
        "gpt_researcher/context/retriever.py",
        "gpt_researcher/context/__init__.py",
        "gpt_researcher/master/agent.py",
        "gpt_researcher/master/functions.py",
        "gpt_researcher/master/prompts.py",
        "gpt_researcher/master/__init__.py",
        "gpt_researcher/memory/embeddings.py",
        "gpt_researcher/memory/__init__.py",
        "gpt_researcher/retrievers/__init__.py",
        "gpt_researcher/retrievers/bing/bing.py",
        "gpt_researcher/retrievers/duckduckgo/duckduckgo.py",
        "gpt_researcher/retrievers/google/google.py",
        "gpt_researcher/retrievers/searx/searx.py",
        "gpt_researcher/retrievers/serpapi/serpapi.py",
        "gpt_researcher/retrievers/serper/serper.py",
        "gpt_researcher/retrievers/tavily_news/tavily_news.py",
        "gpt_researcher/retrievers/tavily_search/tavily_search.py",
        "gpt_researcher/scraper/scraper.py",
        "gpt_researcher/scraper/__init__.py",
        "gpt_researcher/scraper/arxiv/arxiv.py",
        "gpt_researcher/scraper/beautiful_soup/beautiful_soup.py",
        "gpt_researcher/scraper/newspaper/newspaper.py",
        "gpt_researcher/scraper/pymupdf/pymupdf.py",
        "gpt_researcher/scraper/web_base_loader/web_base_loader.py",
        "gpt_researcher/utils/llm.py",
        "gpt_researcher/utils/websocket_manager.py",
        "docs/docusaurus.config.js",
        "docs/sidebars.js",
        "docs/docs/welcome.md",
        "docs/docs/faq.md",
        "docs/docs/contribute.md",
        "docs/docs/gpt-researcher/introduction.md",
        "docs/docs/gpt-researcher/getting-started.md",
        "docs/docs/gpt-researcher/config.md",
        "docs/docs/gpt-researcher/example.md",
        "docs/docs/gpt-researcher/agent_frameworks.md",
        "docs/docs/gpt-researcher/pip-package.md",
        "docs/docs/gpt-researcher/troubleshooting.md",
        "docs/docs/tavily-api/introduction.md",
        "docs/docs/tavily-api/python-sdk.md",
        "docs/docs/tavily-api/rest_api.md",
        "docs/docs/tavily-api/langchain.md",
        "docs/docs/tavily-api/llamaindex.md",
        "docs/docs/tavily-api/Topics/01-introduction.md",
        "docs/docs/tavily-api/Topics/code.md",
        "docs/docs/tavily-api/Topics/finance.md",
        "docs/docs/tavily-api/Topics/news.md",
        "docs/docs/tavily-api/Topics/people.md",
        "docs/docs/reference/sidebar.json",
        "docs/docs/reference/config/config.md",
        "docs/docs/reference/config/singleton.md",
        "docs/docs/reference/processing/html.md",
        "docs/docs/reference/processing/text.md"
        ]
    write_tree_to_file_with_included_files(git_path, output_file_path, include_files)
    process_files(git_path, output_file_path, skip_empty_files, include_files)

#    write_tree_to_file(git_path, output_file_path, ignore_dirs)  # add the ignore_dirs parameter
#    process_path(git_path, ignore_files, ignore_dirs, output_file_path, skip_empty_files)

    print(f"All contents have been written to: {output_file_path}")

if __name__ == '__main__':
    main()
