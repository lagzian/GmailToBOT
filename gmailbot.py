import asyncio
import imaplib
import email
import os

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup 
from telegram.ext import CallbackQueryHandler
from bs4 import BeautifulSoup
from email.header import decode_header

async def fetch_emails_and_send_telegram():

  # Get Telegram bot token
  bot_token = os.environ['TELEGRAM_BOT_TOKEN']
  
  # Initialize Telegram bot
  bot = Bot(token=bot_token)

  # Get Telegram chat ID
  chat_id = os.environ['TELEGRAM_CHAT_ID']

  # Gmail credentials
  username = 'your_gmail@gmail.com'
  password = os.environ['GMAIL_APP_PASSWORD']

  # Connect to Gmail
  mail = imaplib.IMAP4_SSL('imap.gmail.com')
  mail.login(username, password)

  # Select inbox
  mail.select('INBOX')

  _, search_data = mail.search(None, 'UNSEEN')
  email_ids = search_data[0].split()

  for email_id in email_ids:
    _, msg_data = mail.fetch(email_id, '(RFC822)')
    raw_email = msg_data[0][1]
    
    # Parse email
    email_msg = email.message_from_bytes(raw_email)

    # Process email fields
    subject = decode_header(email_msg['Subject'])[0][0]
    sender = decode_header(email_msg['From'])[0][0]
    body = get_email_body(email_msg)
    
    # Build Telegram message
    message = build_telegram_message(subject, sender, body, email_id)
    
    # Send message with delete button
    sent_msg = await bot.send_message(chat_id=chat_id, text=message, reply_markup=build_keyboard(email_id))

  mail.logout()

def get_email_body(email_msg):
  # Logic to extract plain text body
  
def build_telegram_message(subject, sender, body, email_id):
  # Logic to build message string

def build_keyboard(email_id):
  keyboard = [[InlineKeyboardButton("Delete", callback_data=email_id)]]
  return InlineKeyboardMarkup(keyboard) 

async def delete_email(update, context):
  query = update.callback_query
  email_id = query.data
  
  # Delete email on server
  mail.store(email_id , '+FLAGS', '\\Deleted') 
  
  await query.answer()
  await query.edit_message_reply_markup(reply_markup=None)

if __name__ == '__main__':

  # Add callback handler
  dp.add_handler(CallbackQueryHandler(delete_email))

  # Run main function
  asyncio.run(fetch_emails_and_send_telegram())
