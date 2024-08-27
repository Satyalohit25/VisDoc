**File & Query Answering App**
=============================

### Overview
This application allows users to upload image, PDF, or EPUB files, extracts text from these files using OCR (Optical Character Recognition) and parsing techniques, and then answers user queries based on the extracted text. The application utilizes the Ollama mistral model for generating responses and Tesseract OCR for text extraction from images.

### Features
* **File Upload**: Users can upload image (PNG, JPG, JPEG), PDF, or EPUB files.
* **Text Extraction**: Extracts text from images, PDFs, and EPUB files.
* **Query Processing**: Answers user queries based on the extracted text using the Ollama mistral model.
* **Log Viewing**: Provides a log of operations and errors for debugging and tracking purposes.

### Technologies Used
* Ollama: For generating responses based on the extracted text using the mistral model.
* Tesseract OCR: For extracting text from image files.
* Gradio: For building the user interface.
* PyPDF2: For extracting text from PDF files.
* ebooklib: For parsing EPUB files.
* Pillow: For image processing.

### Installation
1. Clone the repository:
    ```
    git clone <repositoryurl>
    cd <repositorydirectory>
    ```
    Install dependencies:
    Ensure you have Python 3.7+ installed. Create a virtual environment and install the required packages:
    ```
    python -m venv venv
    source venv/bin/activate   (On Windows use venv\Scripts\activate)
    pip install -r requirements.txt
    ```
    `requirements.txt` should include:
    ```
    gradio
    PyPDF2
    pytesseract
    ebooklib
    langchain_community
    Pillow
    ```
    Install Tesseract OCR:
    Windows: Download the installer from the official Tesseract page and follow the installation instructions. Make sure to add Tesseract to your system PATH.
    Linux: Install Tesseract using your package manager:
    ```
    sudo apt-get install tesseract-ocr
    ```
    Install Ollama and start the service:
    Follow the instructions on the Ollama website to install and run the Ollama service.

### Usage
1. Start the application:
    ```
    python app.py
    ```
    Access the application:
    Open your browser and go to http://localhost:7860 to interact with the application.

### How It Works
* **File Upload**: Users upload files which are processed to extract text.
* **Text Extraction**: Depending on the file type, the text is extracted using Tesseract OCR for images, PyPDF2 for PDFs, and ebooklib for EPUBs.
* **Query Processing**: Extracted text is fed into the Ollama mistral model to generate responses to user queries.
* **Logs**: Errors and information are logged for troubleshooting and insights.

### Error Handling
* If Tesseract OCR is not found, ensure that Tesseract is installed and its path is correctly set.
* If the Ollama model cannot be connected, check that the Ollama service is running and accessible at the specified URL.

### Contributing
If you find any issues or want to contribute to the project, please open an issue or submit a pull request on the repository's GitHub page.

### License
This project is licensed under the MIT License. See the LICENSE file for details.
