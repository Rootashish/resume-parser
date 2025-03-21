from flask import Flask, request, jsonify, send_file
import pandas as pd
import re
import os
from PyPDF2 import PdfReader
from docx import Document

app = Flask(__name__)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        pdf = PdfReader(file)
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Function to extract text from DOCX
def extract_text_from_docx(docx_path):
    text = ""
    doc = Document(docx_path)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Function to extract name, email, and phone number
def extract_contact_details(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_pattern = r"\+?\d[\d -]{8,14}\d"

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)

    name = text.split("\n")[0]  # Assuming first line is name

    return {
        "Name": name.strip(),
        "Email": emails[0] if emails else "Not Found",
        "Phone": phones[0] if phones else "Not Found"
    }

@app.route("/")
def home():
    return "Resume Parser API is running!"

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_ext = file.filename.split(".")[-1].lower()
    temp_path = f"temp.{file_ext}"
    file.save(temp_path)

    if file_ext == "pdf":
        text = extract_text_from_pdf(temp_path)
    elif file_ext == "docx":
        text = extract_text_from_docx(temp_path)
    else:
        return jsonify({"error": "Unsupported file format. Use PDF or DOCX."}), 400

    os.remove(temp_path)  # Clean up temp file

    # Extract details
    details = extract_contact_details(text)

    # Save to Excel
    df = pd.DataFrame([details])
    excel_path = "output.xlsx"
    df.to_excel(excel_path, index=False)

    return send_file(excel_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
