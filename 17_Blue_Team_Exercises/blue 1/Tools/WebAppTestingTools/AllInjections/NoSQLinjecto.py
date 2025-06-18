import xml.etree.ElementTree as ET
import base64
import os
import re
import random
import argparse
import json
import logging
from datetime import datetime

print("Script started")

def ensure_dir(directory):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            logging.info(f"Created directory: {directory}")
        except Exception as e:
            logging.error(f"Failed to create directory {directory}: {str(e)}")
    else:
        logging.info(f"Directory already exists: {directory}")

def decode_base64(encoded_text):
    return base64.b64decode(encoded_text).decode('utf-8', errors='ignore')

def load_wordlist(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def write_to_file(filename, content):
    try:
        with open(filename, 'w') as f:
            f.write(content)
        logging.info(f"Successfully wrote to file: {filename}")
    except Exception as e:
        logging.error(f"Failed to write to file {filename}: {str(e)}")

def setup_logging(output_dir):
    print(f"Setting up logging in directory: {output_dir}")
    log_file = os.path.join(output_dir, f'scan_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    print(f"Log file path: {log_file}")
    try:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        print(f"Logging initialized. Log file: {log_file}")
        logging.info("This is a test log message")
    except Exception as e:
        print(f"Failed to set up logging to file {log_file}: {str(e)}")
        print("Falling back to console logging only")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )

def modify_request_for_nosql_injection(request, payload):
    lines = request.split('\n')
    modified = []
    body_start = lines.index('')
    for i, line in enumerate(lines):
        if i < body_start:
            modified.append(line)
        elif i == body_start:
            modified.append(line)
        else:
            try:
                body = json.loads(line)
                for key in body:
                    if isinstance(body[key], str):
                        body[key] = f"{body[key]}{payload}"
                modified.append(json.dumps(body))
            except json.JSONDecodeError:
                modified.append(line)
    return '\n'.join(modified)

def scan_for_nosql_injection(xml_file, business, asset_type, asset_value):
    base_output_dir = "/home/kali/Desktop/BugBountyWork"
    wordlist_file = "/usr/share/wfuzz/wordlist/vulns/sql_inj.txt"
    injection_type = "NoSQLInjection"
    output_dir = os.path.join(base_output_dir, business, asset_type, asset_value,
                              "WEBENVFINAL", "Server-Side-Topics", "nosql-injection", "Techniques", "basic-nosql-injection")
    print(f"Debug: output_dir = {output_dir}")
    ensure_dir(output_dir)
    setup_logging(output_dir)
    print("Logging setup complete")

    logging.info(f"Starting scan for {injection_type} on {xml_file}")
    logging.info(f"Output directory: {output_dir}")
    
    alarm_file = os.path.join(output_dir, 'alarm.txt')
    print(f"Debug: Attempting to write to alarm file: {alarm_file}")
    
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    logging.info(f"Loading wordlist from {wordlist_file}")
    wordlist = load_wordlist(wordlist_file)
    logging.info(f"Loaded {len(wordlist)} payloads from wordlist")
    
    items_processed = 0
    potential_vulnerabilities = 0
    
    with open(alarm_file, 'w') as alarm:
        for i, item in enumerate(root.findall('.//item')):
            request_element = item.find('request')
            if request_element is not None and request_element.text:
                items_processed += 1
                request = decode_base64(request_element.text)
                first_line = request.split('\n')[0]
                if 'POST' in first_line and 'Content-Type: application/json' in request:
                    logging.info(f"Processing item {i + 1}: {first_line}")
                    original_file = os.path.join(output_dir, f'original_request_{i + 1}.txt')
                    write_to_file(original_file, request)
                    for j in range(3):
                        payload = random.choice(wordlist)
                        modified_request = modify_request_for_nosql_injection(request, payload)
                        modified_file = os.path.join(output_dir, f'modified_request_{i + 1}_{j + 1}.txt')
                        write_to_file(modified_file, modified_request)
                    potential_vulnerabilities += 1
                    alarm.write(f"Potential {injection_type} vulnerability in Item {i + 1}:\n")
                    alarm.write(f"Method: {first_line}\n")
                    alarm.write(f"Original file: {original_file}\n")
                    alarm.write(f"Modified files: {output_dir}/modified_request_{i + 1}_*.txt\n\n")
                    logging.info(f"Potential vulnerability found in item {i + 1}")
                else:
                    logging.info(f"Skipping item {i + 1}: Not a POST request with JSON content")
            else:
                logging.warning(f"Skipping item {i + 1}: No request element or empty request")
    
    logging.info(f"Scan completed. Processed {items_processed} items.")
    logging.info(f"Found {potential_vulnerabilities} potential vulnerabilities.")
    logging.info(f"Results written to {alarm_file}")

def verify_output_files(output_dir):
    files = os.listdir(output_dir)
    logging.info(f"Files in output directory {output_dir}:")
    for file in files:
        logging.info(f"- {file}")

print("Script completed")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NoSQL Injection Scanner')
    parser.add_argument('xml_file', help='Input XML file to scan')
    parser.add_argument('--business', required=True, help='Business name')
    parser.add_argument('--asset_type', required=True, help='Asset type')
    parser.add_argument('--asset_value', required=True, help='Asset value')
    args = parser.parse_args()
    
    try:
        scan_for_nosql_injection(args.xml_file, args.business, args.asset_type, args.asset_value)
    except Exception as e:
        logging.exception(f"An error occurred during the scan: {str(e)}")
