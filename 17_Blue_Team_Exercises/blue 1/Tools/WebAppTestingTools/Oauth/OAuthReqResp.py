import xml.etree.ElementTree as ET
import base64
import re
import argparse
import os

# Hardcoded path for oauth_words_file
OAUTH_WORDS_FILE = "/home/kali/Desktop/BugBountyKaliFinal/Tools/WebAppTestingPythonFiles/Oauth/OauthReqResp.txt"

def decode_base64(encoded_string):
    try:
        return base64.b64decode(encoded_string).decode('utf-8')
    except:
        return ""

def scan_for_oauth_words(text, oauth_words):
    found_words = []
    for word in oauth_words:
        if re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE):
            found_words.append(word)
    return found_words

def process_xml_file(xml_file, oauth_words, output_dir):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    alarm_file = os.path.join(output_dir, 'Alarm_OAuth_Words.txt')
    with open(alarm_file, 'w') as af:
        for i, item in enumerate(root.findall('.//item'), 1):
            request = item.find('request')
            response = item.find('response')
            if request is not None and response is not None:
                decoded_request = decode_base64(request.text)
                decoded_response = decode_base64(response.text)
                request_words = scan_for_oauth_words(decoded_request, oauth_words)
                response_words = scan_for_oauth_words(decoded_response, oauth_words)
                if request_words or response_words:
                    af.write(f"Potential OAuth usage found in item #{i} of {xml_file}:\n")
                    if request_words:
                        af.write(f"  Request: {', '.join(request_words)}\n")
                    if response_words:
                        af.write(f"  Response: {', '.join(response_words)}\n")
                    af.write("\n")

def main(xml_file, business, asset_type, asset_value):
    with open(OAUTH_WORDS_FILE, 'r') as f:
        oauth_words = [line.strip() for line in f]

    base_output_dir = "/home/kali/Desktop/BugBountyWork"
    output_dir = os.path.join(base_output_dir, business, asset_type, asset_value,
                              "WEBENVFINAL", "Advanced Topics", "oauth", "Techniques", "basic-oauth")
    os.makedirs(output_dir, exist_ok=True)
    
    process_xml_file(xml_file, oauth_words, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OAuth Word Scanner")
    parser.add_argument("xml_file", help="Input XML file to scan")
    parser.add_argument("--business", required=True, help="Business name")
    parser.add_argument("--asset_type", required=True, help="Asset type")
    parser.add_argument("--asset_value", required=True, help="Asset value")
    args = parser.parse_args()

    main(args.xml_file, args.business, args.asset_type, args.asset_value)
