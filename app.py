from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import re
import time

app = Flask(__name__)

# LINE channel credentials
CHANNEL_SECRET = '08e002ac70b1e026209541c98a0de0a2'
CHANNEL_ACCESS_TOKEN = 'P+nUnOsdahIBJobBiMMB/qsXNy5pJs3vZjGmvZcx0No9eKUKb4neemjRudmykIpBtmztusiGtxEe0eW21BiiOOnrWR74e+WYozYv0QrEhCgHIOurdCMv84LGiUBPpwkyhjQ0fr9UXRvLcNzuaqsj5AdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 礦石需求 (不打折)
ore_list = [247440, 259820, 272810, 286450, 300770, 315810, 331600, 348180, 365590, 383870]

# 卷軸需求 (原始卷數 * 3 再打82折四捨五入)
scroll_list = [5188, 5449, 5720, 6007, 6307, 6622, 6952, 7301, 7665, 8049]

# 防刷紀錄
user_last_action = {}
cooldown_seconds = 2

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def parse_ore_input(ore_str):
    ore_str = ore_str.replace('\u3000', '').replace(' ', '').lower()
    match = re.match(r'^([0-9]*\.?[0-9]+)k?$', ore_str)
    if not match:
        return None
    number = float(match.group(1))
    total_ore = int(round(number * 1000))
    return total_ore

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    now = time.time()

    last_action = user_last_action.get(user_id, 0)
    if now - last_action < cooldown_seconds:
        return
    user_last_action[user_id] = now

    text = event.message.text.strip().replace('\u3000', ' ')
    parts = text.split()

    if len(parts) != 2:
        return

    ore_str = parts[0]
    tail_str = parts[1]

    total_ore = parse_ore_input(ore_str)
    if total_ore is None:
        return

    try:
        tail = int(tail_str)
        if tail < 0 or tail > 9:
            return
    except:
        return

    current_index = (tail + 1) % 10
    ore_needed = ore_list[current_index]
    scroll_needed = scroll_list[current_index]

    if total_ore < ore_needed:
        reply = f"礦量不足，無法升級（需要 {ore_needed} 礦石）"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    total_ore -= ore_needed
    levels = 1
    scrolls = scroll_needed

    index = (current_index + 1) % 10
    while True:
        ore_next = ore_list[index]
        if total_ore >= ore_next:
            total_ore -= ore_next
            levels += 1
            scrolls += scroll_list[index]
            index = (index + 1) % 10
        else:
            break

    # 計算總提升百分比
    total_percent = levels * 1500
    percent_k = round(total_percent / 10, 1)

    reply = (
        f"可升級：{levels} 級\n"
        f"消耗卷：{scrolls} 張\n"
        f"剩餘礦石：{total_ore} 單位\n"
        f"預期提升：約 {percent_k}k%"
    )

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run()
