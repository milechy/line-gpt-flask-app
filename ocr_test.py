import os
import pytesseract
from PIL import Image
import io
import sys
import pytesseract
from PIL import Image

# 必要なら pytesseract のコマンドパスを指定
# pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

if len(sys.argv) < 2:
    print("⚠️ 画像ファイル名を指定してください。例: python ocr_test.py sample.jpg")
    sys.exit(1)

image_path = sys.argv[1]

try:
    image = Image.open(image_path)
    # 日本語言語データでOCR（tesseract-langがインストールされていればOK）
    text = pytesseract.image_to_string(image, lang="jpn")
    cleaned_text = text.strip().replace("\n", "")
    print("=== OCR結果 ===")
    print(cleaned_text)
except FileNotFoundError:
    print(f"⚠️ ファイルが見つかりません: {image_path}")
except Exception as e:
    print(f"❌ エラーが発生しました: {e}")