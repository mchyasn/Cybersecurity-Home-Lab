import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import argparse

# Hardcoded path for identifiers file
IDENTIFIERS_FILE = "/home/kali/Desktop/BugBountyKaliFinal/Tools/WebAppTestingPythonFiles/GRAPHQLTests/graphql_identifiers.txt"

def read_wordlist(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def fetch_source(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def check_url(url, identifiers):
    source = fetch_source(url)
    if source is None:
        return None
    found_identifiers = []
    for identifier in identifiers:
        if identifier in source:
            found_identifiers.append(identifier)
    if found_identifiers:
        return (url, found_identifiers)
    return None

def main(urls_file, business, asset_type, asset_value):
    urls = read_wordlist(urls_file)
    identifiers = read_wordlist(IDENTIFIERS_FILE)

    base_output_dir = "/home/kali/Desktop/BugBountyWork"
    output_dir = os.path.join(base_output_dir, business, asset_type, asset_value,
                              "WEBENVFINAL", "Advanced Topics", "GraphQL", "Techniques")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "GraphQL_Alarm_VS.txt")

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(check_url, url, identifiers): url for url in urls}
        with open(output_file, 'w') as alarm_file:
            for future in as_completed(future_to_url):
                result = future.result()
                if result:
                    url, found_identifiers = result
                    alarm_message = f"GraphQL identifiers found in {url}: {', '.join(found_identifiers)}\n"
                    alarm_file.write(alarm_message)
                    print(alarm_message.strip())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vulnerability Scanner for GraphQL")
    parser.add_argument("urls_file", help="File containing URLs to scan")
    parser.add_argument("--business", required=True, help="Business name")
    parser.add_argument("--asset_type", required=True, help="Asset type")
    parser.add_argument("--asset_value", required=True, help="Asset value")
    args = parser.parse_args()

    main(args.urls_file, args.business, args.asset_type, args.asset_value)
