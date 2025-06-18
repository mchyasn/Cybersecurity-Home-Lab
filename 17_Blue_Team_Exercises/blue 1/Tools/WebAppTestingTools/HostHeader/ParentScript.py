import subprocess
import os

def run_script(script_name, path):
    print(f"\nRunning {script_name}...")
    try:
        result = subprocess.run(['python', script_name, path], check=True, text=True, capture_output=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(e.output)

def main():
    # Get the path from user input
    path = input("Please enter the path to the parent folder: NOTE IF YOU ARE SEEING THIS EDIT THE SCRIPT TO AUTOMATE THIS").strip()

    # Validate the path
    if not os.path.isdir(path):
        print("Error: The provided path is not a valid directory.")
        return

    # Run HeaderAttackV1.py
    run_script("HeaderAttackV1.py", path)

    # Run txt2CURLv3.py
    run_script("txt2CURLv3.py", path)

    print("\nBoth scripts have been executed successfully.")

if __name__ == "__main__":
    main()