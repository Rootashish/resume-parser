from flask import Flask, request, jsonify
import re
import pdfminer.high_level
from werkzeug.utils import secure_filename
import os
import docx

app = Flask(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"pdf", "docx"}

# Function to check file extension
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    return pdfminer.high_level.extract_text(pdf_path)

# Function to extract text from DOCX
def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Function to extract contact details (name, email, phone)
def extract_contact_info(text):
    email_pattern = r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+"
    phone_pattern = r"\+?\d[\d -]{8,12}\d"

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)

    return {
        "name": text.split("\n")[0],  # Assume first line is the name (improve as needed)
        "emails": emails if emails else "Not found",
        "phones": phones if phones else "Not found",
    }

# Resume parser route
@app.route("/parse", methods=["POST"])
def parse_resume():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join("/tmp", filename)  # Save to temporary directory
    file.save(filepath)

    # Extract text based on file type
    if filename.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(filepath)
    elif filename.endswith(".docx"):
        extracted_text = extract_text_from_docx(filepath)
    else:
        return jsonify({"error": "Unsupported file format"}), 400

    # Extract contact details
    contact_info = extract_contact_info(extracted_text)

    return jsonify({
        "message": "Resume processed successfully",
        "name": contact_info["name"],
        "email": contact_info["emails"],
        "phone": contact_info["phones"]
    })

# Root route (for testing)
@app.route("/", methods=["GET"])
def home():
    return "Resume Parser API is running!"

if __name__ == "__main__":
    app.run(debug=True)
