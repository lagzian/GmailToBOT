import asyncio
import imaplib
import email
import os
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from bs4 import BeautifulSoup
from email.header import decode_header

async def fetch_emails_and_send_telegram():

  # Get bot token
  bot_token = os.environ['TELEGRAM_BOT_TOKEN']
  
  # Initialize bot
  bot = Bot(token=bot_token)

  # Get chat ID
  chat_id = os.environ['TELEGRAM_CHAT_ID']

  # Connect to Gmail
  mail = imaplib.IMAP4_SSL('imap.gmail.com')
  mail.login(os.environ['GMAIL_USERNAME'], os.environ['GMAIL_APP_PASSWORD'])

  # Select inbox
  mail.select('INBOX')

  # Search for unseen emails
  _, data = mail.search(None, 'UNSEEN')
  email_ids = data[0].split()

  # Process each email
  for email_id in email_ids:

    # Fetch email data
    _, msg_data = mail.fetch(email_id, '(RFC822)')
    raw_email = msg_data[0][1]
    email_msg = email.message_from_bytes(raw_email)

    # Parse headers
    subject = decode_header(email_msg['Subject'])[0][0]
    subject = subject if isinstance(subject, str) else subject.decode()
    sender = decode_header(email_msg['From'])[0][0]
    sender = sender if isinstance(sender, str) else sender.decode()

    # Parse body
    body = ''
    if email_msg.is_multipart():
      for part in email_msg.get_payload():
        if part.get_content_type() == 'text/plain':
          body = part.get_payload(decode=True)
          body = body.decode() if type(body) == bytes else body  
          break

    # Create message 
    header = "🔔📧📭NEW EMAIL📭📧🔔"
    msg_text = f"{header}\nSubject: {subject}\nFrom: {sender}\n\n{body}"
    if len(msg_text) > 4096:
      msg_text = msg_text[:4093] + "..."
    
    # Send Email Message
    await bot.send_message(chat_id=chat_id, text=msg_text)

    # Create Inline Keyboard
    button = InlineKeyboardButton(text='Delete', callback_data='delete')
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[button]])

    # Send Inline Keyboard
    await bot.send_message(chat_id=chat_id, text='', reply_markup=reply_markup)

    # Delete email
    mail.store(email_id , '+FLAGS', '\\Deleted') 

if __name__ == '__main__':
  
  asyncio.run(fetch_emails_and_send_telegram())
