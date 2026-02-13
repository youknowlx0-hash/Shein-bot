import os
import time
import requests
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# -----------------------------
# CONFIG
# -----------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
API_KEY = os.getenv("RUNHUMAN_KEY")  # Set this to qa_live_cd119151b7fa768a8600e32c23b3662d2e0881b3
PRICE_THRESHOLD = float(os.getenv("PRICE_THRESHOLD") or 1000)

if not BOT_TOKEN or not CHANNEL_ID or not API_KEY:
    print("Missing BOT_TOKEN, CHANNEL_ID or RUNHUMAN_KEY")
    exit()

bot = Bot(token=BOT_TOKEN)
posted_products = set()

API_URL = "https://runhuman.com/mcp"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# -----------------------------
# Fetch products from runhuman.com
# -----------------------------
def fetch_products():
    try:
        resp = requests.get(API_URL, headers=HEADERS, timeout=10)
        data = resp.json()

        products = []
        for item in data.get("products", []):
            prod_id = item.get("id")
            name = item.get("name", "No Name")
            price = float(item.get("price") or 0)
            image = item.get("image")
            link = item.get("link")
            
            products.append({
                "id": prod_id,
                "name": name,
                "price": price,
                "image": image,
                "link": link
            })
        return products

    except Exception as e:
        print("API Error:", e)
        return []


# -----------------------------
# Send Telegram Alert
# -----------------------------
def send_alert(prod):
    caption = f"""
🆕 NEW DROP
🛍 {prod['name']}
🆔 Product ID: {prod['id']}
💰 Price: Rs.{prod['price']}
🔗 {prod['link']}
⏰ {datetime.now().strftime('%I:%M:%S %p')}
"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("View Product", url=prod['link'])]
    ])
    try:
        if prod["image"]:
            bot.send_photo(chat_id=CHANNEL_ID, photo=prod["image"], caption=caption, reply_markup=keyboard)
        else:
            bot.send_message(chat_id=CHANNEL_ID, text=caption, reply_markup=keyboard)
    except Exception as e:
        print("Telegram send error:", e)


# -----------------------------
# MAIN LOOP
# -----------------------------
print("RUNHUMAN BOT STARTED 🚀")

while True:
    products = fetch_products()
    print("FOUND:", len(products))

    for p in products:
        if p["id"] not in posted_products and p["price"] <= PRICE_THRESHOLD:
            send_alert(p)
            posted_products.add(p["id"])
            time.sleep(2)

    time.sleep(60)  # check every minute
