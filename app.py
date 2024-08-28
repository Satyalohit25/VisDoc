import os

import gradio as gr
import PyPDF2
import pytesseract
from gradio_pdf import PDF
from langchain_community.llms import Ollama
from PIL import Image

# Set up Tesseract path (modify if necessary)
tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if not os.path.exists(tesseract_path):
    raise FileNotFoundError(
        "Tesseract not found at the specified path. Please check the path.")
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Initialize the Ollama model
try:
    ollama = Ollama(
        base_url='http://localhost:11434',
        model="mistral"
    )
except Exception as e:
    raise ConnectionError(
        "Could not connect to the Ollama model. Please ensure Ollama is running and the model is loaded correctly.")

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
    try:
        img = Image.open(image_path)
        extracted_information = pytesseract.image_to_string(img).strip()
        return extracted_information
    except Exception as e:
        return f"Error reading image: {str(e)}"

def extract_text_from_pdf(pdf_path):
    extracted_information = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                extracted_information += page.extract_text().strip() + "\n"
        return extracted_information
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

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

# Modify this function to update the global variable extracted_information
def upload_file_and_extract_text(file):
    global extracted_information  # Update the global variable directly
    file_path = file.name
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        text = extract_text_from_image(file_path)
        extracted_information = text  # Update global variable
        return text, file_path, None, gr.update(visible=True), gr.update(visible=False)
    elif file_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
        extracted_information = text  # Update global variable
        return text, None, file_path, gr.update(visible=False), gr.update(visible=True)
    else:
        extracted_information = ""  # Clear extracted information
        return "Unsupported file format. Please upload an image or PDF file.", None, None, gr.update(visible=False), gr.update(visible=False)

# Adding some debugging in the answer_query function
def answer_query(user_query):
    if not extracted_information:
        # Check if any information was extracted
        logs.append("No information available to answer the query.")
        return "No information has been extracted yet. Please upload an image, PDF, or EPUB file first."
    
    response = get_llama2_response(user_query)
    return response if response else "Error processing query. Check the logs."

# Launch Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# File & Query Answering App")

    with gr.Row():
        with gr.Column():
            gr.Markdown("## Upload File")
            file_input = gr.File(label="Upload Image or PDF", type="filepath")
            pdf_viewer = PDF(label="PDF Preview", interactive=True)
            image_viewer = gr.Image(label="Image Preview", type="filepath")

        with gr.Column():
            gr.Markdown("## Extracted Text")
            extracted_text_output = gr.Textbox(
                label="Extracted Text", lines=10, interactive=False
            )

    file_input.change(
        fn=upload_file_and_extract_text,
        inputs=file_input,
        outputs=[extracted_text_output, image_viewer, pdf_viewer, image_viewer, pdf_viewer]
    )

    gr.Markdown("## Query Processing")
    query_input = gr.Textbox(label="Enter Query", lines=2)
    query_button = gr.Button("Submit Query")
    query_output = gr.Textbox(label="Query Answer", lines=10, interactive=False)
    query_button.click(
        fn=answer_query,
        inputs=query_input,
        outputs=query_output
    )

demo.launch()
