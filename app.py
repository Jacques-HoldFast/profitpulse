import pdfplumber
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def is_scanned_pdf(pdf_path):
    """Checks if a PDF is scanned (contains no selectable text)."""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            if page.get_text():  # If text is found, it's not scanned
                return False
    return True  # No text found, likely a scanned PDF

def extract_text_from_scanned_pdf(pdf_path):
    """Extracts text from a scanned PDF using OCR."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            img = page.get_pixmap()  # Convert page to an image
            img = Image.frombytes("RGB", [img.width, img.height], img.samples)
            text += pytesseract.image_to_string(img) + "\n"
    return text

def extract_transactions(pdf_path):
    """Extracts transactions dynamically from digital and scanned PDFs."""
    transactions = []
    
    if is_scanned_pdf(pdf_path):
        raw_text = extract_text_from_scanned_pdf(pdf_path).split("\n")
    else:
        with pdfplumber.open(pdf_path) as pdf:
            raw_text = []
            for page in pdf.pages:
                raw_text.extend(page.extract_text().split("\n"))

    for line in raw_text:
        parts = line.split()

        # Check if the row has 6 columns (scanned bank statement)
        if len(parts) >= 6 and "/" in parts[1]:  
            try:
                posting_date = parts[0]
                transaction_date = parts[1]
                description = " ".join(parts[2:-3])  # Everything in between
                money_in = parts[-3] if parts[-3].replace(",", "").replace(".", "").isdigit() else "0.00"
                money_out = parts[-2] if parts[-2].replace(",", "").replace(".", "").isdigit() else "0.00"
                balance = parts[-1]

                transactions.append({
                    "posting_date": posting_date.strip(),
                    "transaction_date": transaction_date.strip(),
                    "description": description.strip(),
                    "money_in": money_in.strip(),
                    "money_out": money_out.strip(),
                    "balance": balance.strip()
                })
            except IndexError:
                continue

        # Handle 5-column format (previous logic)
        elif len(parts) >= 5 and "/" in parts[0]:  
            try:
                date = parts[0]
                description = " ".join(parts[1:-3])
                amount = parts[-3]
                fees = parts[-2]
                balance = parts[-1]

                transactions.append({
                    "date": date.strip(),
                    "description": description.strip(),
                    "amount": amount.strip(),
                    "fees": fees.strip(),
                    "balance": balance.strip()
                })
            except IndexError:
                continue

    return transactions


@app.route("/upload", methods=["POST"])
def upload():
    if "pdfFile" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400

    file = request.files["pdfFile"]
    file_path = f"/tmp/{file.filename}"
    file.save(file_path)

    transactions = extract_transactions(file_path)

    if not transactions:
        return jsonify({"success": False, "message": "No transactions found"}), 400

    return jsonify({"success": True, "transactions": transactions})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
