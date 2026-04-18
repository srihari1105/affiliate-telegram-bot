import requests
from bs4 import BeautifulSoup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import json

TOKEN = "8612219346:AAH6qjg-mK976Ow0NKAUYQe6mwMml98VK9Y"  # ⚠️ change this


# ------------------------------
# LOAD & SAVE CHAT IDS (PERMANENT)
# ------------------------------

def load_chat_ids():
    try:
        with open("chat_ids.json", "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_chat_ids():
    with open("chat_ids.json", "w") as f:
        json.dump(list(chat_ids), f)

chat_ids = load_chat_ids()

                # ------------------------------
                # LOAD & SAVE channel IDS (Manual)
                # -----------------------------

chat_ids.add(-1003929191388)  # paste your channel ID here

# ------------------------------
# SCRAPE PRODUCT DETAILS
# ------------------------------

def get_product_details(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    try:
        title = soup.find(id="productTitle").get_text().strip()
    except:
        title = "No title"

    try:
        price = soup.find("span", {"class": "a-price-whole"}).get_text()
    except:
        price = "N/A"

    return title, price

# ------------------------------
# SAVE CHAT IDs (GROUP / CHANNEL / PRIVATE)
# ------------------------------

async def save_chat(update, context):
    chat_id = update.effective_chat.id

    if chat_id not in chat_ids:
        chat_ids.add(chat_id)
        save_chat_ids()
        print("Saved chat:", chat_id)

# ------------------------------
# HANDLE MESSAGES (MAIN LOGIC)
# ------------------------------

async def handle_message(update, context: ContextTypes.DEFAULT_TYPE):

    # ONLY accept messages from bot/private/group (not channel)
    if not update.message or not update.message.text:
        return

    url = update.message.text

    if not url.startswith("http"):
        return

    print("Received:", url)
    print("All chat IDs:", chat_ids)

    title, price = get_product_details(url)

    message = f"""
🔥 *DEALS BABAI SPECIAL* 🔥

🛍️ *{title}*

💰 *Deal Price:* ₹{price}  
🚀 *Hurry! Limited Time Offer*

━━━━━━━━━━━━━━━
👉 [🛒 Buy Now]({url})
━━━━━━━━━━━━━━━

💥 Best Deal Alert ⚡
"""


    for chat_id in chat_ids:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Failed to send to {chat_id}:", e)

# ------------------------------
# RUN BOT
# ------------------------------

app = ApplicationBuilder().token(TOKEN).build()

# handle normal messages (bot/private/group)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 🔥 handle channel posts (correct way)
app.add_handler(MessageHandler(filters.ChatType.CHANNEL, save_chat))

print("Bot running... 🚀")
from telegram import Update

app.run_polling(allowed_updates=Update.ALL_TYPES)