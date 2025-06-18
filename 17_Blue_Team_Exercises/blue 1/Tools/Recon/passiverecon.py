import subprocess
import os
import csv
import json
import shutil
import argparse


def run_nmap_scans(asset_value, output_file):
    nmap_commands = [
        f"sudo nmap -sS -O '{asset_value}' -oN '{output_file}_1.txt'",
        f"sudo nmap -sU -p 123,161,500 '{asset_value}' -oN '{output_file}_2.txt'",
        f"sudo nmap -sV --version-intensity 5 '{asset_value}' -oN '{output_file}_3.txt'"
    ]
    for cmd in nmap_commands:
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {cmd}")
            print(f"Error message: {e}")

    with open(output_file, 'w') as outfile:
        for i in range(1, 4):
            if os.path.exists(f"{output_file}_{i}.txt"):
                with open(f"{output_file}_{i}.txt") as infile:
                    outfile.write(infile.read())
                os.remove(f"{output_file}_{i}.txt")
            else:
                print(f"Warning: {output_file}_{i}.txt not found")


def process_nmap_output(input_file, output_csv):
    awk_command = f"awk '/^[0-9]/ {{print $1\",\"$2\",\"$3}}' '{input_file}' > '{output_csv}'"
    subprocess.run(awk_command, shell=True, check=True)


def get_open_ports(csv_file):
    open_ports = set()
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if len(row) >= 2 and 'open' in row[1]:
                open_ports.add(row[0])  # Keep the full port specification (e.g., "80/tcp")
    print(f"Open ports found: {open_ports}")
    return open_ports


def parse_port(port_str):
    # Handle both "80" and "80/tcp" formats
    return port_str.split('/')[0]


def copy_relevant_folders(json_file, open_ports, source_base, dest_base):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: JSON file {json_file} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {json_file}.")
        return

    print(f"Loaded JSON data: {data}")

    for service, info in data.items():
        service_ports = set(info['ports'].split(','))
        print(f"Checking service {service} with ports {service_ports}")

        # Check for matches in both full specification and port number only
        if any(parse_port(sp) in [parse_port(op) for op in open_ports] for sp in
               service_ports) and 'folder_path' in info:
            # Remove any leading '~' or '/' from the folder_path
            relative_path = info['folder_path'].lstrip('~/').lstrip('/')
            source_folder = os.path.join(source_base, relative_path)
            dest_folder = os.path.join(dest_base, os.path.basename(relative_path))
            print(f"Matching ports found for {service}. Attempting to copy from {source_folder} to {dest_folder}")
            if os.path.exists(source_folder):
                shutil.copytree(source_folder, dest_folder, dirs_exist_ok=True)
                print(f"Copied {source_folder} to {dest_folder}")
            else:
                print(f"Source folder {source_folder} does not exist for service {service}")
        else:
            print(f"No matching ports for service {service}")


def create_directory(path):
    os.makedirs(path, exist_ok=True)
    os.chmod(path, 0o755)


def main():
    parser = argparse.ArgumentParser(description='Bug Bounty Reconnaissance Automation')
    parser.add_argument('--business', required=True, help='Business name')
    parser.add_argument('--asset_type', required=True, help='Asset type')
    parser.add_argument('--asset_value', required=True, help='Asset value (e.g., IP address or hostname)')
    parser.add_argument('--base_url', required=True, help='Base URL for file operations')
    args = parser.parse_args()

    passive_recon_path = os.path.join(args.base_url, args.business, args.asset_type, args.asset_value,
                                      "Passive Reconnaissance")
    active_recon_path = os.path.join(args.base_url, args.business, args.asset_type, args.asset_value,
                                     "Active Reconnaissance")
    create_directory(passive_recon_path)
    create_directory(active_recon_path)

    nmap_output = os.path.join(passive_recon_path, "nmap_output.txt")
    run_nmap_scans(args.asset_value, nmap_output)

    nmap_csv = os.path.join(passive_recon_path, "nmap_results.csv")
    process_nmap_output(nmap_output, nmap_csv)

    open_ports = get_open_ports(nmap_csv)

    # Copy relevant folders based on open ports
    json_file = '/home/kali/Desktop/JSONMakerWebTwo/PortDB.json'  # Replace with your JSON file path
    source_base = '/home/kali/Desktop/JSONMakerWebTwo/NetTestFoldRepo'  # Replace with the base path of your test folders
    copy_relevant_folders(json_file, open_ports, source_base, active_recon_path)


if __name__ == "__main__":
    main()