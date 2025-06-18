import os
import subprocess
import re
import argparse

def run_dirb(url, output_folder):
    output_file = os.path.join(output_folder, f"dirb_results_{url.replace('://', '_').replace('.', '_')}.txt")
    command = [
        "dirb",
        f"https://{url}",  # Assuming HTTPS, adjust if needed
        "/usr/share/dirb/wordlists/common.txt",
        "-X", ".graphql,.gql",  # Looking for GraphQL file extensions
        "-a", "HackerOne",
        "-r",
        "-o", output_file
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        return output_file, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return output_file, e.output, e.stderr

def process_results(output_file, stdout, stderr, alarm_file):
    with open(output_file, 'r') as f:
        content = f.read()

    match = re.search(r'DOWNLOADED: (\d+) - FOUND: (\d+)', content)
    if match:
        downloaded, found = map(int, match.groups())
        if downloaded > 0 or found > 0:
            with open(alarm_file, 'a') as af:
                af.write(f"Alert for {output_file}: DOWNLOADED: {downloaded} - FOUND: {found}\n")
    else:
        with open(alarm_file, 'a') as af:
            af.write(f"Alert for {output_file}: 'DOWNLOADED: 0 - FOUND: 0' not found in output\n")

def main(base_folder, business, asset_type, asset_value):
    base_output_dir = "/home/kali/Desktop/BugBountyWork"
    output_dir = os.path.join(base_output_dir, business, asset_type, asset_value,
                              "WEBENVFINAL", "Advanced Topics", "GraphQL", "Techniques")
    os.makedirs(output_dir, exist_ok=True)
    alarm_file = os.path.join(output_dir, "GraphQL_Alarm_Dirb.txt")

    for root, dirs, files in os.walk(base_folder):
        if "URL" in dirs:
            url_folder = os.path.join(root, "URL")
            for url_dir in os.listdir(url_folder):
                url = url_dir
                print(f"Processing URL: {url}")
                output_file, stdout, stderr = run_dirb(url, output_dir)
                process_results(output_file, stdout, stderr, alarm_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dirb Scanner for GraphQL")
    parser.add_argument("base_folder", help="Base folder containing URL directories")
    parser.add_argument("--business", required=True, help="Business name")
    parser.add_argument("--asset_type", required=True, help="Asset type")
    parser.add_argument("--asset_value", required=True, help="Asset value")

    args = parser.parse_args()

    main(args.base_folder, args.business, args.asset_type, args.asset_value)
