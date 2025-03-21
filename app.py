from flask import Flask, request, jsonify
import pdfminer.high_level
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Resume Parser API is running!"

@app.route("/parse-resume", methods=["POST"])
def parse_resume():
    # Check if a file is uploaded
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    
    # Ensure the file is not empty
    if file.filename == "":
        return jsonify({"error": "Empty file"}), 400

    try:
        # Read and extract text from the PDF
        text = pdfminer.high_level.extract_text(file)
        return jsonify({"text": text})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Get PORT for deployment
    app.run(host="0.0.0.0", port=port, debug=True)
