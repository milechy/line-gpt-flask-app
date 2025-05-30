@app.route("/consultation", methods=["POST"])
def consultation():
    try:
        data = request.get_json()
        user_id = data.get("user_id", "anonymous")
        message = data.get("message", "")
        image_base64 = data.get("image", "")

        # OCR処理が必要なら画像をテキスト化
        ocr_text = ""
        if image_base64:
            try:
                image_data = base64.b64decode(image_base64)
                image = Image.open(io.BytesIO(image_data))
                ocr_text = pytesseract.image_to_string(image, lang="jpn")
            except Exception as ocr_error:
                print(f"[OCR ERROR] {ocr_error}")
                ocr_text = ""

        # アドバイス生成（ダミー例として固定文言）
        gpt_advice = f"以下のような改善が考えられます：...\n\n[OCR内容: {ocr_text}]\n\n→ 実施が難しい場合は代行見積をご検討ください。"

        # 必要ならヒアリング（今回は省略またはダミーヒアリング）

        # 日本の相場での概算見積（仮の固定値）
        jp_estimate = {
            "価格": "約15万円",
            "納期": "2週間",
            "備考": "出張費は含まれていません。"
        }

        # 弊社の見積（仮の固定値）
        our_estimate = {
            "価格": "約9万円",
            "納期": "1週間",
            "備考": "フルリモート対応・出張費なし。"
        }

        # データ保存（任意）
        supabase.table("chat_logs").insert({
            "user_id": user_id,
            "character": "Consultation",
            "message": message or "[画像]",
            "reply": gpt_advice,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }).execute()

        # レスポンス
        return jsonify({
            "advice": gpt_advice,
            "jp_estimate": jp_estimate,
            "our_estimate": our_estimate,
            "consultation_url": "https://timerex.net/s/hirokikobayashi93_780c/1ccba21c"
        })

    except Exception as e:
        print(f"[Consultation ERROR] {e}")
        return jsonify({"error": str(e)}), 500
import base64
import json
from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import io
from supabase import create_client
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Supabase client setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/ocr", methods=["POST"])
def ocr():
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "Missing 'image' field"}), 400
    try:
        image_data = base64.b64decode(data["image"])
        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(image, lang="jpn")
        try:
            supabase.table("chat_logs").insert({
                "user_id": "test_user",  # Replace with actual user_id if available
                "character": "OCR",
                "message": "[画像アップロード]",
                "reply": text,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }).execute()
        except Exception as e:
            print(f"[Supabase ERROR] {e}")
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        payload = request.json
        events = payload.get("events", [])
        for event in events:
            user_id = event["source"]["userId"]
            message = event["message"]["text"]
            print(f"[Webhook] user_id: {user_id}, message: {message}")

            # Supabaseに保存
            supabase.table("chat_logs").insert({
                "user_id": user_id,
                "character": "LINE",
                "message": message,
                "reply": "（返信未設定）",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }).execute()

        return "OK", 200
    except Exception as e:
        print(f"[Webhook ERROR] {e}")
        return "NG", 500

if __name__ == "__main__":
    try:
        result = supabase.table("chat_logs").insert({
            "user_id": "local_test_user",
            "character": "OCR",
            "message": "ローカルテストメッセージ",
            "reply": "これはローカルからの挿入テストです。",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }).execute()
        print("✅ Supabase insert 成功:", result)
    except Exception as e:
        print("❌ Supabase insert エラー:", e)