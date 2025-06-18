import xml.etree.ElementTree as ET
import base64
import re
import os
import argparse

def decode_base64(encoded_text):
    return base64.b64decode(encoded_text).decode('utf-8', errors='ignore')

def check_csrf_vulnerability(xml_file, business, asset_type, asset_value):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    base_output_dir = "/home/kali/Desktop/BugBountyWork"
    output_dir = os.path.join(base_output_dir, business, asset_type, asset_value,
                              "WEBENVFINAL", "Client-Side Topics", "csrf", "Techniques", "BasicCSRF")
    os.makedirs(output_dir, exist_ok=True)
    alarm_file_path = os.path.join(output_dir, 'csrf_alarm.txt')

    with open(alarm_file_path, 'w') as alarm_file:
        for i, item in enumerate(root.findall('.//item')):
            request_element = item.find('request')
            if request_element is not None and request_element.text:
                request = decode_base64(request_element.text)

                # Check if the request is POST, PUT, or DELETE
                if re.search(r'^(POST|PUT|DELETE)', request, re.IGNORECASE | re.MULTILINE):
                    # Check if the request contains a Cookie header
                    if 'Cookie:' in request:
                        alarm_file.write(f"Potential CSRF vulnerability in Item {i + 1}:\n")

                        # Extract and write the method
                        method = re.search(r'^(POST|PUT|DELETE)', request, re.IGNORECASE | re.MULTILINE)
                        if method:
                            alarm_file.write(f"Method: {method.group()}\n")

                        # Extract and write the path
                        path = re.search(r'^(POST|PUT|DELETE)\s+(\S+)', request, re.IGNORECASE | re.MULTILINE)
                        if path:
                            alarm_file.write(f"Path: {path.group(2)}\n")

                        # Extract and write the cookie header
                        cookie = re.search(r'Cookie:.*', request, re.IGNORECASE | re.MULTILINE)
                        if cookie:
                            alarm_file.write(f"{cookie.group()}\n")

                        alarm_file.write("\n")

def main(xml_file, business, asset_type, asset_value):
    check_csrf_vulnerability(xml_file, business, asset_type, asset_value)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSRF Vulnerability Scanner")
    parser.add_argument("xml_file", help="Input XML file to scan")
    parser.add_argument("--business", required=True, help="Business name")
    parser.add_argument("--asset_type", required=True, help="Asset type")
    parser.add_argument("--asset_value", required=True, help="Asset value")

    args = parser.parse_args()

    main(args.xml_file, args.business, args.asset_type, args.asset_value)
