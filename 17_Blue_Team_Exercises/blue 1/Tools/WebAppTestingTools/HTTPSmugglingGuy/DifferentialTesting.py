import os
import base64
import xml.etree.ElementTree as ET
import subprocess


def load_items_from_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return root.findall(".//item")


def decode_base64(encoded_text):
    return base64.b64decode(encoded_text).decode('utf-8', errors='ignore')


def modify_request_clte(request):
    lines = request.split('\n')
    body_start = lines.index('') + 1
    lines.insert(body_start, 'GET /404 HTTP/1.1')
    lines.insert(body_start + 1, 'Foo: x')
    return '\n'.join(lines)


def modify_request_tecl(request):
    lines = request.split('\n')
    host = next(line for line in lines if line.startswith('Host:'))
    content_type = next(line for line in lines if line.startswith('Content-Type:'))
    body_start = lines.index('') + 1

    modified = lines[:body_start]
    modified.extend([
        'GET /404 HTTP/1.1',
        host,
        content_type,
        'Content-Length: 50',
        'x=',
        '',
        '0'
    ])
    return '\n'.join(modified)


def send_curl_request(request, url):
    curl_command = ['curl', '-X', 'POST', url, '-H', request, '-s', '-o', '/dev/null', '-w', '%{http_code}']
    result = subprocess.run(curl_command, capture_output=True, text=True)
    return result.stdout.strip()


def differential_testing(xml_file, output_dir, url):
    items = load_items_from_xml(xml_file)

    main_dir = os.path.join(output_dir, "HTTPSmuggling", "Differential")
    os.makedirs(main_dir, exist_ok=True)

    alarm_file = os.path.join(main_dir, "alarm.txt")

    with open(alarm_file, 'w') as alarm:
        for i, item in enumerate(items):
            request_element = item.find("request")

            if request_element is not None and request_element.text:
                try:
                    decoded_request = decode_base64(request_element.text)

                    # Test for CL.TE
                    modified_request_clte = modify_request_clte(decoded_request)
                    modified_response_clte = send_curl_request(modified_request_clte, url)
                    original_response_clte = send_curl_request(decoded_request, url)

                    if modified_response_clte == '404':
                        alarm.write(f"Potential CL.TE vulnerability detected in item {i + 1}\n")

                    # Test for TE.CL
                    modified_request_tecl = modify_request_tecl(decoded_request)
                    modified_response_tecl = send_curl_request(modified_request_tecl, url)

                    original_responses_tecl = [send_curl_request(decoded_request, url) for _ in range(4)]

                    if all(response == '404' for response in original_responses_tecl):
                        alarm.write(f"Potential TE.CL vulnerability detected in item {i + 1}\n")

                    alarm.write(f"Item {i + 1} results:\n")
                    alarm.write(f"CL.TE modified response: {modified_response_clte}\n")
                    alarm.write(f"TE.CL modified response: {modified_response_tecl}\n")
                    alarm.write(f"Original responses: {original_responses_tecl}\n\n")

                except Exception as e:
                    print(f"Error processing item {i + 1}: {str(e)}")


# Usage
differential_testing('TESTXML2CURL.xml', 'HTTPSmugglingGuy', 'http://example.com')