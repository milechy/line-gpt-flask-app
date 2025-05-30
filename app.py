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
    send_webhook_notification("OCRリクエストが処理されました。")
    return jsonify({"text": clean_text(text)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)

# WSGIサーバー用にアプリケーションを指定
application = app

# Webhook通知用関数
import requests

def send_webhook_notification(message: str):
    webhook_url = "https://line-gpt-flask-app.onrender.com/webhook"
    try:
        response = requests.post(
            webhook_url,
            json={"text": message},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code != 200:
            print(f"Webhook送信エラー: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Webhook送信中にエラーが発生しました: {e}")