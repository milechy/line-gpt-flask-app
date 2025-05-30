import base64
import json
from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import io

app = Flask(__name__)

@app.route("/ocr", methods=["POST"])
def ocr():
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "Missing 'image' field"}), 400
    try:
        image_data = base64.b64decode(data["image"])
        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(image, lang="jpn")
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500