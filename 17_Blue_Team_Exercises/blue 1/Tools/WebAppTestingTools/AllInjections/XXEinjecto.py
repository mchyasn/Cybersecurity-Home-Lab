import xml.etree.ElementTree as ET
import base64
import os
import re
import random
import argparse


def decode_base64(encoded_text):
    return base64.b64decode(encoded_text).decode('utf-8', errors='ignore')


def load_wordlist(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]


def modify_request_for_xxe(request, payload):
    lines = request.split('\n')
    modified = []
    body_start = lines.index('')
    for i, line in enumerate(lines):
        if i < body_start:
            modified.append(line)
        elif i == body_start:
            modified.append(line)
            modified.append(payload)
        else:
            modified.append(line)
    return '\n'.join(modified)


def scan_for_xxe_injection(xml_file, business, asset_type, asset_value):
    base_output_dir = "/home/kali/Desktop/BugBountyKaliFinal"
    wordlist_file = "/usr/share/wfuzz/wordlist/Injections/XML.txt"
    injection_type = "XXEInjection"

    output_dir = os.path.join(base_output_dir, business, asset_type, asset_value,
                              "Server-Side Topics", "xxe-injection", "Techniques", "basic-xxe-injection")
    os.makedirs(output_dir, exist_ok=True)
    alarm_file = os.path.join(output_dir, 'alarm.txt')

    tree = ET.parse(xml_file)
    root = tree.getroot()
    wordlist = load_wordlist(wordlist_file)

    with open(alarm_file, 'w') as alarm:
        for i, item in enumerate(root.findall('.//item')):
            request_element = item.find('request')
            if request_element is not None and request_element.text:
                request = decode_base64(request_element.text)
                first_line = request.split('\n')[0]

                if 'POST' in first_line and 'Content-Type: application/xml' in request:
                    original_file = os.path.join(output_dir, f'original_request_{i + 1}.txt')
                    with open(original_file, 'w') as f:
                        f.write(request)

                    for j in range(3):
                        payload = random.choice(wordlist)
                        modified_request = modify_request_for_xxe(request, payload)
                        modified_file = os.path.join(output_dir, f'modified_request_{i + 1}_{j + 1}.txt')
                        with open(modified_file, 'w') as f:
                            f.write(modified_request)

                    alarm.write(f"Potential {injection_type} vulnerability in Item {i + 1}:\n")
                    alarm.write(f"Method: {first_line}\n")
                    alarm.write(f"Original file: {original_file}\n")
                    alarm.write(f"Modified files: {output_dir}/modified_request_{i + 1}_*.txt\n\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='XXE Injection Scanner')
    parser.add_argument('xml_file', help='Input XML file to scan')
    parser.add_argument('--business', required=True, help='Business name')
    parser.add_argument('--asset_type', required=True, help='Asset type')
    parser.add_argument('--asset_value', required=True, help='Asset value')

    args = parser.parse_args()

    scan_for_xxe_injection(args.xml_file, args.business, args.asset_type, args.asset_value)
