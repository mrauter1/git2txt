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