import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# -----------------------------
# CONFIG
# -----------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PRICE_THRESHOLD = float(os.getenv("PRICE_THRESHOLD") or 1000)  # Only alert below this price

if not BOT_TOKEN or not CHANNEL_ID:
    print("Missing BOT_TOKEN or CHANNEL_ID")
    exit()

bot = Bot(token=BOT_TOKEN)
posted_products = set()

# Multiple categories support
CATEGORY_URLS = [
    "https://www.sheinindia.in/c/sverse-5939-37961",
    # Add more categories here if needed
]

# -----------------------------
# Selenium Headless Setup with ChromeDriverManager
# -----------------------------
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# -----------------------------
# Fetch Products
# -----------------------------
def fetch_products(category_url):
    try:
        driver.get(category_url)
        print(f"Accessing category: {category_url}")
        time.sleep(7)  # wait for JS to load

        try:
            items = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/product/']"))
            )
        except TimeoutException:
            print("No products found in this category.")
            return []

        products = []

        for item in items:
            try:
                link = item.get_attribute("href")
                product_id = link.split("/")[-1]
            except:
                continue

            try:
                name = item.find_element(By.CSS_SELECTOR, "div.product-item__name").text
            except NoSuchElementException:
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
        for category_url in CATEGORY_URLS:
            products = fetch_products(category_url)
            print(f"Found {len(products)} products in this category.")

            for p in products:
                if p['id'] not in posted_products and p['price'] <= PRICE_THRESHOLD:
                    send_alert(p)
                    posted_products.add(p['id'])
                    time.sleep(2)

        time.sleep(60)  # check every 60 seconds
    except Exception as e:
        print("Main Loop Error:", e)
        time.sleep(30)
