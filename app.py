import io
import os

import ebooklib
import gradio as gr
import PyPDF2
import pytesseract
from ebooklib import epub
from gradio_pdf import PDF
from langchain_community.llms import Ollama
from PIL import Image

# Set up Tesseract path (modify if necessary)
tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if not os.path.exists(tesseract_path):
    raise FileNotFoundError("Tesseract not found at the specified path. Please check the path.")
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Initialize the Ollama model
try:
    ollama = Ollama(
        base_url='http://localhost:11434',
        model="mistral"
    )
except Exception as e:
    raise ConnectionError("Could not connect to the Ollama model. Please ensure Ollama is running and the model is loaded correctly.")

# Global variables
extracted_information = ""
logs = []

# Define the system message to enforce content rules
system_message = """
You are OnlyFileReferGPT, and your primary role is to provide answers exclusively based on the information contained within the provided knowledge files. 

### Key Instructions:
1. Reference Restriction: You must only use the content from the provided documents to generate your responses. Do not incorporate any general knowledge, common facts, or information not explicitly mentioned in the documents.

2. Information Confirmation: Before answering any question, you must first verify whether the information is present within the documents. If the required information is not found in the files, respond with: 
   - "Information not found in the provided documents."

3. Exactness in Responses: Ensure that your responses are as precise as possible, directly quoting or paraphrasing the relevant sections from the files when applicable. Do not infer, assume, or generalize beyond what is stated in the documents.

4. Clarification and Transparency: If the document provides information that might be different or context-specific (e.g., boiling point of water in a specific location), include this context in your response to ensure accuracy.

5. No Guessing: If a question cannot be answered based on the documents alone, do not guess or provide speculative answers. Instead, acknowledge the limitation by stating:
   - "The answer is not available in the provided documents."

### Examples of Appropriate Behavior:
- User Question: "Who is the President of the United States?"
  - Appropriate Response: "Information not found in the provided documents."
  
- User Question: "At what temperature does water boil according to the provided documents?"
  - Appropriate Response: "According to the document, water boils at 96°C in [specific location]."

By following these instructions, you will ensure that all outputs are strictly aligned with the information within the provided documents, avoiding any use of external or general knowledge.
"""

# Functions to extract text from files
def extract_text_from_image(image_path):
    global extracted_information, logs
    try:
        img = Image.open(image_path)
        extracted_information = pytesseract.image_to_string(img).strip()
        logs.append(f"Extracted Text: {extracted_information}")
        return extracted_information
    except Exception as e:
        error_message = f"Error reading image: {str(e)}"
        logs.append(error_message)
        return error_message

def extract_text_from_pdf(pdf_path):
    global extracted_information, logs
    extracted_information = ""  # Reset before extraction
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                extracted_information += page.extract_text().strip() + "\n"
        logs.append(f"Extracted Text from PDF: {extracted_information}")
        return extracted_information
    except Exception as e:
        error_message = f"Error reading PDF: {str(e)}"
        logs.append(error_message)
        return error_message

def extract_text_from_epub(epub_path):
    global extracted_information, logs
    extracted_information = ""  # Reset before extraction
    try:
        book = epub.read_epub(epub_path)
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                extracted_information += item.get_body_content().decode('utf-8').strip() + "\n"
        logs.append(f"Extracted Text from EPUB: {extracted_information}")
        return extracted_information
    except Exception as e:
        error_message = f"Error reading EPUB: {str(e)}"
        logs.append(error_message)
        return error_message

def get_llama2_response(user_query):
    global extracted_information, logs
    if extracted_information:
        prompt = f"Context: {extracted_information}\n\nQuestion: {user_query}\nAnswer:"
        logs.append(f"Prompt fed to model: {prompt}")
        try:
            response = ollama.invoke(prompt)  # Using invoke method
            if isinstance(response, dict):
                if 'output' in response:
                    answer = response['output']
                    logs.append(f"Model response: {answer}")
                    return answer
                else:
                    error_message = "Response dictionary does not contain 'output'."
                    logs.append(error_message)
                    return error_message
            elif isinstance(response, str):
                logs.append(f"Model response (string): {response}")
                return response
            else:
                error_message = "Unexpected response format from model. Response is not a dictionary or string."
                logs.append(error_message)
                return error_message
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            logs.append(error_message)
            return error_message
    else:
        no_info_message = "No information has been extracted yet. Please upload an image, PDF, or EPUB file first."
        logs.append(no_info_message)
        return no_info_message

def upload_file_and_extract_text(file):
    file_path = file.name
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        return extract_text_from_image(file_path), file_path  # Return image path for preview
    elif file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path), file_path  # Return PDF path for preview
    elif file_path.lower().endswith('.epub'):
        return extract_text_from_epub(file_path), None  # EPUB preview is not supported in Gradio directly
    else:
        return "Unsupported file format. Please upload an image, PDF, or EPUB file.", None

def answer_query(user_query):
    response = get_llama2_response(user_query)
    return response if response else "Error processing query. Check the logs."

def get_logs():
    return "\n".join(logs)

# Creating Gradio Interface with a dark mode theme and a streamlined layout
with gr.Blocks(
    css="""
    .gradio-container {padding: 20px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #f1f1f1;}
    .header {text-align: center; margin-bottom: 20px; font-size: 28px; font-weight: bold; color: #00aaff;}
    .section-title {font-size: 18px; font-weight: bold; color: #f1f1f1; margin-bottom: 10px;}
    .gr-button {background-color: #00aaff; color: white; border-radius: 4px; margin-top: 10px; margin-bottom: 10px; padding: 10px;}
    .gr-button:hover {background-color: #0088cc;}
    .gr-textbox {border: 1px solid #444; border-radius: 4px; background-color: #333; color: #f1f1f1; margin-bottom: 10px;}
    .card {border-radius: 8px; background-color: #3a3a3a; padding: 20px; margin-bottom: 20px; color: #f1f1f1;}
    .log-output {background-color: #3a3a3a; border-radius: 8px; color: #f1f1f1;}
""") as demo:

    gr.Markdown(
        """
        <div class="header">File & Query Answering App</div>
        """
    )

    # Step 1: Upload File and Automatically Extract Text
    with gr.Row():
        with gr.Column():
            gr.Markdown("<div class='section-title'>Upload File</div>")
            file_input = gr.File(label="Upload Image, PDF, or EPUB", type="filepath")
            pdf_viewer = PDF(label="PDF Preview", interactive=True)  # PDF preview
        with gr.Column():
            gr.Markdown("<div class='section-title'>Extracted Text</div>")
            extracted_text_output = gr.Textbox(
                label="Extracted Text", lines=10, interactive=False)

    # Connect file input to preview and text extraction
    file_input.change(
        fn=upload_file_and_extract_text,
        inputs=file_input,
        outputs=[extracted_text_output, pdf_viewer]
    )

    # Query processing
    gr.Markdown("<div class='section-title'>Query Processing</div>")
    query_input = gr.Textbox(label="Enter Query", lines=2)
    query_button = gr.Button("Submit Query", elem_id="submit_query")
    query_output = gr.Textbox(label="Query Answer", lines=10, interactive=False)
    query_button.click(
        fn=answer_query,
        inputs=query_input,
        outputs=query_output
    )

    # Logs display
    gr.Markdown("<div class='section-title'>Logs</div>")
    logs_output = gr.Textbox(value=get_logs, label="Logs", lines=10, interactive=False, elem_id="logs_output")

demo.launch()
