import requests
import time
import os
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime

# =========================
# CONFIG (Railway Variables)
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

CATEGORY_URL = "https://www.sheinindia.in/c/sverse-5939-37961"
BASE_URL = "https://www.sheinindia.in"

bot = Bot(token=BOT_TOKEN)
posted_products = set()

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_products():
    response = requests.get(CATEGORY_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    products = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/product/" in href:
            product_link = BASE_URL + href.split("?")[0]
            product_id = product_link.split("/")[-1]

            products.append({
                "id": product_id,
                "link": product_link
            })

    return products


def send_telegram(product):
    message = f"""
🆕 NEW DROP

🛍 Product ID: {product['id']}
📁 Category: Men
🔗 View Product: {product['link']}

⏰ Time: {datetime.now().strftime("%I:%M:%S %p")}

👨‍💻 Developed by LexlordD
"""

    bot.send_message(chat_id=CHANNEL_ID, text=message)


while True:
    try:
        products = get_products()

        for product in products:
            if product["id"] not in posted_products:
                send_telegram(product)
                posted_products.add(product["id"])
                time.sleep(2)

        time.sleep(60)  # Check every 1 minute

    except Exception as e:
        print("Error:", e)
        time.sleep(10)
