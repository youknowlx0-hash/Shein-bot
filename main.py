import os
import time
import requests
from telegram import Bot
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")  # API key required

if not BOT_TOKEN or not CHANNEL_ID or not SEARCH_API_KEY:
    print("Missing required environment variables!")
    exit()

bot = Bot(token=BOT_TOKEN)
posted_products = set()

# API Config
SEARCH_API_URL = "https://api.searchapi.io/api/v1/search"
CATEGORY_KEYWORD = "sverse 5939"

def fetch_products():
    params = {
        "engine": "shein_search",
        "q": CATEGORY_KEYWORD,
        "api_key": SEARCH_API_KEY
    }

    try:
        r = requests.get(SEARCH_API_URL, params=params, timeout=10)
        data = r.json()

        products = []
        if "products" in data:
            for p in data["products"]:
                pid = p.get("product_id") or p.get("id")
                name = p.get("title") or "Unknown Product"
                link = p.get("product_url") or p.get("url")
                price = p.get("price") or "N/A"
                image = p.get("thumbnail_url") or p.get("image_url")

                products.append({
                    "id": pid,
                    "name": name,
                    "link": link,
                    "price": price,
                    "image": image
                })

        return products
    except Exception as e:
        print("API Fetch Error:", e)
        return []


def send_alert(prod):
    caption = f"""
🆕 NEW DROP
🛍 {prod['name']}
🆔 Product ID: {prod['id']}
💰 Price: Rs.{prod['price']}
🔗 {prod['link']}

⏰ {datetime.now().strftime('%I:%M:%S %p')}
"""

    try:
        bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=prod["image"],
            caption=caption
        )
    except Exception as e:
        print("Telegram Error:", e)


print("BOT STARTED SUCCESSFULLY")

while True:
    products = fetch_products()
    print("FOUND PRODUCTS:", len(products))

    for p in products:
        if p["id"] not in posted_products:
            send_alert(p)
            posted_products.add(p["id"])
            time.sleep(2)

    time.sleep(60)
