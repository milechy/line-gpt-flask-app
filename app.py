from flask import Flask, request, abort
from linebot.models import FlexSendMessage, TextSendMessage, MessageEvent, TextMessage
from linebot import LineBotApi, WebhookHandler

import os


# --- LINE credentials are now taken from environment variables ---
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET       = os.getenv("LINE_CHANNEL_SECRET")

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    raise RuntimeError("⚠️ Environment variables LINE_CHANNEL_ACCESS_TOKEN and/or LINE_CHANNEL_SECRET are not set.")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler      = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)

# Webhook endpoint
@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Webhook Error:", e)
        abort(400)
    return 'OK'

import json
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text.strip()
    user_id = event.source.user_id
    print(f"[DEBUG] Received message: '{user_input}' from user: {user_id}")

    # キャラ変更のリクエストがあれば優先して処理
    if user_input.strip() in ["キャラ変更", "キャラ選択"]:
        print("[DEBUG] Character change request detected")
        flex_contents = create_character_selection_flex()
        print("[DEBUG] Flex contents:", json.dumps(flex_contents, ensure_ascii=False))
        flex_message = FlexSendMessage(
            alt_text="キャラクターを選んでください",
            contents=flex_contents
        )
        reply = "キャラクターを変更します。以下から選んでください。"
        try:
            line_bot_api.reply_message(event.reply_token, [
                TextSendMessage(text=reply),
                flex_message
            ])
            save_conversation(user_id, "未設定", user_input, reply)
        except Exception as e:
            import traceback
            print("Reply Error:", e)
            traceback.print_exc()
        return

    # ボタン押下によるアクション処理
    if user_input in ["ホームページの困りごと相談", "ホームページの見積もり診断", "ホームページの困りごとを相談したい", "ホームページの見積もりを診断してほしい", "ホームページの困りごと", "見積もり診断"]:
        character = get_user_character(user_id)
        if not character:
            print("[DEBUG] Sending character selection Flex message")
            flex_message = FlexSendMessage(
                alt_text="キャラクターを選んでください",
                contents=create_character_selection_flex()
            )
            line_bot_api.reply_message(event.reply_token, flex_message)
            return

        reply = generate_gpt_reply(user_input, character)
        save_conversation(user_id, character, user_input, reply)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # 通常のメッセージ処理
    character = get_user_character(user_id)
    if not character:
        print("[DEBUG] Sending character selection Flex message")
        flex_message = FlexSendMessage(
            alt_text="キャラクターを選んでください",
            contents=create_character_selection_flex()
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
        return

    reply = generate_gpt_reply(user_input, character)
    save_conversation(user_id, character, user_input, reply)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))


# --- generate_gpt_reply 関数の防御的実装 ---
def generate_gpt_reply(user_input, character):
    if not character or character == "未設定":
        return "キャラクターが未設定です。先にキャラクターを選択してください。"

    messages = [
        {"role": "system", "content": f"あなたは{character}というキャラクターになりきって親切なWeb制作診断AIです。"},
        {"role": "user", "content": user_input}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 一時的にgpt-3.5-turboに変更
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        import traceback
        print("GPT Error:", e)
        traceback.print_exc()
        return f"⚠️ GPTエラーが発生しました: {str(e)}"


def create_character_selection_flex():
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "キャラクターを選んでください", "weight": "bold", "size": "lg", "margin": "md"},
                {"type": "separator", "margin": "md"},
                {
                    "type": "button",
                    "action": {"type": "postback", "label": "柚葉", "data": "SET_CHARACTER:柚葉"},
                    "style": "primary"
                },
                {
                    "type": "button",
                    "action": {"type": "postback", "label": "優芽", "data": "SET_CHARACTER:優芽"},
                    "style": "primary"
                },
                {
                    "type": "button",
                    "action": {"type": "postback", "label": "澪", "data": "SET_CHARACTER:澪"},
                    "style": "primary"
                },
                {
                    "type": "button",
                    "action": {"type": "postback", "label": "剣太郎", "data": "SET_CHARACTER:剣太郎"},
                    "style": "primary"
                },
                {
                    "type": "button",
                    "action": {"type": "postback", "label": "鈴木", "data": "SET_CHARACTER:鈴木"},
                    "style": "primary"
                },
                {
                    "type": "button",
                    "action": {"type": "postback", "label": "陽菜", "data": "SET_CHARACTER:陽菜"},
                    "style": "primary"
                }
            ]
        }
    }
@app.route("/debug/flex")
def debug_flex():
    from flask import jsonify
    return jsonify(create_character_selection_flex())