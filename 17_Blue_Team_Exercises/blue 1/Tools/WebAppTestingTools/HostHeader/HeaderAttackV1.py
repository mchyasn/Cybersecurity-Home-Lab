import os
import base64
import xml.etree.ElementTree as ET
import argparse

def load_requests_from_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return root.findall(".//request")

def decode_base64(encoded_text):
    return base64.b64decode(encoded_text).decode('utf-8', errors='ignore')


def modify_request(request_text, technique):
    lines = request_text.split('\n')
    method_line = lines[0]
    headers = lines[1:-2]
    body = lines[-1]

    if technique == "arbitrary_host":
        for i, line in enumerate(headers):
            if line.startswith("Host:"):
                headers[i] = "Host: localhost:8000"
                break

    elif technique == "ambiguous_request":
        headers.append("Host: localhost:8000")

    elif technique == "duplicate_host":
        for i, line in enumerate(headers):
            if line.startswith("Host:"):
                headers.insert(i + 1, line)
                break

    elif technique == "absolute_url":
        parts = method_line.split()
        if len(parts) >= 2:
            host = next((h.split(": ")[1] for h in headers if h.startswith("Host:")), "")
            parts[1] = f"http://{host}{parts[1]}"
            method_line = " ".join(parts)

    elif technique == "line_wrapping":
        for i, line in enumerate(headers):
            if line.startswith("Host:"):
                host_parts = line.split(": ")
                if len(host_parts) > 1:
                    headers[i] = f"{host_parts[0]}: {host_parts[1][:-4]}"
                    headers.insert(i + 1, f" {host_parts[1][-4:]}")
                break

    elif technique == "host_override":
        override_headers = [
            "X-Forwarded-Host: localhost:8000",
            "X-Forwarded-Server: localhost:8000",
            "X-Host: localhost:8000",
            "X-HTTP-Host-Override: localhost:8000",
            "Forwarded: host=localhost:8000"
        ]
        headers.extend(override_headers)

    return '\n'.join([method_line] + headers + ['', body])


def apply_techniques(xml_file, business, asset_type, asset_value):
    requests = load_requests_from_xml(xml_file)
    techniques = ["arbitrary_host", "ambiguous_request", "duplicate_host", "absolute_url", "line_wrapping", "host_override"]

    base_output_dir = "/home/kali/Desktop/BugBountyWork"
    main_dir = os.path.join(base_output_dir, business, asset_type, asset_value,
                            "WEBENVFINAL", "Advanced Topics", "host-header", "Techniques")

    for technique in techniques:
        technique_dir = os.path.join(main_dir, technique)
        os.makedirs(technique_dir, exist_ok=True)

        for i, request in enumerate(requests):
            original_request = decode_base64(request.text)
            modified_request = modify_request(original_request, technique)

            # Save original request
            original_file = os.path.join(technique_dir, f'original_request_{i + 1}.txt')
            with open(original_file, 'w') as f:
                f.write(original_request)

            # Save modified request
            modified_file = os.path.join(technique_dir, f'modified_request_{i + 1}.txt')
            with open(modified_file, 'w') as f:
                f.write(modified_request)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Header Attack Scanner")
    parser.add_argument("xml_file", help="Input XML file to scan")
    parser.add_argument("--business", required=True, help="Business name")
    parser.add_argument("--asset_type", required=True, help="Asset type")
    parser.add_argument("--asset_value", required=True, help="Asset value")

    args = parser.parse_args()

    apply_techniques(args.xml_file, args.business, args.asset_type, args.asset_value)
