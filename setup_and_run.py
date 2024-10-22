import os
import subprocess
import sys
import platform


def create_virtualenv(venv_dir='venv'):
    """Create a virtual environment if it doesn't exist."""
    if not os.path.exists(venv_dir):
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])
        print(f"Virtual environment created in {venv_dir}")
    else:
        print("Virtual environment already exists.")


def activate_virtualenv(venv_dir='venv'):
    """Activate the virtual environment."""
    if platform.system() == 'Windows':
        activate_script = os.path.join(venv_dir, 'Scripts', 'activate')
    else:
        activate_script = os.path.join(venv_dir, 'bin', 'activate')

    print(f"Activating virtual environment: {activate_script}")

    if platform.system() == 'Windows':
        activate_cmd = f"{venv_dir}\\Scripts\\activate"
        subprocess.call(activate_cmd, shell=True)
    else:
        activate_cmd = f"source {venv_dir}/bin/activate"
        os.system(activate_cmd)


def install_requirements(venv_dir='venv'):
    """Install the dependencies from requirements.txt into the virtual environment."""
    requirements_file = 'requirements.txt'
    if not os.path.exists(requirements_file):
        print(f"Error: {requirements_file} file not found.")
        sys.exit(1)

    pip_path = os.path.join(venv_dir, 'bin', 'pip') if platform.system() != 'Windows' else os.path.join(venv_dir,
                                                                                                        'Scripts',
                                                                                                        'pip')

    print("Installing dependencies from requirements.txt...")
    subprocess.check_call([pip_path, 'install', '-r', requirements_file])
    print("Dependencies installed successfully.")


def run_application(venv_dir='venv', app_entry='src/main.py'):
    """Run the main Python application."""
    python_path = os.path.join(venv_dir, 'bin', 'python') if platform.system() != 'Windows' else os.path.join(venv_dir,
                                                                                                              'Scripts',
                                                                                                              'python')

    if not os.path.exists(app_entry):
        print(f"Error: {app_entry} not found.")
        sys.exit(1)

    print(f"Running the application: {app_entry}")
    subprocess.check_call([python_path, app_entry])


if __name__ == '__main__':
    venv_dir = 'venv'
    app_entry = 'src/main.py'  # You can customize the entry point

    create_virtualenv(venv_dir)
    install_requirements(venv_dir)
    run_application(venv_dir, app_entry)
