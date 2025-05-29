import base64
import json
import requests

# 1. sample.jpg を base64 でエンコード
with open("sample.jpg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

# 2. FlaskアプリにPOST
response = requests.post(
    "http://localhost:5050/ocr",
    headers={"Content-Type": "application/json"},
    data=json.dumps({"image": encoded_string})
)

# 3. 結果表示
print(response.status_code)

result_text = response.json().get("text", "")
cleaned_text = result_text.replace("\\n", "\n").replace("\\t", "\t").strip()

print("=== OCR結果 ===")
print(cleaned_text)