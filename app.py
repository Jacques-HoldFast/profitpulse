from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber

app = Flask(__name__)
CORS(app)

def extract_transactions(pdf_path):
    """Extracts transactions dynamically from a bank statement PDF."""
    transactions = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()

                for table in tables:
                    for row in table:
                        # Skip empty rows or header rows
                        if not row or "Date" in row[0]:
                            continue  

                        try:
                            date = row[0]  # First column is Date
                            description = row[1]  # Second column is Description
                            amount = row[-3]  # Third last column is Amount
                            fees = row[-2]  # Second last column is Fees
                            balance = row[-1]  # Last column is Balance

                            transactions.append({
                                "date": date.strip(),
                                "description": description.strip(),
                                "amount": amount.strip(),
                                "fees": fees.strip(),
                                "balance": balance.strip()
                            })
                        except IndexError:
                            continue  # Skip rows that don’t match expected structure

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
