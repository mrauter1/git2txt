# Git2Text - Codebase Extraction Utility

Git2Text is an utility that simplifies the process of extracting and formatting the entire structure of a codebase into a single text file. Whether you're working with a local Git project, a remote Git repository, or any other codebase, Git2Text is perfect for copying and pasting your code into ChatGPT or other large language models (LLMs). With Git2Text, you can avoid the hassle of manually copying and pasting the source for LLM consumption.

## Features

- **Extract Complete Codebase**: Convert your entire codebase into a Markdown-formatted text.
- **Support for Local and Remote Repositories**: Work with local directories or clone remote Git repositories on-the-fly.
- **Tree View Representation**: Automatically generate a directory structure to provide context.
- **Code Block Formatting**: Files are formatted with appropriate syntax highlighting for better readability.
- **Easy Copy to Clipboard**: Quickly copy the output for pasting into LLMs like ChatGPT.
- **GLOB Pattern Support**: Use powerful GLOB patterns for fine-grained control over file inclusion and exclusion.
- **.gitignore Integration**: Respect .gitignore rules by default, with option to override.
- **Cross-Platform Compatibility**: Works on Windows, macOS, and Linux.
  
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

Run the script directly from your terminal or command prompt:

```bash
python git2text.py <path-or-url> [options]
```

The <path-or-url> can be:

A path to a local directory containing your codebase
A Git repository URL (e.g., https://github.com/username/repo.git)

### Options

- **`-o, --output`**: Specify the output file path.
- **`-if, --ignore-files`**: List of files to ignore (supports glob patterns).
- **`-id, --ignore-dirs`**: List of directories to ignore (supports glob patterns).
- **`-inc, --include-files`**: List of files to include. If specified, only these files will be processed.
- **`-se, --skip-empty-files`**: Skip empty files during extraction.
- **`-cp, --clipboard`**: Copy the generated content to the clipboard.
- **`-igi, --ignoregitignore`**: Ignore the `.gitignore` file when specified.

### Example Usage

### Options

- **-o, --output**: Specify the output file path.
- **-if, --ignore-files**: List of files to ignore (supports glob patterns).
- **-id, --ignore-dirs**: List of directories to ignore (supports glob patterns).
- **-inc, --include-files**: List of files to include. If specified, only these files will be processed.
- **-se, --skip-empty-files**: Skip empty files during extraction.
- **-cp, --clipboard**: Copy the generated content to the clipboard.
- **-igi, --ignoregitignore**: Ignore the .gitignore file when specified.

### Example Usage

#### Extract Entire Codebase from a Local Directory to a Markdown File

```bash
python git2text.py /path/to/local/codebase -o output.md
```

#### Clone and Extract a Remote Git Repository

```bash
python git2text.py https://github.com/username/repo.git -o output.md
```

This command will clone the specified repository to a temporary directory, extract its contents, and save the output to `output.md`.

#### Extract Only Specific Files and Copy to Clipboard

```bash
python git2text.py /path/to/codebase -inc "*.py"
```

#### Skip .gitignore and Empty Files

```bash
python git2text.py https://github.com/username/repo.git -igi -se -o output.md
```

#### Ignore Specific Files and Directories

```bash
python git2text.py /path/to/codebase -if "*.log" -id "__pycache__" -o output.md
```

#### Include Only Specific Files

```bash
python git2text.py https://github.com/username/repo.git -inc "src/**/*.py" -o output.md
```

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

## Contributing

Feel free to contribute to the project by opening an issue or submitting a pull request. We welcome feedback and suggestions to improve **Git2Text**!

## License

This project is licensed under the MIT License.

## Contact

For any questions or support, please open an issue on the GitHub repository.

---


