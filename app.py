import base64
import json
import requests

def load_image_as_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print("❌ sample.jpg が見つかりません")
        return None

def send_to_ocr(encoded_string):
    url = "http://localhost:5050/ocr"  # 必要に応じてRenderのURLに変更
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"image": encoded_string})
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ OCR APIの呼び出しに失敗しました: {e}")
        return None

def main():
    encoded_string = load_image_as_base64("sample.jpg")
    if not encoded_string:
        return

    response = send_to_ocr(encoded_string)
    if not response:
        return

    try:
        result_text = response.json().get("text", "")
        print("=== OCR結果 ===")
        print(result_text)
    except json.JSONDecodeError:
        print("❌ OCRサーバーからのレスポンスが不正です")

if __name__ == "__main__":
    main()