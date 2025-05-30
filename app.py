import base64
import json
import requests
import sys

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Error: ファイルが見つかりません: {image_path}")
        sys.exit(1)
    except Exception as e:
        print(f"画像の読み込み中にエラーが発生しました: {e}")
        sys.exit(1)

def post_image_for_ocr(encoded_string, url):
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"image": encoded_string})
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"OCRリクエスト中にエラーが発生しました: {e}")
        sys.exit(1)

def main():
    image_path = "sample.jpg"
    ocr_url = "http://localhost:5050/ocr"

    print("画像をエンコード中...")
    encoded_string = encode_image_to_base64(image_path)

    print("OCRサーバーへ送信中...")
    response = post_image_for_ocr(encoded_string, ocr_url)

    print(f"ステータスコード: {response.status_code}")

    try:
        result_text = response.json().get("text", "")
        cleaned_text = result_text.replace("\\n", "\n").replace("\\t", "\t").strip()
        print("=== OCR結果 ===")
        print(cleaned_text)
    except Exception as e:
        print(f"レスポンスの解析中にエラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()