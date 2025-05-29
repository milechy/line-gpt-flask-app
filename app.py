import base64
from pathlib import Path
from flask import Flask, request, jsonify

def encode_image_to_base64(image_path: str) -> str:
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {image_path}")
        return ""
    except Exception as e:
        print(f"画像エンコード中にエラーが発生しました: {e}")
        return ""


# 仮のOCR処理（将来は pytesseract などに置き換え）
def dummy_ocr_process(encoded_image: str) -> str:
    return "仮のOCR結果\nこれはサンプルテキストです。"

def clean_text(raw_text: str) -> str:
    return raw_text.replace("\\n", "\n").replace("\\t", "\t").strip()

def main():
    image_path = "sample.jpg"

    if not Path(image_path).exists():
        print(f"画像ファイルが存在しません: {image_path}")
        return

    encoded_image = encode_image_to_base64(image_path)
    text = dummy_ocr_process(encoded_image)
    print("=== OCR結果 ===")
    print(clean_text(text))

app = Flask(__name__)

@app.route("/")
def index():
    return "OCR Flask App is running!"

@app.route("/ocr", methods=["POST"])
def ocr_endpoint():
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "画像データが見つかりません"}), 400

    encoded_image = data["image"]
    text = dummy_ocr_process(encoded_image)
    return jsonify({"text": clean_text(text)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)

# WSGIサーバー用にアプリケーションを指定
application = app