import os
import subprocess
import re
import argparse

def run_dirb(url, output_folder, wordlist):
    output_file = os.path.join(output_folder, f"dirb_results_{url.replace('://', '_').replace('.', '_')}.txt")
    command = [
        "dirb",
        f"https://{url}",  # Assuming HTTPS, adjust if needed
        wordlist,
        "-X", ".php",
        "-a", "HackerOne",
        "-r",
        "-o", output_file
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        return output_file, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return output_file, e.output, e.stderr

def process_results(output_file, stdout, stderr, alarm_file, wordlist):
    with open(output_file, 'r') as f:
        content = f.read()

    match = re.search(r'DOWNLOADED: (\d+) - FOUND: (\d+)', content)
    if match:
        downloaded, found = map(int, match.groups())
        if downloaded > 0 or found > 0:
            with open(alarm_file, 'a') as af:
                af.write(f"Alert for {output_file}: DOWNLOADED: {downloaded} - FOUND: {found}\n")

    # Check for wordlist matches
    with open(wordlist, 'r') as wf:
        endpoints = wf.read().splitlines()

    for endpoint in endpoints:
        if endpoint in content:
            with open(alarm_file, 'a') as af:
                af.write(f"Alert for {output_file}: Found endpoint '{endpoint}'\n")

def main(base_folder, wordlist, business, asset_type, asset_value, xml_file=None):
    base_output_dir = "/home/kali/Desktop/BugBountyKaliFinal"
    output_dir = os.path.join(base_output_dir, business, asset_type, asset_value,
                              "Advanced Topics", "oauth", "Techniques", "basic-oauth")
    os.makedirs(output_dir, exist_ok=True)

    alarm_file = os.path.join(output_dir, 'Alarm_Dirb.txt')

    for root, dirs, files in os.walk(base_folder):
        if "URL" in dirs:
            url_folder = os.path.join(root, "URL")
            for url_dir in os.listdir(url_folder):
                url = url_dir
                print(f"Processing URL: {url}")
                output_file, stdout, stderr = run_dirb(url, output_dir, wordlist)
                process_results(output_file, stdout, stderr, alarm_file, wordlist)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OAuth Dirb Scanner")
    parser.add_argument("base_folder", help="Base folder containing URL directories")
    parser.add_argument("wordlist", help="Path to the OAuth endpoints wordlist")
    parser.add_argument("--business", required=True, help="Business name")
    parser.add_argument("--asset_type", required=True, help="Asset type")
    parser.add_argument("--asset_value", required=True, help="Asset value")
    parser.add_argument("--xml_file", help="XML file (not used by this script, but included for compatibility)")

    args = parser.parse_args()

    main(args.base_folder, args.wordlist, args.business, args.asset_type, args.asset_value, args.xml_file)
