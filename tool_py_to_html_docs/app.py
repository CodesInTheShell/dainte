"""
Usage:

## Simple run, it will skip by default the folders .venv venv env .env
python app.py GeminiapiKey '/path to your folder with python codes/' '/path output folder of html documentation/' 

## Run with --skip-dirs for additional folders to skip creating documentation
python app.py GeminiapiKey '/path to your folder with python codes/' '/path output folder of html documentation/' --skip-dirs other_dir some_dir

"""

import os
import sys
import argparse
import google.generativeai as genai

SYSTEM_INSTRUCTION = """You are an assistant that generates a code documentation. Respond with the html formatted documentation.
"""

def read_code(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def generate_documentation(gemini_api_key, code, language='python'):
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_INSTRUCTION,
    )

    prompt = f"Generate HTML documentation for the following {language} code:\n\n{code}. It should contain overview on the code then classes and methods has each documentation."
    response = model.generate_content(prompt)
    return response.text

def save_html(html_content, output_dir, file_name):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, file_name)
    with open(file_path, 'w') as file:
        file.write(html_content)
    return file_path

def create_index_html(links, output_dir):
    index_path = os.path.join(output_dir, 'index.html')
    with open(index_path, 'w') as index_file:
        index_file.write('<html><body><h1>Documentation Index</h1><ul>')
        for link in links:
            index_file.write(f'<li><a href="{link}">{os.path.basename(link)}</a></li>')
        index_file.write('</ul></body></html>')
    print(f"Index page generated at {index_path}")

def main(gemini_api_key, input_dir, output_dir, skip_dirs):
    all_links = []
    for root, dirs, files in os.walk(input_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]  # Skip specified directories
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                code = read_code(file_path)
                documentation = generate_documentation(gemini_api_key, code)
                
                relative_path = os.path.relpath(root, input_dir)
                output_file_dir = os.path.join(output_dir, relative_path)
                output_file_name = f"{os.path.splitext(file)[0]}.html"
                
                full_path = save_html(documentation, output_file_dir, output_file_name)
                relative_html_path = os.path.relpath(full_path, output_dir)
                all_links.append(relative_html_path)
                print(f"Documentation generated for {file_path} and saved to {full_path}")

    create_index_html(all_links, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate HTML documentation for Python files.")
    parser.add_argument('gemini_api_key', type=str, help='The Gemini api key.')
    parser.add_argument('input_directory', type=str, help='The directory containing Python files to document.')
    parser.add_argument('output_directory', type=str, help='The directory to save generated HTML documentation.')
    parser.add_argument('--skip-dirs', type=str, nargs='*', default=[],
                        help='A list of additional directories to skip during documentation generation.')

    args = parser.parse_args()

    default_skip_dirs = ['.env', 'env', 'venv', '.venv']
    skip_dirs = default_skip_dirs + args.skip_dirs

    main(args.gemini_api_key ,args.input_directory, args.output_directory, skip_dirs)