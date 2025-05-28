from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from supabase import create_client
import openai
import os

# 環境変数
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 初期化
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    return "OK"

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    reply = generate_gpt_reply(user_input)

    # データベース保存
    user_id = event.source.user_id
    save_conversation(
    user_id=event.source.user_id,
    character="未設定",  # 後で会話スタイルを選ばせるように拡張可能
    message=user_input,
    reply=reply
)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

def generate_gpt_reply(user_input):
    messages = [
        {"role": "system", "content": "あなたは親切なWeb制作診断AIです。毎回必ず『前の回答に感謝＋次の質問』を1メッセージ内で返してください。"},
        {"role": "user", "content": user_input}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return "申し訳ありません、少し問題が発生しました。もう一度お試しください。"

def save_conversation(user_id, character, message, reply):
    try:
        response = supabase.table("chat_logs").insert({
            "user_id": user_id,
            "character": character,
            "message": message,
            "reply": reply
        }).execute()
        print("Supabase Insert Success:", response)
    except Exception as e:
        print("Supabase Insert Error:", e)

import boto3
from botocore.exceptions import NoCredentialsError

# Wasabi 設定
WASABI_ACCESS_KEY = os.getenv("WASABI_ACCESS_KEY")
WASABI_SECRET_KEY = os.getenv("WASABI_SECRET_KEY")
WASABI_BUCKET_NAME = os.getenv("WASABI_BUCKET_NAME")
WASABI_ENDPOINT_URL = "https://s3.ap-northeast-1.wasabisys.com"

def upload_file_to_wasabi(file_path, object_name):
    try:
        s3 = boto3.client(
            's3',
            endpoint_url=WASABI_ENDPOINT_URL,
            aws_access_key_id=WASABI_ACCESS_KEY,
            aws_secret_access_key=WASABI_SECRET_KEY
        )
        s3.upload_file(file_path, WASABI_BUCKET_NAME, object_name)
        print("✅ Upload Successful:", object_name)
        return True
    except FileNotFoundError:
        print("❌ File not found.")
        return False
    except NoCredentialsError:
        print("❌ Credentials not available.")
        return False
    
from linebot.models import ImageMessage
import tempfile

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    print("📸 画像メッセージを受信しました")
    message_id = event.message.id

    # 一時ファイルを保存
    message_content = line_bot_api.get_message_content(message_id)
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        temp_file_path = tf.name

    # ファイル名（例：user_id/timestamp.jpg）
    import time
    user_id = event.source.user_id
    filename = f"{user_id}/{int(time.time())}.jpg"

    # Wasabiにアップロード
    success = upload_file_to_wasabi(temp_file_path, filename)

    # ✅ Supabaseに記録
    save_conversation(
        user_id=user_id,
        character="未設定",
        message="[画像アップロード]",
        reply=f"[Wasabiに保存済み: {filename}]"
    )

    # ユーザーに返信
    reply_text = "✅ 画像をアップロードしました！" if success else "❌ アップロードに失敗しました。"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

    # 一時ファイル削除
    os.remove(temp_file_path)

if __name__ == "__main__":
    app.run(debug=True)