import xml.etree.ElementTree as ET
import base64
import os
import subprocess
import shlex
import re
import argparse

def decode_base64(encoded_text):
    return base64.b64decode(encoded_text).decode('utf-8', errors='ignore')

def modify_request_for_cors(request, technique):
    lines = request.split('\n')
    method_line = lines[0]
    headers = lines[1:]

    if technique == "BasicACAO":
        headers.insert(0, "Origin: http://localhost:8000")
    elif technique == "BasicWhiteList":
        headers.insert(0, "Origin: https://www.google.com")
    elif technique == "NullWhiteList":
        headers.insert(0, "Origin: null")

    return '\n'.join([method_line] + headers)


def parse_request(request):
    lines = request.split('\n')
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
    try:
        result = subprocess.run(shlex.split(curl_command), capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Error executing curl command: {e}")
        return None


def check_cors_headers(response, technique, item_number, output_dir):
    if response:
        acao_match = re.search(r'Access-Control-Allow-Origin:\s*(.+)', response)
        acac_match = re.search(r'Access-Control-Allow-Credentials:\s*true', response, re.IGNORECASE)

        if acao_match and acac_match:
            acao_value = acao_match.group(1).strip()
            alarm_message = f"CORS vulnerability detected for technique '{technique}' in Item {item_number}:\n"
            alarm_message += f"Access-Control-Allow-Origin: {acao_value}\n"
            alarm_message += "Access-Control-Allow-Credentials: true\n\n"

            alarm_file = os.path.join(output_dir, 'cors_alarm.txt')
            with open(alarm_file, 'a') as file:
                file.write(alarm_message)

            print(f"Alarm logged for Item {item_number}")
        else:
            print(f"No CORS vulnerability detected for technique '{technique}' in Item {item_number}")
    else:
        print(f"No response received for technique '{technique}' in Item {item_number}")

def process_xml_for_cors(xml_file, business, asset_type, asset_value):
    base_output_dir = "/home/kali/Desktop/BugBountyWork/"
    output_dir = os.path.join(base_output_dir, business, asset_type, asset_value,
                              "WEBENVFINAL", "Client-Side Topics", "cors", "Techniques")
    os.makedirs(output_dir, exist_ok=True)

    tree = ET.parse(xml_file)
    root = tree.getroot()

    techniques = ["BasicACAO", "BasicWhiteList", "NullWhiteList"]

    for technique in techniques:
        technique_dir = os.path.join(output_dir, technique)
        os.makedirs(technique_dir, exist_ok=True)

        for i, item in enumerate(root.findall('.//item')):
            request_element = item.find('request')
            if request_element is not None and request_element.text:
                original_request = decode_base64(request_element.text)
                modified_request = modify_request_for_cors(original_request, technique)

                original_file = os.path.join(technique_dir, f'original_request_{i + 1}.txt')
                modified_file = os.path.join(technique_dir, f'modified_request_{i + 1}.txt')

                with open(original_file, 'w') as f:
                    f.write(original_request)
                with open(modified_file, 'w') as f:
                    f.write(modified_request)

                method, path, host, headers, cookies, body = parse_request(modified_request)
                curl_command = format_as_curl(method, path, host, headers, cookies, body)
                response = execute_curl(curl_command)

                check_cors_headers(response, technique, i + 1, output_dir)

def main(xml_file, business, asset_type, asset_value):
    process_xml_for_cors(xml_file, business, asset_type, asset_value)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CORS Vulnerability Scanner")
    parser.add_argument("xml_file", help="Input XML file to scan")
    parser.add_argument("--business", required=True, help="Business name")
    parser.add_argument("--asset_type", required=True, help="Asset type")
    parser.add_argument("--asset_value", required=True, help="Asset value")

    args = parser.parse_args()

    main(args.xml_file, args.business, args.asset_type, args.asset_value)
