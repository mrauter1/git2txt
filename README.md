# Project Tree Markdown Generator

This Python script generates a Markdown-formatted tree structure and content of a specified directory. The generated output file can serve as documentation for your codebase, making it easier to navigate and understand the project structure.

## Features

- Generates a directory tree in Markdown format.
- Includes the content of the files in Markdown code blocks.
- Customizable file and directory inclusion or exclusion.

## Requirements

- Python 3.6 or later

## Installation

Clone this repository to your local machine:

```sh
$ git clone <repository_url>
$ cd <repository_folder>
```

## Usage

Run the script using Python, specifying the directory to generate the tree for. Optionally, specify the output path, files/directories to include or ignore, and whether to skip empty files.

### Basic Usage

```sh
$ python main.py /path/to/your/project
```

This command generates a Markdown file (`project.md`) in the current directory with the tree structure and contents of the specified path.

### Specifying an Output File

```sh
$ python main.py /path/to/your/project -o /path/to/output/your_output.md
```

This command saves the output to the specified file.

### Ignoring Specific Files and Directories

You can ignore files and directories using glob patterns:

```sh
$ python main.py /path/to/your/project -if "*.log" "*.tmp" -id "__pycache__" "node_modules"
```

This command ignores all `.log` and `.tmp` files and the directories named `__pycache__` and `node_modules`.

### Including Specific Files Only

You can also specify which files to include using glob patterns. When you specify `--include-files`, only the specified files will be included:

```sh
$ python main.py /path/to/your/project -inc "**/*.py" "README.md"
```

This command only includes Python files and the `README.md` file.

### Skipping Empty Files

To skip empty files during processing:

```sh
$ python main.py /path/to/your/project --skip-empty-files
```

This command will skip empty files when generating the output.

## Example

Suppose you have the following project structure:

```
project/
├── src/
│   ├── main.py
│   ├── utils.py
│   └── __init__.py
├── README.md
└── requirements.txt
```

Running the command:

```sh
$ python main.py project
```

Would generate a `project.md` file with the following content:

```markdown
# Tree Structure

```
project/
├── src/
│   ├── main.py
│   ├── utils.py
│   └── __init__.py
├── README.md
└── requirements.txt
```


# File: src/main.py
```python
# Example Python code in main.py
print("Hello, world!")
```
# End of file: src/main.py

# File: src/utils.py
```python
# Utility functions for the project
def add(a, b):
    return a + b
```
# End of file: src/utils.py

...
```

## Command-Line Options

- `path` (positional): Path to the project directory.
- `-o, --output`: Optional output file path. Defaults to `project.md` in the current directory.
- `-if, --ignore-files`: List of files to ignore (supports glob patterns).
- `-id, --ignore-dirs`: List of directories to ignore (supports glob patterns).
- `-inc, --include-files`: List of files to include (supports glob patterns). If specified, only these files will be included.
- `--skip-empty-files`: Skip empty files.

## License

This project is licensed under the MIT License.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests. Any contributions are welcome!


