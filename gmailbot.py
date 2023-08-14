import asyncio
import imaplib
import email
import os

from telegram import Bot, ReplyKeyboardMarkup, KeyboardButton
from bs4 import BeautifulSoup
from email.header import decode_header

async def fetch_emails_and_send_telegram(delete_emails=False):

  # Get Telegram bot token
  bot_token = os.environ['TELEGRAM_BOT_TOKEN']

  # Initialize Telegram bot
  bot = Bot(token=bot_token)

  # Get Telegram chat ID
  chat_id = os.environ['TELEGRAM_CHAT_ID']

  # Get Gmail username
  gmail_username = os.environ['GMAIL_USERNAME']

  # Get Gmail app password
  gmail_app_password = os.environ['GMAIL_APP_PASSWORD']

  # Connect to Gmail
  mail = imaplib.IMAP4_SSL('imap.gmail.com')
  mail.login(gmail_username, gmail_app_password)

  # Select inbox
  mailbox = 'INBOX'
  mail.select(mailbox)

  # Search for unseen emails
  _, data = mail.search(None, 'UNSEEN')
  email_ids = data[0].split()

  # Process each email
  for email_id in email_ids:
    _, msg_data = mail.fetch(email_id, '(RFC822)')
    raw_email = msg_data[0][1]
    email_msg = email.message_from_bytes(raw_email)

    # Decode headers
    subject = decode_header(email_msg['Subject'])[0][0]
    if isinstance(subject, bytes):
      subject = subject.decode()
    sender = decode_header(email_msg['From'])[0][0]
    if isinstance(sender, bytes):
      sender = sender.decode()

    # Extract body content
    body = ''
    if email_msg.is_multipart():
      for part in email_msg.get_payload():
        if part.get_content_type() == 'text/plain':
          charset = part.get_content_charset()
          body = part.get_payload(decode=True)
          if charset:
            body = body.decode(charset)
          else:
            body = body.decode('utf-8', 'ignore')
          break
        elif part.get_content_type() == 'text/html':
          body = part.get_payload(decode=True)
          soup = BeautifulSoup(body, 'lxml')
          body = soup.get_text()
          break

    # Create Telegram message
    header = "🔔📧📭NEW EMAIL📭📧🔔"
    msg = f"{header}\nSubject: {subject}\nFrom: {sender}\n\n{body}"
    if len(msg) > 4096:
      msg = msg[:4093] + "..."
    
    # Send message to Telegram
    button = KeyboardButton('Delete')
    reply_markup = ReplyKeyboardMarkup([[button]], one_time_keyboard=True)
    await bot.send_message(chat_id, text=msg, reply_markup=reply_markup)

  # Only delete emails if specified
  if delete_emails:
    mail.store(email_id, '+FLAGS', '(\\Deleted)')

def delete_handler(update, context):
  delete_emails = True
  asyncio.run(fetch_emails_and_send_telegram(delete_emails))

def main():
  bot_token = os.environ['TELEGRAM_BOT_TOKEN']
  bot = Bot(token=bot_token)

  bot.message_handler(delete_handler)

  asyncio.run(fetch_emails_and_send_telegram())

if __name__ == '__main__':
  main()
