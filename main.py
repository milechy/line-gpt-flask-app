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