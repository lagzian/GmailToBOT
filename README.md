# Gmail Bot for Telegram

This repository contains a Python script that fetches new emails from a Gmail account using the IMAP protocol and sends them to a Telegram bot. The script is intended to be run periodically, and it utilizes GitHub Actions workflow for automation.

## Features

- Fetches new emails from a Gmail account using IMAP.
- Extracts email subject, sender, and body.
- Sends the email information to a Telegram bot.
- Supports plain text and HTML email bodies.
- Formats the message in Telegram with bold header for new emails.

## Requirements

- Python 3.x
- Gmail account with IMAP enabled
- Telegram bot token and chat ID
- GitHub repository secrets for Gmail credentials and Telegram bot token

## Installation

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/your-username/GmailToBOT.git
   ```

2. Install the required Python dependencies:

   ```bash
   cd GmailToBOT
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the repository root and add the following environment variables:

   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_telegram_chat_id
   GMAIL_USERNAME=your_gmail_username
   GMAIL_APP_PASSWORD=your_gmail_app_password
   ```

   Replace `your_telegram_bot_token`, `your_telegram_chat_id`, `your_gmail_username`, and `your_gmail_app_password` with your actual credentials.

   Note: For security, it's recommended to use GitHub repository secrets to store sensitive information like the bot token and app password.

4. Run the Python script manually:

   ```bash
   python gmailbot.py
   ```

   The script will fetch new emails from your Gmail account and send them to your Telegram bot.

## GitHub Actions Workflow

This repository includes a GitHub Actions workflow to automate the email fetching process. The workflow is configured to run every 5 minutes using the `cron` expression.

To set up the GitHub Actions workflow:

1. Create the necessary repository secrets in your GitHub repository settings:

   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token.
   - `TELEGRAM_CHAT_ID`: Your Telegram chat ID.
   - `GMAIL_USERNAME`: Your Gmail account username.
   - `GMAIL_APP_PASSWORD`: Your Gmail app password (or regular password if not using app passwords).

2. Commit the changes to the repository, and the GitHub Actions workflow will be triggered automatically every 5 minutes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This script fetches emails from a Gmail account and sends them to a Telegram bot. Make sure to use it responsibly and follow the terms of service for both Gmail and Telegram platforms. The script is provided as-is without any warranty. Use it at your own risk.
