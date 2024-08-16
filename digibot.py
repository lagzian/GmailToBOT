import asyncio
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
from telegram import Bot

async def fetch_webpage_content(url):
    chrome_driver_path = os.getenv('CHROME_DRIVER_PATH')

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)

        for _ in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            await asyncio.sleep(10)  # Use asyncio.sleep instead of time.sleep

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        text = soup.get_text()

        return text

    finally:
        driver.quit()

async def send_to_telegram(message):
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']
    bot = Bot(token=bot_token)
    chat_id = os.environ['TELEGRAM_CHAT_ID']

    # Send message without await if bot.send_message is not async
    bot.send_message(chat_id=chat_id, text=message)

async def main():
    url = "https://www.digikala.com/search/category-drill/ronix/?attributes%5B1027%5D%5B0%5D=3373&has_selling_stock=1&sort=20"

    webpage_content = await fetch_webpage_content(url)

    pattern = r"\d{1},\d{3},\d{3}"
    matches = re.findall(pattern, webpage_content)

    matches = [match for match in matches if match != "۱۰۰,۰۰۰,۰۰۰"]

    message = f"📌💥Found {len(matches)} relevant ronix_drill Price💥📌.\n{'\n'.join(matches)}"

    await send_to_telegram(message)

asyncio.run(main())
