from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

CHANNEL_SECRET = '08e002ac70b1e026209541c98a0de0a2'
CHANNEL_ACCESS_TOKEN = 'P+nUnOsdahIBJobBiMMB/qsXNy5pJs3vZjGmvZcx0No9eKUKb4neemjRudmykIpBtmztusiGtxEe0eW21BiiOOnrWR74e+WYozYv0QrEhCgHIOurdCMv84LGiUBPpwkyhjQ0fr9UXRvLcNzuaqsj5AdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

ore_list = [247440, 259820, 272810, 286450, 300770, 315810, 331600, 348180, 365590, 383870]
scroll_list = [2109, 2215, 2325, 2442, 2564, 2692, 2826, 2968, 3116, 3272]

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    parts = text.split()
    
    if len(parts) != 2:
        return  # 靜默不回覆

    try:
        total_ore = int(parts[0])
        tail = int(parts[1])
        if tail < 1 or tail > 10:
            return  # 靜默不回覆
    except:
        return  # 靜默不回覆

    ore_needed = ore_list[tail-1]
    scroll_needed = scroll_list[tail-1]

    if total_ore < ore_needed:
        reply = f"礦量不足，無法升級（需要 {ore_needed} 礦石）"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    total_ore -= ore_needed
    levels = 1
    scrolls = scroll_needed

    index = tail % 10
    while True:
        ore_next = ore_list[index]
        if total_ore >= ore_next:
            total_ore -= ore_next
            levels += 1
            scrolls += scroll_list[index]
            index = (index + 1) % 10
        else:
            break

    reply = f"可升級：{levels} 級\n消耗卷：{scrolls} 張\n剩餘礦石：{total_ore} 單位"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run()
