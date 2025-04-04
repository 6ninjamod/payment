import os
import re
import json
import logging
import asyncio
import subprocess
from telethon import TelegramClient, events
from datetime import datetime

# API credentials (Replace with your actual API ID & Hash)
API_ID = 22627280  
API_HASH = "b2e5eb5e3dd886f5b8be6a749a26f619"  
OWNER_ID = 1240179115  # Owner Telegram ID

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Telegram client
client = TelegramClient('session_name', API_ID, API_HASH)

# Configuration
channel_link = "https://t.me/+lgb92RXeI2E4ZjM1"
price_list_link = "https://t.me/c/2147999578/8855"
upload_qr_code = 'payment.jpg'
gif_path = 'hello.gif'
upi_id = "ninjagamerop0786@ybl"  # Replace with your actual UPI ID
cooldown_period = 600  # 10 minutes
last_qr_request = {}

help_message = """
🤖 **Available Commands:**

- **`qr`** → Get the QR code for payment
- **`upi`** → Get QR + UPI ID together
- **`price`** → Get the price list link
- **`/id`** → Get your own Telegram ID
- **`/id @username`** (Owner Only) → Get user ID of a specific user
- **`free`** → Get a response with GIF
"""

# Function to check latest SMS using Termux API
def get_latest_sms():
    try:
        result = subprocess.run(["termux-sms-list"], capture_output=True, text=True)
        sms_list = json.loads(result.stdout)
        if sms_list:
            return sms_list[0]  # Get the latest SMS
    except Exception as e:
        logger.error(f"Error reading SMS: {e}")
    return None

# Function to extract UPI payment details
def extract_payment_details(sms_body):
    upi_pattern = r"(?i)(?:received|credited)\s+₹?(\d+(\.\d{1,2})?)\s+from\s+([a-zA-Z\s]+)"
    match = re.search(upi_pattern, sms_body)
    if match:
        amount = match.group(1)
        sender = match.group(3).strip()
        return amount, sender
    return None, None

# Background task to check SMS every 30 seconds
async def check_sms():
    last_checked = None
    while True:
        sms = get_latest_sms()
        if sms and sms['body'] != last_checked:
            last_checked = sms['body']
            amount, sender = extract_payment_details(sms['body'])
            if amount and sender:
                message = f"✅ **Payment Received!**\n💰 **Amount:** ₹{amount}\n👤 **Sender:** {sender}"
                await client.send_message(OWNER_ID, message)
        await asyncio.sleep(30)  # 30 seconds delay

# Handle commands
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    try:
        user_id = event.sender_id
        message_text = event.raw_text.lower()
        
        if message_text in ['qr', 'upi', 'scanner']:
            now = datetime.now()
            if user_id in last_qr_request and (now - last_qr_request[user_id]).total_seconds() < cooldown_period:
                await event.reply("🖕🏻 **BSDK RUK JA 10 Min USKE BAAD MILEGA QR.** 🖕🏻")
                return
            await client.send_file(event.chat_id, upload_qr_code, caption=f"**Here is my QR code for payment.**\n\n💳 UPI ID: `{upi_id}`\n\n📢 Join our channel: {channel_link}\n\n📸 **Please Send a Screenshot of Payment**", force_document=False, allow_cache=True)
            last_qr_request[user_id] = now
            asyncio.create_task(check_sms())
        
        elif 'price' in message_text:
            await event.reply(f"🛒 **Here is our price list:** {price_list_link}")
        
        elif 'help' in message_text:
            await event.reply(help_message)
        
        elif message_text.startswith('/id'):
            parts = message_text.split()
            if len(parts) == 1:
                await event.reply(f"**Your Telegram ID:** `{user_id}`")
            elif len(parts) > 1 and user_id == OWNER_ID:
                try:
                    username = parts[1]
                    entity = await client.get_entity(username)
                    await event.reply(f"**User ID of {username}:** `{entity.id}`")
                except Exception as e:
                    await event.reply("❌ **User not found!**")
                    logger.error(f"Error fetching user ID: {e}")
            elif user_id != OWNER_ID:
                await event.reply("❌ **You are not authorized to check other users' IDs!**")
        
        elif message_text in ['hi', 'hello', 'hey', 'hii', 'hlw']:
            await client.send_file(event.chat_id, gif_path, caption="👋 Hello! How can I assist you?", force_document=False, allow_cache=True)

        elif 'free' in message_text:
            await event.reply("🖕🏻 **FREE ME TO LODA MILEGA!** 🖕🏻")
    
    except Exception as e:
        logger.error(f"Error handling message: {e}")

# Start the Telegram Client
client.start()
logger.info("Bot is running...")
client.run_until_disconnected()
