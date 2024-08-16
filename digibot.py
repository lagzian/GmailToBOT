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
    # Set the path to your Chromedriver executable
    chrome_driver_path = os.getenv('CHROME_DRIVER_PATH')

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode (without GUI)

    # Create a new Chrome WebDriver
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Fetch website content
        driver.get(url)

        # Scroll down the page multiple times to load all content
        for _ in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(10)

        # Get the page source
        page_source = driver.page_source

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Get the entire text content
        text = soup.get_text()

        return text

    finally:
        # Close the browser
        driver.quit()

async def send_to_telegram(message):
    # Get the Telegram bot token from GitHub secret
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']

    # Initialize the bot
    bot = Bot(token=bot_token)

    # Get the Telegram chat ID from GitHub secret
    chat_id = os.environ['TELEGRAM_CHAT_ID']

    # Send the message to Telegram
    await bot.send_message(chat_id=chat_id, text=message)

async def main():
    # Set the website URL
    url = "https://www.digikala.com/search/category-drill/ronix/?attributes%5B1027%5D%5B0%5D=3373&sort=20"

    # Fetch the webpage content
    webpage_content = await fetch_webpage_content(url)

    # Define the desired pattern
    pattern = r"\d{3},\d{3},\d{3}"

    # Find all matches in the webpage content
    matches = re.findall(pattern, webpage_content)

    # Remove matches equal to "۱۰۰,۰۰۰,۰۰۰"
    matches = [match for match in matches if match != "۱۰۰,۰۰۰,۰۰۰"]

    # Modify matches: Remove the first digit if it's greater than 1
    modified_matches = []
    for match in matches:
        first_digit = int(match[0])
        if first_digit > 1:
            match = match[1:]
        modified_matches.append(match)

    # Compose the message
    message = f"📌💥Found {len(modified_matches)} relevant ronix_drill Price💥📌.\n{'\n'.join(modified_matches)}"

    # Send the message to Telegram
    await send_to_telegram(message)

# Run the main function in an asynchronous event loop
asyncio.run(main())
