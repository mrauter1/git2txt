# Git2Text - Codebase Extraction Utility

Welcome to **Git2Text**! This utility simplifies the process of extracting and formatting the entire structure of a codebase into a single text file. Whether you're working with a Git project or any other codebase, **Git2Text** is perfect for copying and pasting your code into ChatGPT or other large language models (LLMs), making your conversations more informative and streamlined.

The tool provides a structured output of your repository's files along with their content, all in Markdown format, which makes it readable and organized for LLMs. With **Git2Text**, you can avoid the hassle of manually extracting, organizing, and presenting your codebase.

## Features

- **Extract Complete Codebase**: Convert your entire codebase into a Markdown-formatted text.
- **Tree View Representation**: Automatically generate a directory structure to provide context.
- **Code Block Formatting**: Files are formatted with appropriate syntax highlighting for better readability.
- **Easy Copy to Clipboard**: Quickly copy the output for pasting into LLMs like ChatGPT.
- **Customizable Filtering**: Control which files or directories to include or ignore using `.gitignore` rules or command-line flags.

## File Overview

The repository contains the following files:

```
├── .gitignore
├── RAG prompt example.txt
├── README.md
├── git2text.bat
└── git2text.py
```

### File Descriptions

- **`.gitignore`**: Specifies which files and folders to exclude during extraction (useful for Git projects).
- **`RAG prompt example.txt`**: A sample prompt for using the output with LLMs.
- **`README.md`**: This file, containing the documentation for the project.
- **`git2text.bat`**: Windows batch script for running `git2text.py` with ease.
- **`git2text.py`**: The main Python script that processes the codebase and generates the Markdown output.

## Prerequisites

- **Python 3.6+**
- **Pathspec** library for `.gitignore` parsing (Install via `pip install pathspec`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/git2text.git
   cd git2text
   ```
2. Install dependencies:
   ```bash
   pip install pathspec
   ```

## Usage

### Running the Script

You can run the script using either the provided batch file (`git2text.bat`) or directly through Python.

#### Option 1: Using Batch File (Windows Only)

1. Double-click `git2text.bat`.
2. Enter the path to your codebase when prompted.

#### Option 2: Using Python

Run the script directly from your terminal or command prompt:

```bash
python git2text.py <path-to-your-codebase> [options]
```

### Options

- **`-o, --output`**: Specify the output file path.
- **`-if, --ignore-files`**: List of files to ignore (supports glob patterns).
- **`-id, --ignore-dirs`**: List of directories to ignore (supports glob patterns).
- **`-inc, --include-files`**: List of files to include. If specified, only these files will be processed.
- **`-se, --skip-empty-files`**: Skip empty files during extraction.
- **`-cp, --clipboard`**: Copy the generated content to the clipboard.
- **`-igi, --ignoregitignore`**: Ignore the `.gitignore` file when specified.

### Example Usage

#### Extract Entire Codebase to a Markdown File

```bash
python git2text.py /path/to/codebase -o output.md
```

This command will generate a `output.md` file containing the entire codebase in a readable Markdown format, including a tree structure representation and the contents of all files.

#### Extract Only Specific Files and Copy to Clipboard

```bash
python git2text.py /path/to/codebase -inc "*.py" -cp
```

This command will extract only Python files (`*.py`) from the specified codebase and copy the output directly to the clipboard for easy pasting.

#### Skip `.gitignore` and Empty Files

```bash
python git2text.py /path/to/codebase -igi -se -o output.md
```

This command will ignore the `.gitignore` file, skip any empty files, and save the output to `output.md`.

#### Ignore Specific Files and Directories

```bash
python git2text.py /path/to/codebase -if "*.log" -id "__pycache__" -o output.md
```

This command will ignore all `.log` files and the `__pycache__` directory while generating the Markdown output.

#### Include Only Specific Files

```bash
python git2text.py /path/to/codebase -inc "src/**/*.py" -o output.md
```

This command will include only Python files within the `src` directory (including subdirectories) and generate the output to `output.md`.

## Example Output

The output of **Git2Text** follows a Markdown structure for easy readability. Here's a sample of how it formats the files:
````
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

This format helps provide syntax-highlighted code blocks, making it much easier for LLMs to understand your code.

## Tips for Using with LLMs

- **Tree Representation**: The directory tree provides context to the LLM on the project structure, making it easier to understand relationships between files.
- **Comment Your Code**: The better commented your code is, the more context the LLM will have, resulting in better quality responses.
- **RAG Prompting**: Use the `RAG prompt example.txt` file to guide LLMs on how to interpret and work with your extracted code.

## Contributing

Feel free to contribute to the project by opening an issue or submitting a pull request. We welcome feedback and suggestions to improve **Git2Text**!

## License

This project is licensed under the MIT License.

## Contact

For any questions or support, please open an issue on the GitHub repository.

---

Happy coding, and enjoy seamless interaction with your favorite LLMs using **Git2Text**! 🚀

