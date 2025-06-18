import ollama
import xml.etree.ElementTree as ET
import base64
import os

def decode_base64(encoded_text):
    return base64.b64decode(encoded_text).decode('utf-8', errors='ignore')

def process_xml_with_ollama(xml_file, output_dir, model='deepseek-llm:latest'):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    system_message = 'Give me examples of code that would be used to test each of these issues, I think the last AI was wrong'

    os.makedirs(output_dir, exist_ok=True)

    for i, item in enumerate(root.findall('.//item')):
        request_element = item.find('request')
        response_element = item.find('response')

        if request_element is not None and request_element.text and response_element is not None and response_element.text:
            decoded_request = decode_base64(request_element.text)
            decoded_response = decode_base64(response_element.text)

            input_content = f"Request:\n{decoded_request}\n\nResponse:\n{decoded_response}"

            stream = ollama.chat(
                model=model,
                messages=[
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': input_content}
                ],
                options={'temperature': 0.01},
                stream=True,
            )

            output_file = os.path.join(output_dir, f'ollama_output_{i+1}.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                for chunk in stream:
                    content = chunk['message']['content']
                    print(content, end='', flush=True)
                    f.write(content)

            print(f"\nProcessed item {i+1}, output saved to {output_file}")

def main(xml_file, output_dir):
    process_xml_with_ollama(xml_file, output_dir)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python ollama_xml_processor.py <xml_file> <output_directory>")
        sys.exit(1)

    xml_file = sys.argv[1]
    output_dir = sys.argv[2]
    main(xml_file, output_dir)