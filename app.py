from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import io
import base64

app = Flask(__name__)

@app.route("/")
def health_check():
    return "OCR Flask App is running!"

@app.route("/ocr", methods=["POST"])
def ocr_image():
    try:
        # 画像をbase64で受け取る前提
        data = request.get_json()
        base64_image = data.get("image")

        if not base64_image:
            return jsonify({"error": "画像データがありません"}), 400

        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(image, lang="jpn+eng")

        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500