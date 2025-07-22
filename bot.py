import os
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from selenium import webdriver
from selenium.webdriver.common.by import By

TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли мне код товара с бирки (например, 318GF-10X), и я найду товар на reserved.com 😊")

def find_item(code):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    search_url = f"https://www.reserved.com/ua/uk/search?q={code}"
    driver.get(search_url)
    time.sleep(3)

    try:
        first_item = driver.find_element(By.CSS_SELECTOR, '.products-list .product-grid-item a')
        first_item.click()
        time.sleep(2)

        title = driver.find_element(By.CSS_SELECTOR, 'h1.product-name').text
        img_url = driver.find_element(By.CSS_SELECTOR, '.product-gallery__media img').get_attribute('src')
        product_url = driver.current_url

        driver.quit()
        return title, img_url, product_url
    except:
        driver.quit()
        return None, None, None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    await update.message.reply_text(f"Ищу товар по коду: {code}...")

    title, img, link = find_item(code)
    if title:
        caption = f"{title}\n{link}"
        await update.message.reply_photo(photo=img, caption=caption)
    else:
        await update.message.reply_text("❌ Товар не найден. Проверь код ещё раз.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
