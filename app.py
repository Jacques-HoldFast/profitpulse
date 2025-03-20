from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF

app = Flask(__name__)
CORS(app)

def extract_transactions(pdf_path):
    """Extracts transactions from a bank statement PDF."""
    transactions = []
    
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text("text") for page in doc])
        
        # Split text into lines and find transaction rows
        lines = text.split("\n")
        for line in lines:
            # Basic format check (date + description + amount)
            if "/" in line and any(char.isdigit() for char in line):
                parts = line.split()
                if len(parts) >= 3:
                    date = parts[0]
                    description = " ".join(parts[1:-2])
                    amount = parts[-2]
                    balance = parts[-1]
                    
                    transactions.append({
                        "date": date,
                        "description": description,
                        "amount": amount,
                        "balance": balance
                    })

    except Exception as e:
        return {"error": str(e)}

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
