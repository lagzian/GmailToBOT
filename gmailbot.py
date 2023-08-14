import asyncio
import imaplib
import email
import os
from telegram import Bot, ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from bs4 import BeautifulSoup
from email.header import decode_header

# Define a callback function to handle messages
def message_handler(update: Update, context: CallbackContext) -> None:
    user_response = update.message.text.lower()

    # If the user responds with 'delete', mark the email for deletion
    if user_response == 'delete':
        email_id = context.user_data.get('email_id')
        if email_id is not None:
            mail.store(email_id, '+FLAGS', '(\\Deleted)')
            context.user_data['email_id'] = None
            update.message.reply_text('Email marked for deletion.')
        else:
            update.message.reply_text('No email to delete.')

async def fetch_emails_and_send_telegram():

    # Get the Telegram bot token from GitHub secret
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']

    # Initialize the bot
    bot = Bot(token=bot_token)

    # Get the Telegram chat ID from GitHub secret
    chat_id = os.environ['TELEGRAM_CHAT_ID']

    # Get the Gmail username from GitHub secret
    gmail_username = os.environ['GMAIL_USERNAME']

    # Get the Gmail app password from GitHub secret
    gmail_app_password = os.environ['GMAIL_APP_PASSWORD']

    # Connect to Gmail IMAP server
    mail = imaplib.IMAP4_SSL('imap.gmail.com')

    # Login to the account
    mail.login(gmail_username, gmail_app_password)

    # Select the mailbox (e.g., 'INBOX')
    mailbox = 'INBOX'
    mail.select(mailbox)

    # Search for new emails
    _, data = mail.search(None, 'UNSEEN')

    # Fetch the email IDs
    email_ids = data[0].split()

    # Set up the Telegram updater with the message handler
    updater = Updater(token=bot_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

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

        # Extract the desired information from the email body
        body = ''
        if email_message.is_multipart():
            for part in email_message.get_payload():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    charset = part.get_content_charset()
                    body = part.get_payload(decode=True)
                    if charset:
                        body = body.decode(charset)
                    else:
                        body = body.decode('utf-8', 'ignore')
                    break
                elif content_type == 'text/html':
                    body = part.get_payload(decode=True)
                    soup = BeautifulSoup(body, 'lxml')
                    body = soup.get_text()
                    break

        # Add "📧NEW EMAIL📧" header to the message
        header = "🔔📧📭NEW EMAIL📭📧🔔"
        message = f"{header}\nSubject: {subject}\nFrom: {sender}\n\n{body}"

        # Truncate the message if it exceeds the limit
        if len(message) > 4096:
            message = message[:4093] + "..."

        # Send the message to Telegram with a delete button
        button = KeyboardButton('Delete')

        # Pass the keyboard in ReplyKeyboardMarkup
        reply_markup = ReplyKeyboardMarkup(keyboard=[[button]], one_time_keyboard=True)

        # Send the message and store the email ID for later deletion
        sent_message = bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
        context = sent_message.reply_text
        context.user_data['email_id'] = email_id

        # Wait for a response
        await asyncio.sleep(60)  # Adjust the waiting time as needed

    # Logout and close the connection
    mail.expunge()
    mail.logout()

    # Stop the updater
    updater.stop()

if __name__ == '__main__':
    asyncio.run(fetch_emails_and_send_telegram())
