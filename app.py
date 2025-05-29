import sys
import pytesseract
from PIL import Image

if len(sys.argv) < 2:
    print("⚠️ 画像ファイル名を指定してください。例: python ocr_test.py sample.jpg")
    sys.exit(1)

image_path = sys.argv[1]

try:
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang="eng")
    print("=== OCR結果 ===")
    print(text)
except FileNotFoundError:
    print(f"⚠️ ファイルが見つかりません: {image_path}")
except Exception as e:
    print(f"❌ エラーが発生しました: {e}")