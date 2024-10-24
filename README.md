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

