import base64
import json
import requests
import sys
import os

def encode_image_to_base64(image_path):
    if not os.path.exists(image_path):
        print(f"❌ ファイルが見つかりません: {image_path}")
        sys.exit(1)
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        print(f"❌ 画像の読み込み中にエラーが発生しました: {e}")
        sys.exit(1)

def send_ocr_request(base64_image, url="http://localhost:5050/ocr"):
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"image": base64_image})
        )
        response.raise_for_status()
        return response.json().get("text", "")
    except requests.exceptions.RequestException as e:
        print(f"❌ OCRリクエスト中にエラーが発生しました: {e}")
        sys.exit(1)

def clean_text(text):
    return text.replace("\\n", "\n").replace("\\t", "\t").strip()

def main():
    image_path = "sample.jpg"
    print(f"📤 画像をbase64に変換中: {image_path}")
    base64_image = encode_image_to_base64(image_path)

    print("📡 OCR APIにリクエスト送信中...")
    raw_text = send_ocr_request(base64_image)

    print("📄 === OCR 結果 ===")
    print(clean_text(raw_text))

if __name__ == "__main__":
    main()