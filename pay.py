import os
import logging
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from datetime import datetime

# API credentials (Use environment variables for security)
API_ID = int(os.getenv("API_ID", 22627280))
API_HASH = os.getenv("API_HASH", "b2e5eb5e3dd886f5b8be6a749a26f619")
SESSION_STRING = os.getenv("SESSION_STRING")  # Use session string to avoid OTP issue
OWNER_ID = int(os.getenv("OWNER_ID", 1240179115))  # Admin ID

# Initialize Telegram client with session string
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Configuration
channel_link = "https://t.me/+lgb92RXeI2E4ZjM1"
price_list_link = "https://t.me/c/2147999578/8855"
qr_code_path = 'payment.jpg'
upi_id = "your_upi_id@upi"  # Replace with actual UPI ID
gif_path = '0.gif'
cooldown_period = 600  # 10 minutes
last_qr_request = {}
help_message = """
🤖 **Available Commands:**

- **`qr`**, **`upi`** → Get the QR code and UPI ID for payment
- **`free`** → **🖕🏻 FREE ME TO LODA MILEGA! 🖕🏻**
- **`channel`**, **`channel link`**, **`link`** → Get the channel link
- **`price`** → Get the price list link
- **`help`** → Show this help message
- **`/id`** → Get your own Telegram ID
- **`/id @username`** (Admin Only) → Get user ID of a specific user
- **`admin`** → Get Admin Contact
"""

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    try:
        user_id = event.sender_id
        message_text = event.raw_text.lower()
        
        # Handle QR & UPI requests with cooldown
        if any(word in message_text for word in ['qr', 'upi']):
            now = datetime.now()
            if user_id in last_qr_request and (now - last_qr_request[user_id]).total_seconds() < cooldown_period:
                await event.reply("🖕🏻 **BSDK RUK JA 10 Min USKE BAAD MILEGA QR.** 🖕🏻")
                return
            
            await client.send_file(
                event.chat_id, qr_code_path,
                caption=f"**Here is my QR code for payment.**\n\n💳 **UPI ID:** `{upi_id}`\n\n🔗 {channel_link}\n\n📸 **Please send a screenshot of your payment as confirmation.**",
                force_document=False, allow_cache=True
            )
            last_qr_request[user_id] = now
        
        # Free message response
        elif 'free' in message_text:
            await event.reply("🖕🏻 **FREE ME TO LODA MILEGA!** 🖕🏻")
        
        # Channel link response
        elif any(word in message_text for word in ['channel', 'channel link', 'link']):
            await event.reply(f"**My channel link:** {channel_link}")
        
        # Price list response
        elif 'price' in message_text:
            await event.reply(f"🛒 **Here is our price list:** {price_list_link}")
        
        # Help command
        elif 'help' in message_text:
            await event.reply(help_message)
        
        # Send GIF to new users
        elif message_text in ['hi', 'hello', 'hlw', 'hii', 'hey']:
            await client.send_file(event.chat_id, gif_path, caption="**Welcome!**", force_document=False, allow_cache=True)
        
        # ID command
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
                    logging.error(f"Error fetching user ID: {e}")
            elif user_id != OWNER_ID:
                await event.reply("❌ **You are not authorized to check other users' IDs!**")

        # Admin contact
        elif 'admin' in message_text:
            await event.reply(f"👨‍💻 **Admin Contact:** [Click Here](tg://user?id={OWNER_ID})")

    except Exception as e:
        logging.error(f"Error handling message: {e}")

# Start the client
client.start()
logging.info("Client is running...")
client.run_until_disconnected()
