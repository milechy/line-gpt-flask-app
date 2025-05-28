from flask import Flask, request
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

if __name__ == "__main__":
    app.run(debug=True)