import asyncio
import imaplib
import email
import os
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler
from bs4 import BeautifulSoup
from email.header import decode_header

# Gmail account details
username = 'milad.lagzian@gmail.com'
password = os.environ['GMAIL_APP_PASSWORD']

# Connect to Gmail IMAP server
mail = imaplib.IMAP4_SSL('imap.gmail.com')

# Login to the account
mail.login(username, password)

# Callback function to handle the delete action
def handle_delete_action(update, context):
    query = update.callback_query
    email_id = query.data

    # Delete the email from the server
    mail.store(email_id, '+FLAGS', '\\Deleted')
    mail.expunge()

    # Send a confirmation message
    query.answer(text='Email deleted successfully.')

# Function to fetch emails and send to Telegram
async def fetch_emails_and_send_telegram():
    # Get the Telegram bot token from GitHub secret
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']

    # Initialize the bot
    bot = Bot(token=bot_token)

    # Get the Telegram chat ID from GitHub secret
    chat_id = os.environ['TELEGRAM_CHAT_ID']

    # Select the mailbox (e.g., 'INBOX')
    mailbox = 'INBOX'
    mail.select(mailbox)

    # Search for new emails
    _, data = mail.search(None, 'UNSEEN')

    # Fetch the email IDs
    email_ids = data[0].split()

    # Process each email
    for email_id in email_ids:
        _, msg_data = mail.fetch(email_id, '(RFC822)')

        # Parse the email message
        raw_email = msg_data[0][1]
        email_message = email.message_from_bytes(raw_email)

        # Decode subject and sender headers
        subject = decode_header(email_message['Subject'])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode('utf-8')
        
        sender = decode_header(email_message['From'])[0][0]
        if isinstance(sender, bytes):
            sender = sender.decode('utf-8')

        # Extract the desired information from the email
        body = ''

        if email_message.is_multipart():
            for part in email_message.get_payload():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload()
                    break
        else:
            body = email_message.get_payload()

        # Remove HTML tags from the body if it contains HTML
        soup = BeautifulSoup(body, 'lxml')
        plain_text_body = soup.get_text()

        # Truncate the message if it exceeds the limit
        message = f"Subject: {subject}\nFrom: {sender}\n\n{plain_text_body}"
        if len(message) > 4096:
            message = message[:4093] + "..."

        # Create inline keyboard with delete button
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Delete', callback_data=email_id.decode())]])

        # Send the message with inline keyboard to Telegram
        await bot.send_message(chat_id=chat_id, text=message, reply_markup=keyboard)

    # Logout and close the connection
    mail.logout()

# Run the function in an asynchronous event loop
asyncio.run(fetch_emails_and_send_telegram())

# Set up the Telegram bot and add the delete action handler
updater = Updater(token=os.environ['TELEGRAM_BOT_TOKEN'], use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CallbackQueryHandler(handle_delete_action))

# Start the bot
updater.start_polling()
updater.idle()
