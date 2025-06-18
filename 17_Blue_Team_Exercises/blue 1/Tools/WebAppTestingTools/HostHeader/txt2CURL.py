import sys
import subprocess
import shlex
import os
import re
import argparse

def parse_request_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read().strip()

    lines = content.split('\n')
    first_line = lines[0].split()
    method, path, _ = first_line if len(first_line) >= 3 else ('GET', '/', 'HTTP/1.1')

    headers = []
    body = ''
    reading_headers = True
    host = ''
    cookies = ''

    for line in lines[1:]:
        if reading_headers:
            if line.strip() == '':
                reading_headers = False
                continue
            if line.lower().startswith('host:'):
                host = line.split(':', 1)[1].strip()
            elif line.lower().startswith('cookie:'):
                cookies = line.split(':', 1)[1].strip()
            else:
                headers.append(line.strip())
        else:
            body += line + '\n'

    return method, path, host, headers, cookies, body.strip()


def format_as_curl(method, path, host, headers, cookies, body):
    curl_command = ["curl", "--path-as-is", "-i", "-s", "-k"]
    curl_command.extend(["-X", method])

    for header in headers:
        if not header.lower().startswith(('host:', 'cookie:')):
            curl_command.extend(["-H", header])

    if cookies:
        curl_command.extend(["-b", cookies])

    if body:
        curl_command.extend(["-d", body])

    full_url = f"https://{host}{path}"
    curl_command.append(full_url)

    return " ".join(curl_command)


def execute_curl(curl_command):
    print("Executing curl command:")
    print(curl_command)
    print("\nResponse:")
    try:
        result = subprocess.run(shlex.split(curl_command), capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        return result.stdout
    except Exception as e:
        print(f"Error executing curl command: {e}")
        return None


def check_response_and_log(response, technique_name, file_identifier, output_dir):
    if response:
        status_match = re.search(r'HTTP/[1-2](?:\.\d)?\s+200', response)
        if status_match:
            status_line = status_match.group(0)
            alarm_message = f"200 Response detected for technique '{technique_name}' (File {file_identifier}): {status_line}\n"

            alarm_file = os.path.join(output_dir, 'alarm.txt')
            with open(alarm_file, 'a') as file:
                file.write(alarm_message)

            print(f"Alarm logged: {alarm_message}")
        else:
            print(f"No 200 status code detected for technique '{technique_name}' (File {file_identifier}).")
    else:
        print(f"No response received for technique '{technique_name}' (File {file_identifier}).")

def get_file_identifier(file_name):
    match = re.search(r'(\d+)\.txt$', file_name)
    return match.group(1) if match else "unknown"

def process_folder(folder_path, output_dir):
    technique_name = os.path.basename(folder_path)
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(folder_path, file_name)
            file_identifier = get_file_identifier(file_name)

            print(f"\nProcessing file: {file_path}")
            method, path, host, headers, cookies, body = parse_request_file(file_path)
            curl_command = format_as_curl(method, path, host, headers, cookies, body)
            response = execute_curl(curl_command)

            check_response_and_log(response, technique_name, file_identifier, output_dir)

def process_parent_folder(parent_folder, output_dir):
    for item in os.listdir(parent_folder):
        item_path = os.path.join(parent_folder, item)
        if os.path.isdir(item_path):
            print(f"\nProcessing folder: {item_path}")
            process_folder(item_path, output_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="txt2CURL Processor")
    parser.add_argument("parent_folder", help="Parent folder containing technique folders")
    parser.add_argument("--business", required=True, help="Business name")
    parser.add_argument("--asset_type", required=True, help="Asset type")
    parser.add_argument("--asset_value", required=True, help="Asset value")

    args = parser.parse_args()

    base_output_dir = "C:/BugBounty/Results"
    output_dir = os.path.join(base_output_dir, args.business, args.asset_type, args.asset_value,
                              "Advanced Topics", "host-header", "Techniques")

    process_parent_folder(args.parent_folder, output_dir)