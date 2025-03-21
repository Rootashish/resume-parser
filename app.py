from flask import Flask, request, jsonify, send_file
import os
import re
import pandas as pd
import PyPDF2
import docx
from io import BytesIO

app = Flask(__name__)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
    return text

# Function to extract text from DOCX
def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    text = "".join([para.text for para in doc.paragraphs])
    return text

# Function to extract contact details
def extract_contact_details(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b\d{10}\b'  # Adjust regex for different formats
    
    email = re.findall(email_pattern, text)
    phone = re.findall(phone_pattern, text)
    
    return {
        "Name": text.split("\n")[0],  # Assuming name is at the top
        "Email": email[0] if email else "Not Found",
        "Phone": phone[0] if phone else "Not Found"
    }

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    file_ext = file.filename.split(".")[-1].lower()
    
    if file_ext == "pdf":
        text = extract_text_from_pdf(file)
    elif file_ext == "docx":
        text = extract_text_from_docx(file)
    else:
        return jsonify({"error": "Unsupported file format. Use PDF or DOCX."}), 400
    
    extracted_data = extract_contact_details(text)
    df = pd.DataFrame([extracted_data])
    
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    
    return send_file(output, download_name="contact_details.xlsx", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
