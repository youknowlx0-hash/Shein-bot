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
PRICE_THRESHOLD = float(os.getenv("PRICE_THRESHOLD") or 1000)  # Only alert below this price
API_KEY = os.getenv("API_KEY")  # Your searchapi.io or Shein API key

if not BOT_TOKEN or not CHANNEL_ID or not API_KEY:
    print("Missing BOT_TOKEN, CHANNEL_ID or API_KEY")
    exit()

bot = Bot(token=BOT_TOKEN)
posted_products = set()

# Multiple categories / search queries
CATEGORY_QUERIES = [
    "sverse 5939-37961",
    # Add more queries if needed
]

API_URL = "https://api.searchapi.io/api/v1/search"  # example API endpoint

# -----------------------------
# Fetch Products via API
# -----------------------------
def fetch_products(query):
    try:
        params = {
            "engine": "shein_search",
            "q": query,
            "api_key": API_KEY
        }
        response = requests.get(API_URL, params=params, timeout=10)
        data = response.json()

        products = []
        for item in data.get("products", []):
            product_id = item.get("id") or item.get("product_id")
            name = item.get("name") or "Unknown Product"
            price = float(item.get("price", 0))
            link = item.get("link") or item.get("url")
            image = item.get("image") or item.get("image_url")

            products.append({
                "id": product_id,
                "name": name,
                "price": price,
                "link": link,
                "image": image
            })
        return products
    except Exception as e:
        print("API Fetch Error:", e)
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
⏰ {datetime.now().strftime('%I:%M:%S %p')}
"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("View Product", url=prod['link'])]
    ])
    try:
        if prod['image']:
            bot.send_photo(chat_id=CHANNEL_ID, photo=prod['image'], caption=caption, reply_markup=keyboard)
        else:
            bot.send_message(chat_id=CHANNEL_ID, text=caption, reply_markup=keyboard)
    except Exception as e:
        print("Telegram Error:", e)

# -----------------------------
# MAIN LOOP
# -----------------------------
print("API-based Premium Bot Started ✅")

while True:
    try:
        for query in CATEGORY_QUERIES:
            products = fetch_products(query)
            print(f"Found {len(products)} products for query: {query}")

            for p in products:
                if p['id'] not in posted_products and p['price'] <= PRICE_THRESHOLD:
                    send_alert(p)
                    posted_products.add(p['id'])
                    time.sleep(2)

        time.sleep(60)  # check every 60 seconds

    except Exception as e:
        print("Main Loop Error:", e)
        time.sleep(30)
