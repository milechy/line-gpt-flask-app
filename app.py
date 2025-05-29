import base64
import json
import requests
from pathlib import Path

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

def send_image_to_ocr_api(encoded_image: str, api_url: str = "http://localhost:5050/ocr") -> dict:
    if not encoded_image:
        return {}

    try:
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"image": encoded_image})
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"OCR APIへのリクエストに失敗しました: {e}")
        return {}

def clean_text(raw_text: str) -> str:
    return raw_text.replace("\\n", "\n").replace("\\t", "\t").strip()

def main():
    image_path = "sample.jpg"

    if not Path(image_path).exists():
        print(f"画像ファイルが存在しません: {image_path}")
        return

    encoded_image = encode_image_to_base64(image_path)
    result = send_image_to_ocr_api(encoded_image)

    if "text" in result:
        print("=== OCR結果 ===")
        print(clean_text(result["text"]))
    else:
        print("OCR結果が取得できませんでした。")

if __name__ == "__main__":
    main()