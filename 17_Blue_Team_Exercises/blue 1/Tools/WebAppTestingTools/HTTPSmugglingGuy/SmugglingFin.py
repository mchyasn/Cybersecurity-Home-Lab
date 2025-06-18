import os
import base64
import xml.etree.ElementTree as ET
import argparse

def load_items_from_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return root.findall(".//item")

def decode_base64(encoded_text):
    return base64.b64decode(encoded_text).decode('utf-8', errors='ignore')

def check_for_http_downgrade(response_text):
    return "HTTP/1" in response_text or "HTTP/1.1" in response_text

def process_items(xml_file, business, asset_type, asset_value):
    items = load_items_from_xml(xml_file)

    base_output_dir = "/home/kali/Desktop/BugBountyWork/"
    main_dir = os.path.join(base_output_dir, business, asset_type, asset_value,
                            "WEBENVFINAL", "Advanced Topics", "host-header", "Techniques", "Smuggling")
    os.makedirs(main_dir, exist_ok=True)

    downgrade_dir = os.path.join(main_dir, "HTTPDowngrade")
    os.makedirs(downgrade_dir, exist_ok=True)

    for subfolder in ["CLTE", "TECL", "TETE"]:
        os.makedirs(os.path.join(main_dir, subfolder), exist_ok=True)

    alarm_file = os.path.join(downgrade_dir, "alarm.txt")

    with open(alarm_file, 'w') as alarm:
        for i, item in enumerate(items):
            response_element = item.find("response")
            if response_element is not None and response_element.text:
                try:
                    decoded_response = decode_base64(response_element.text)
                    if check_for_http_downgrade(decoded_response):
                        alarm.write(f"HTTP/1 or HTTP/1.1 found in response of item {i + 1}\n")

                        response_file = os.path.join(downgrade_dir, f"response_{i + 1}.txt")
                        with open(response_file, 'w') as f:
                            f.write(decoded_response)
                except Exception as e:
                    print(f"Error processing item {i + 1}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTTP Smuggling Start Scanner")
    parser.add_argument("xml_file", help="Input XML file to scan")
    parser.add_argument("--business", required=True, help="Business name")
    parser.add_argument("--asset_type", required=True, help="Asset type")
    parser.add_argument("--asset_value", required=True, help="Asset value")

    args = parser.parse_args()

    process_items(args.xml_file, args.business, args.asset_type, args.asset_value)
