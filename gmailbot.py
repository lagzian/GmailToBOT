import asyncio
import imaplib
import email
import os
from telegram import Bot
import html2text

async def fetch_emails_and_send_telegram():
    # Get the Telegram bot token from GitHub secret
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']

    # Initialize the bot
    bot = Bot(token=bot_token)

    # Get the Telegram chat ID from GitHub secret
    chat_id = os.environ['TELEGRAM_CHAT_ID']

    # Gmail account details
    username = 'milad.lagzian@gmail.com'
    password = os.environ['GMAIL_APP_PASSWORD']

    # Connect to Gmail IMAP server
    mail = imaplib.IMAP4_SSL('imap.gmail.com')

    # Login to the account
    mail.login(username, password)

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

        # Extract the desired information from the email
        subject = email_message['Subject']
        sender = email_message['From']
        body = ''

        if email_message.is_multipart():
            for part in email_message.get_payload():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload()
                    break
                elif part.get_content_type() == 'text/html':
                    html_body = part.get_payload()
                    h = html2text.HTML2Text()
                    body = h.handle(html_body)
                    break
        else:
            body = email_message.get_payload()

        # Truncate the message if it exceeds the limit
        message = f"Subject: {subject}\nFrom: {sender}\n\n{body}"
        if len(message) > 4096:
            message = message[:4093] + "..."

        # Send the message to Telegram
        await bot.send_message(chat_id=chat_id, text=message)

    # Logout and close the connection
    mail.logout()

# Run the function in an asynchronous event loop
asyncio.run(fetch_emails_and_send_telegram())
