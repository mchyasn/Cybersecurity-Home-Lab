import os
import base64
import xml.etree.ElementTree as ET


def load_items_from_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return root.findall(".//item")


def decode_base64(encoded_text):
    return base64.b64decode(encoded_text).decode('utf-8', errors='ignore')


def check_for_http_downgrade(response_text):
    return "HTTP/1" in response_text or "HTTP/1.1" in response_text


def process_items(xml_file, output_dir):
    items = load_items_from_xml(xml_file)

    # Create main directory and subfolders
    main_dir = os.path.join(output_dir, "HTTPSmuggling")
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

                        # Save the full response
                        response_file = os.path.join(downgrade_dir, f"response_{i + 1}.txt")
                        with open(response_file, 'w') as f:
                            f.write(decoded_response)
                except Exception as e:
                    print(f"Error processing item {i + 1}: {str(e)}")


# Usage
process_items('burp_export.xml', 'HTTPSmugglingGuy')