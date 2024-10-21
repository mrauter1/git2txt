import os
import sys
import subprocess
import ctypes
import platform

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
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.'], check=True)
        print("Package installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing the package: {e}")
        sys.exit(1)

    # Retrieve the package installation location
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'show', 'git2text'], capture_output=True, text=True, check=True)
        output = result.stdout
        location = None
        for line in output.splitlines():
            if line.startswith('Location:'):
                location = line.split(':', 1)[1].strip()
                break
        if not location:
            print("Could not determine the package installation location.")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while retrieving package information: {e}")
        sys.exit(1)

    # Determine the scripts path from the location
    scripts_path = os.path.join(location, '..', 'Scripts')
    if not os.path.exists(scripts_path):
        # On Unix-based systems or if Scripts does not exist, try 'bin'
        scripts_path = os.path.join(location, '..', 'bin')
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
            print(f"Successfully updated {variable} in {scope} environment variables.")
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
        print("Failed to add scripts path to PATH variable.")
        print("Please consider cleaning up your PATH variable or use the script from its full path.")

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
    install_package()
    scripts_path = install_package()
    print(f"Python Scripts path: {scripts_path}")

    if platform.system() == 'Windows':
        check_and_add_scripts_path_windows(scripts_path)
    else:
        check_and_create_symlink_unix(scripts_path)

if __name__ == '__main__':
    main()
