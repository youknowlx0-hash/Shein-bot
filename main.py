import requests
import time
import os
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not BOT_TOKEN or not CHANNEL_ID:
    print("ERROR: BOT_TOKEN or CHANNEL_ID missing!")
    exit()

bot = Bot(token=BOT_TOKEN)

CATEGORY_URL = "https://www.sheinindia.in/c/sverse-5939-37961"
BASE_URL = "https://www.sheinindia.in"

posted_products = set()

headers = {
    "User-Agent": "Mozilla/5.0"
}

# -----------------------------
# FUNCTIONS
# -----------------------------
def get_products():
    try:
        response = requests.get(CATEGORY_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        products = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/product/" in href:
                link = BASE_URL + href.split("?")[0]
                product_id = link.split("/")[-1]
                products.append({"id": product_id, "link": link})

        return products
    except Exception as e:
        print("Fetch Error:", e)
        return []

def send_message(product):
    try:
        message = f"""
🆕 NEW DROP

🛍 Product ID: {product['id']}
🔗 View Product: {product['link']}

⏰ Time: {datetime.now().strftime("%I:%M:%S %p")}

👨‍💻 Developed by LexlordD
"""
        bot.send_message(chat_id=CHANNEL_ID, text=message)
    except Exception as e:
        print("Telegram Error:", e)

# -----------------------------
# MAIN LOOP
# -----------------------------
print("BOT STARTED SUCCESSFULLY ✅")

while True:
    try:
        products = get_products()
        print("TOTAL PRODUCTS FOUND:", len(products))

        for product in products:
            if product["id"] not in posted_products:
                send_message(product)
                posted_products.add(product["id"])
                time.sleep(2)  # polite pause

        time.sleep(10)  # check every 10 sec
    except Exception as e:
        print("Main Loop Error:", e)
        time.sleep(10)
