from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Allow all origins (or specify your frontend domain)

@app.route("/upload", methods=["POST"])
def upload():
    if "pdfFile" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400

    file = request.files["pdfFile"]
    # Process the PDF here...

    return jsonify({"success": True, "transactions": []})  # Replace with actual data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)