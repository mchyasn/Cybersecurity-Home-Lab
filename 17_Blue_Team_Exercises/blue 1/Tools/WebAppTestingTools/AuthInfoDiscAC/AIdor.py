import ollama
import xml.etree.ElementTree as ET
import os

def process_xml_urls_with_ollama(xml_file, output_dir, model='deepseek-llm:latest'):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    system_message = 'Give me examples of code that would be used to test each of these issues, I think the last AI was wrong'

    os.makedirs(output_dir, exist_ok=True)

    for i, item in enumerate(root.findall('.//item')):
        url_element = item.find('url')

        if url_element is not None and url_element.text:
            url = url_element.text.strip()

            input_content = f"URL: {url}"

            stream = ollama.chat(
                model=model,
                messages=[
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': input_content}
                ],
                options={'temperature': 0.01},
                stream=True,
            )

            output_file = os.path.join(output_dir, f'ollama_url_output_{i+1}.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Processing URL: {url}\n\n")
                for chunk in stream:
                    content = chunk['message']['content']
                    print(content, end='', flush=True)
                    f.write(content)

            print(f"\nProcessed item {i+1}, output saved to {output_file}")

def main(xml_file, output_dir):
    process_xml_urls_with_ollama(xml_file, output_dir)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python ollama_xml_url_processor.py <xml_file> <output_directory>")
        sys.exit(1)

    xml_file = sys.argv[1]
    output_dir = sys.argv[2]
    main(xml_file, output_dir)