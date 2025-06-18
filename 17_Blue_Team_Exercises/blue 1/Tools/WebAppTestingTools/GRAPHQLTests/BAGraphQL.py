import xml.etree.ElementTree as ET
import base64
import re
import os
import argparse

# Hardcoded path for identifiers file
IDENTIFIERS_FILE = "/home/kali/Desktop/BugBountyKaliFinal/Tools/WebAppTestingPythonFiles/GRAPHQLTests/graphql_identifiers.txt"

def read_identifiers(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def decode_base64(encoded_string):
    try:
        return base64.b64decode(encoded_string).decode('utf-8', errors='ignore')
    except:
        return ""

def search_identifiers(text, identifiers):
    found = []
    for identifier in identifiers:
        if re.search(re.escape(identifier), text, re.IGNORECASE):
            found.append(identifier)
    return found

def process_burp_xml(xml_file, business, asset_type, asset_value):
    identifiers = read_identifiers(IDENTIFIERS_FILE)
    base_output_dir = "/home/kali/Desktop/BugBountyWork"
    output_dir = os.path.join(base_output_dir, business, asset_type, asset_value,
                              "WEBENVFINAL", "Advanced Topics", "GraphQL", "Techniques")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "GraphQL_Alarm_Burp.txt")

    tree = ET.parse(xml_file)
    root = tree.getroot()

    with open(output_file, 'w') as alarm_file:
        for index, item in enumerate(root.findall('.//item'), start=1):
            request = decode_base64(item.find('request').text)
            response = decode_base64(item.find('response').text)
            request_findings = search_identifiers(request, identifiers)
            response_findings = search_identifiers(response, identifiers)

            if request_findings or response_findings:
                alarm_message = f"Item {index}:\n"
                if request_findings:
                    alarm_message += f"  Request identifiers: {', '.join(request_findings)}\n"
                if response_findings:
                    alarm_message += f"  Response identifiers: {', '.join(response_findings)}\n"
                alarm_message += "\n"
                alarm_file.write(alarm_message)
                print(alarm_message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Burp Analyzer for GraphQL")
    parser.add_argument("xml_file", help="Input Burp XML file to analyze")
    parser.add_argument("--business", required=True, help="Business name")
    parser.add_argument("--asset_type", required=True, help="Asset type")
    parser.add_argument("--asset_value", required=True, help="Asset value")
    args = parser.parse_args()

    process_burp_xml(args.xml_file, args.business, args.asset_type, args.asset_value)
