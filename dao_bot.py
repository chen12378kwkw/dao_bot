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
admin_state = {}

# ==========================================
# GỬI ALBUM THEO NGÀY
# ==========================================
def send_album(chat_id, date_key, date_label):
    data = load_data()
    album = data.get(date_key)
    if not album or (not album.get("photos") and not album.get("video")):
        bot.send_message(chat_id, f"😅 Chưa có album ngày *{date_label}* nha sếp!", parse_mode='Markdown')
        return

    # Gửi ảnh
    photos = album.get("photos", [])
    if photos:
        if len(photos) == 1:
            bot.send_photo(chat_id, photo=photos[0])
        else:
            media = [telebot.types.InputMediaPhoto(p) for p in photos]
            bot.send_media_group(chat_id, media)

    # Gửi video
    if album.get("video"):
        bot.send_video(chat_id, video=album["video"])

    # Gửi mô tả
    caption = album.get("caption", "")
    if caption:
        bot.send_message(chat_id, caption, parse_mode='Markdown')

def send_date_picker(chat_id, label="📅 Chọn ngày xem:"):
    today_key = get_date_key(0)
    yesterday_key = get_date_key(-1)
    today_label = get_date_str(0)
    yesterday_label = get_date_str(-1)

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton(f"📅 Hôm nay ({today_label})", callback_data=f"view_{today_key}"),
        telebot.types.InlineKeyboardButton(f"📅 Hôm qua ({yesterday_label})", callback_data=f"view_{yesterday_key}")
    )
    bot.send_message(chat_id, label, reply_markup=markup)

# ==========================================
# USER: /start
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID,
            "👑 *Chào Admin!*\n\n"
            "Lệnh quản lý:\n"
            "📸 /setphoto — Thêm ảnh cho ngày hôm nay\n"
            "🎬 /setvideo — Đặt video cho ngày hôm nay\n"
            "📝 /setcaption — Đặt mô tả cho ngày hôm nay\n"
            "👁 /preview — Xem trước album hôm nay\n"
            "🗑 /clearphoto — Xoá ảnh hôm nay\n",
            parse_mode='Markdown')
        return

    today_key = get_date_key(0)
    today_label = get_date_str(0)

    bot.send_message(message.chat.id,
        f"Chào sếp! 👋\n🌸 *Đào* gửi ngay cho sếp album hot *{today_label}* nha!",
        parse_mode='Markdown')

    send_album(message.chat.id, today_key, today_label)

    # Sau đó hiện nút chọn ngày hôm qua
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

    # Sau khi xem xong cho chọn ngày khác
    send_date_picker(call.message.chat.id, "📅 Xem ngày khác không sếp?")

# ==========================================
# ADMIN: lệnh set
# ==========================================
@bot.message_handler(commands=['setphoto'])
def cmd_setphoto(message):
    if message.chat.id != ADMIN_ID: return
    admin_state[ADMIN_ID] = "waiting_photo"
    bot.send_message(ADMIN_ID, f"📸 Gửi ảnh cho album ngày *{get_date_str()}* nha! (gửi nhiều ảnh cũng được)", parse_mode='Markdown')

@bot.message_handler(commands=['setvideo'])
def cmd_setvideo(message):
    if message.chat.id != ADMIN_ID: return
    admin_state[ADMIN_ID] = "waiting_video"
    bot.send_message(ADMIN_ID, f"🎬 Gửi video cho album ngày *{get_date_str()}*!", parse_mode='Markdown')

@bot.message_handler(commands=['setcaption'])
def cmd_setcaption(message):
    if message.chat.id != ADMIN_ID: return
    admin_state[ADMIN_ID] = "waiting_caption"
    bot.send_message(ADMIN_ID, f"📝 Gửi mô tả cho album ngày *{get_date_str()}*!", parse_mode='Markdown')

@bot.message_handler(commands=['preview'])
def cmd_preview(message):
    if message.chat.id != ADMIN_ID: return
    today_key = get_date_key(0)
    today_label = get_date_str(0)
    bot.send_message(ADMIN_ID, f"👁 Xem trước album *{today_label}*:", parse_mode='Markdown')
    send_album(ADMIN_ID, today_key, today_label)

@bot.message_handler(commands=['clearphoto'])
def cmd_clearphoto(message):
    if message.chat.id != ADMIN_ID: return
    today_key = get_date_key(0)
    data = load_data()
    if today_key in data:
        data[today_key]["photos"] = []
        save_data(data)
    bot.send_message(ADMIN_ID, "🗑 Đã xoá ảnh hôm nay!")

# ==========================================
# NHẬN ẢNH TỪ ADMIN
# ==========================================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.chat.id != ADMIN_ID: return
    if admin_state.get(ADMIN_ID) == "waiting_photo":
        file_id = message.photo[-1].file_id
        today_key = get_date_key(0)
        data = load_data()
        if today_key not in data:
            data[today_key] = {"photos": [], "video": None, "caption": ""}
        data[today_key]["photos"].append(file_id)
        save_data(data)
        bot.send_message(ADMIN_ID, f"✅ Đã thêm ảnh! (Tổng: {len(data[today_key]['photos'])} ảnh)\nGửi thêm ảnh hoặc dùng lệnh khác.")

# ==========================================
# NHẬN VIDEO TỪ ADMIN
# ==========================================
@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.chat.id != ADMIN_ID: return
    if admin_state.get(ADMIN_ID) == "waiting_video":
        file_id = message.video.file_id
        today_key = get_date_key(0)
        data = load_data()
        if today_key not in data:
            data[today_key] = {"photos": [], "video": None, "caption": ""}
        data[today_key]["video"] = file_id
        save_data(data)
        admin_state[ADMIN_ID] = None
        bot.send_message(ADMIN_ID, "✅ Đã cập nhật video!")

# ==========================================
# NHẬN TEXT TỪ ADMIN
# ==========================================
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.chat.id == ADMIN_ID and admin_state.get(ADMIN_ID) == "waiting_caption":
        today_key = get_date_key(0)
        data = load_data()
        if today_key not in data:
            data[today_key] = {"photos": [], "video": None, "caption": ""}
        data[today_key]["caption"] = message.text
        save_data(data)
        admin_state[ADMIN_ID] = None
        bot.send_message(ADMIN_ID, "✅ Đã cập nhật mô tả!")
        return
    if message.chat.id != ADMIN_ID:
        today_key = get_date_key(0)
        today_label = get_date_str(0)
        send_album(message.chat.id, today_key, today_label)

print("✅ Đào Bot đang chạy...")
bot.infinity_polling()
