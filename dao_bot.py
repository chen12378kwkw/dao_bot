"""
🤖 ĐÀO BOT
===============================
Cách chạy:
1. pip install pyTelegramBotAPI
2. python dao_bot.py
"""

import telebot
import json
import os
from datetime import datetime, timedelta

TOKEN = "8733413325:AAGPZJDsUuobpwWXd_KmN6BJEwJv2xno3Qo"
ADMIN_ID = 8182465056
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_date_str(delta=0):
    d = datetime.now() + timedelta(days=delta)
    return d.strftime("%d/%m/%Y")

def get_date_key(delta=0):
    d = datetime.now() + timedelta(days=delta)
    return d.strftime("%Y-%m-%d")

bot = telebot.TeleBot(TOKEN)

# admin_state lưu trạng thái + index đang chỉnh
# vd: {"state": "waiting_photo_caption", "index": 0}
admin_state = {}

# ==========================================
# GỬI ALBUM THEO NGÀY
# ==========================================
def send_album(chat_id, date_key, date_label):
    data = load_data()
    album = data.get(date_key)
    if not album or (not album.get("items")):
        bot.send_message(chat_id, f"😅 Chưa có album ngày *{date_label}* nha sếp!", parse_mode='Markdown')
        return

    for item in album["items"]:
        caption = item.get("caption", "")
        if item["type"] == "photo":
            bot.send_photo(chat_id, photo=item["file_id"], caption=caption or None)
        elif item["type"] == "video":
            bot.send_video(chat_id, video=item["file_id"], caption=caption or None)

# ==========================================
# USER: /start
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID,
            "👑 *Chào Admin!*\n\n"
            "Lệnh quản lý:\n"
            "📸 /addphoto — Thêm ảnh + mô tả\n"
            "🎬 /addvideo — Thêm video + mô tả\n"
            "👁 /preview — Xem trước album hôm nay\n"
            "🗑 /clear — Xoá toàn bộ album hôm nay\n"
            "📋 /list — Xem danh sách items hôm nay\n",
            parse_mode='Markdown')
        return

    today_key = get_date_key(0)
    today_label = get_date_str(0)
    bot.send_message(message.chat.id,
        f"Chào sếp! 👋\n🌸 *Đào* gửi ngay cho sếp album hot *{today_label}* nha!",
        parse_mode='Markdown')
    send_album(message.chat.id, today_key, today_label)

    yesterday_label = get_date_str(-1)
    yesterday_key = get_date_key(-1)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        f"📅 Xem album hôm qua ({yesterday_label})",
        callback_data=f"view_{yesterday_key}"
    ))
    bot.send_message(message.chat.id, "Sếp muốn xem thêm?", reply_markup=markup)

# ==========================================
# CALLBACK: chọn ngày
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("view_"))
def handle_view(call):
    date_key = call.data.replace("view_", "")
    try:
        d = datetime.strptime(date_key, "%Y-%m-%d")
        date_label = d.strftime("%d/%m/%Y")
    except:
        date_label = date_key
    bot.answer_callback_query(call.id, f"Đang tải album {date_label}...")
    send_album(call.message.chat.id, date_key, date_label)

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton(f"📅 Hôm nay ({get_date_str(0)})", callback_data=f"view_{get_date_key(0)}"),
        telebot.types.InlineKeyboardButton(f"📅 Hôm qua ({get_date_str(-1)})", callback_data=f"view_{get_date_key(-1)}")
    )
    bot.send_message(call.message.chat.id, "📅 Xem ngày khác không sếp?", reply_markup=markup)

# ==========================================
# ADMIN: /addphoto
# ==========================================
@bot.message_handler(commands=['addphoto'])
def cmd_addphoto(message):
    if message.chat.id != ADMIN_ID: return
    admin_state[ADMIN_ID] = {"state": "waiting_photo"}
    bot.send_message(ADMIN_ID, f"📸 Gửi ảnh cho ngày *{get_date_str()}*!", parse_mode='Markdown')

# ==========================================
# ADMIN: /addvideo
# ==========================================
@bot.message_handler(commands=['addvideo'])
def cmd_addvideo(message):
    if message.chat.id != ADMIN_ID: return
    admin_state[ADMIN_ID] = {"state": "waiting_video"}
    bot.send_message(ADMIN_ID, f"🎬 Gửi video cho ngày *{get_date_str()}*!", parse_mode='Markdown')

# ==========================================
# ADMIN: /preview
# ==========================================
@bot.message_handler(commands=['preview'])
def cmd_preview(message):
    if message.chat.id != ADMIN_ID: return
    today_key = get_date_key(0)
    today_label = get_date_str(0)
    bot.send_message(ADMIN_ID, f"👁 Xem trước album *{today_label}*:", parse_mode='Markdown')
    send_album(ADMIN_ID, today_key, today_label)

# ==========================================
# ADMIN: /list
# ==========================================
@bot.message_handler(commands=['list'])
def cmd_list(message):
    if message.chat.id != ADMIN_ID: return
    today_key = get_date_key(0)
    data = load_data()
    album = data.get(today_key, {})
    items = album.get("items", [])
    if not items:
        bot.send_message(ADMIN_ID, "📋 Chưa có gì hôm nay!")
        return
    text = f"📋 Album hôm nay ({get_date_str()}) — {len(items)} items:\n\n"
    for i, item in enumerate(items):
        emoji = "📸" if item["type"] == "photo" else "🎬"
        cap = item.get("caption") or "_(chưa có mô tả)_"
        text += f"{i+1}. {emoji} {cap}\n"
    bot.send_message(ADMIN_ID, text, parse_mode='Markdown')

# ==========================================
# ADMIN: /clear
# ==========================================
@bot.message_handler(commands=['clear'])
def cmd_clear(message):
    if message.chat.id != ADMIN_ID: return
    today_key = get_date_key(0)
    data = load_data()
    data[today_key] = {"items": []}
    save_data(data)
    bot.send_message(ADMIN_ID, "🗑 Đã xoá toàn bộ album hôm nay!")

# ==========================================
# NHẬN ẢNH TỪ ADMIN
# ==========================================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.chat.id != ADMIN_ID: return
    st = admin_state.get(ADMIN_ID, {})
    if st.get("state") == "waiting_photo":
        file_id = message.photo[-1].file_id
        # Lưu tạm file_id, chờ mô tả
        admin_state[ADMIN_ID] = {"state": "waiting_photo_caption", "file_id": file_id, "type": "photo"}
        bot.send_message(ADMIN_ID, "✅ Nhận ảnh rồi!\n📝 Giờ gửi *mô tả* cho ảnh này nha! (gõ /skip nếu không cần)", parse_mode='Markdown')

# ==========================================
# NHẬN VIDEO TỪ ADMIN
# ==========================================
@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.chat.id != ADMIN_ID: return
    st = admin_state.get(ADMIN_ID, {})
    if st.get("state") == "waiting_video":
        file_id = message.video.file_id
        admin_state[ADMIN_ID] = {"state": "waiting_video_caption", "file_id": file_id, "type": "video"}
        bot.send_message(ADMIN_ID, "✅ Nhận video rồi!\n📝 Giờ gửi *mô tả* cho video này nha! (gõ /skip nếu không cần)", parse_mode='Markdown')

# ==========================================
# /skip — bỏ qua mô tả
# ==========================================
@bot.message_handler(commands=['skip'])
def cmd_skip(message):
    if message.chat.id != ADMIN_ID: return
    st = admin_state.get(ADMIN_ID, {})
    if st.get("state") in ("waiting_photo_caption", "waiting_video_caption"):
        _save_item(st["file_id"], st["type"], "")
        admin_state[ADMIN_ID] = {}
        bot.send_message(ADMIN_ID, "✅ Đã lưu không kèm mô tả!")

# ==========================================
# NHẬN TEXT (MÔ TẢ) TỪ ADMIN
# ==========================================
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.chat.id == ADMIN_ID:
        st = admin_state.get(ADMIN_ID, {})
        if st.get("state") in ("waiting_photo_caption", "waiting_video_caption"):
            _save_item(st["file_id"], st["type"], message.text)
            admin_state[ADMIN_ID] = {}
            emoji = "📸" if st["type"] == "photo" else "🎬"
            bot.send_message(ADMIN_ID, f"✅ Đã lưu {emoji} kèm mô tả!\n\nThêm tiếp? Dùng /addphoto hoặc /addvideo")
            return
    if message.chat.id != ADMIN_ID:
        today_key = get_date_key(0)
        today_label = get_date_str(0)
        send_album(message.chat.id, today_key, today_label)

def _save_item(file_id, item_type, caption):
    today_key = get_date_key(0)
    data = load_data()
    if today_key not in data:
        data[today_key] = {"items": []}
    data[today_key]["items"].append({
        "type": item_type,
        "file_id": file_id,
        "caption": caption
    })
    save_data(data)

print("✅ Đào Bot đang chạy...")
bot.infinity_polling()
