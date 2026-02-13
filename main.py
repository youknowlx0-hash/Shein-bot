import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# -----------------------------
# CONFIG
# -----------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PRICE_THRESHOLD = float(os.getenv("PRICE_THRESHOLD") or 1000)  # Only alert below price

if not BOT_TOKEN or not CHANNEL_ID:
    print("Missing BOT_TOKEN or CHANNEL_ID")
    exit()

bot = Bot(token=BOT_TOKEN)
posted_products = set()
CATEGORY_URL = "https://www.sheinindia.in/c/sverse-5939-37961"

# -----------------------------
# Selenium Headless Setup
# -----------------------------
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=chrome_options)

# -----------------------------
# Fetch Products
# -----------------------------
def fetch_products():
    try:
        driver.get(CATEGORY_URL)
        time.sleep(5)  # wait for JS

        products = []
        items = driver.find_elements(By.CSS_SELECTOR, "a[href*='/product/']")

        for item in items:
            link = item.get_attribute("href")
            product_id = link.split("/")[-1]

            try:
                name = item.find_element(By.CSS_SELECTOR, "div.product-item__name").text
            except:
                name = "Unknown Product"

            try:
                price_text = item.find_element(By.CSS_SELECTOR, "div.product-item__price-current").text
                price = float(price_text.replace("₹","").replace(",","").strip())
            except:
                price = 0

            try:
                image = item.find_element(By.TAG_NAME, "img").get_attribute("src")
            except:
                image = None

            products.append({
                "id": product_id,
                "name": name,
                "price": price,
                "link": link,
                "image": image
            })
        return products
    except Exception as e:
        print("Fetch Error:", e)
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
print("PREMIUM BOT STARTED ✅")

while True:
    try:
        products = fetch_products()
        print(f"Found Products: {len(products)}")

        for p in products:
            if p['id'] not in posted_products and p['price'] <= PRICE_THRESHOLD:
                send_alert(p)
                posted_products.add(p['id'])
                time.sleep(2)

        time.sleep(10)  # check every 10 seconds
    except Exception as e:
        print("Main Loop Error:", e)
        time.sleep(10)
