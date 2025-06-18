import xml.etree.ElementTree as ET
import base64
import os
import re
import random


def decode_base64(encoded_text):
    return base64.b64decode(encoded_text).decode('utf-8', errors='ignore')


def load_wordlist(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]


def modify_request(request, payload):
    lines = request.split('\n')
    modified = []
    for line in lines:
        if line.startswith('Host:'):
            url_part = line.split(':', 1)[1].strip()
            modified_url = re.sub(r'=.*', '=' + payload, url_part)
            modified.append(f"Host: {modified_url}")
        else:
            modified.append(line)
    return '\n'.join(modified)


def scan_for_injection(xml_file, output_dir, injection_type, wordlist_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    injection_dir = os.path.join(output_dir, injection_type)
    os.makedirs(injection_dir, exist_ok=True)
    alarm_file = os.path.join(injection_dir, 'alarm.txt')

    wordlist = load_wordlist(wordlist_file)

    with open(alarm_file, 'w') as alarm:
        for i, item in enumerate(root.findall('.//item')):
            request_element = item.find('request')
            if request_element is not None and request_element.text:
                request = decode_base64(request_element.text)
                first_line = request.split('\n')[0]

                if any(method in first_line for method in ['GET', 'POST', 'PUT', 'DELETE']):
                    original_file = os.path.join(injection_dir, f'original_request_{i + 1}.txt')
                    with open(original_file, 'w') as f:
                        f.write(request)

                    for j in range(3):
                        payload = random.choice(wordlist)
                        modified_request = modify_request(request, payload)
                        modified_file = os.path.join(injection_dir, f'modified_request_{i + 1}_{j + 1}.txt')
                        with open(modified_file, 'w') as f:
                            f.write(modified_request)

                    alarm.write(f"Potential {injection_type} Injection vulnerability in Item {i + 1}:\n")
                    alarm.write(f"Method: {first_line}\n")
                    alarm.write(f"Original file: {original_file}\n")
                    alarm.write(f"Modified files: {injection_dir}/modified_request_{i + 1}_*.txt\n\n")


def main(xml_file, output_dir, injection_type, wordlist_file):
    scan_for_injection(xml_file, output_dir, injection_type, wordlist_file)


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 5:
        print("Usage: python injection_scanner.py <xml_file> <output_directory> <injection_type> <wordlist_file>")
        sys.exit(1)

    xml_file = sys.argv[1]
    output_dir = sys.argv[2]
    injection_type = sys.argv[3]
    wordlist_file = sys.argv[4]
    main(xml_file, output_dir, injection_type, wordlist_file)