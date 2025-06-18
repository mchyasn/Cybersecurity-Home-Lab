import argparse
import os
import subprocess


def parse_arguments():
    parser = argparse.ArgumentParser(description="Bug Bounty Reconnaissance Script")
    parser.add_argument("--base_url", required=True, help="Base URL (e.g., BugBounty)")
    parser.add_argument("--business", required=True, help="Business name (e.g., Hilton)")
    parser.add_argument("--asset_type", required=True, help="Asset type (e.g., IPAddress)")
    parser.add_argument("--asset_value", required=True, help="Asset value (e.g., 192.0.0.1)")
    return parser.parse_args()


def build_path(args):
    return os.path.join(args.base_url, args.business, args.asset_type, args.asset_value)


def run_python_files(base_path):
    recon_path = os.path.join(base_path, "Active Reconnaissance")

    if not os.path.exists(recon_path):
        print(f"Error: Path does not exist: {recon_path}")
        return

    for folder in os.listdir(recon_path):
        folder_path = os.path.join(recon_path, folder)
        if os.path.isdir(folder_path):
            python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]

            if len(python_files) == 1:
                python_file = os.path.join(folder_path, python_files[0])
                print(f"Executing: {python_file}")
                try:
                    subprocess.run(["python", python_file], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error executing {python_file}: {e}")
            elif len(python_files) == 0:
                print(f"No Python file found in {folder_path}")
            else:
                print(f"Multiple Python files found in {folder_path}, skipping...")


def main():
    args = parse_arguments()
    base_path = build_path(args)
    run_python_files(base_path)


if __name__ == "__main__":
    main()