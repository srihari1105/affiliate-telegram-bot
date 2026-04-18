import requests
from bs4 import BeautifulSoup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(url, headers=headers, allow_redirects=True)
        final_url = url

        soup = BeautifulSoup(r.content, "html.parser")

        # TITLE
        title = soup.find("span", {"id": "productTitle"})
        if title:
            title = title.get_text().strip()
        else:
            title = "🔥 Hot Deal Product"

        # PRICE (multiple attempts)
        price = "N/A"

        selectors = [
            ("span", {"class": "a-price-whole"}),
            ("span", {"class": "a-offscreen"}),
        ]

        for tag, attrs in selectors:
            price_tag = soup.find(tag, attrs)
            if price_tag:
                price = price_tag.get_text().strip().replace("₹", "")
                break

        # IMAGE (fallbacks)
        image = None

        img = soup.find("img", {"id": "landingImage"})
        if img and img.get("src"):
            image = img["src"]

        return title, price, image, final_url

    except Exception as e:
        print("Error:", e)
        return "🔥 Hot Deal", "Check Below 👇", None, url
    
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

    if not update.message or not update.message.text:
        return

    url = update.message.text

    if not url.startswith("http"):
        return

    print("Received:", url)
    print("All chat IDs:", chat_ids)

    title, price, image, final_url = get_product_details(url)

    # fallback title
    if not title or title == "No title":
        title = "🔥 New Deal Alert"

    # price text
    if price == "N/A":
        price_text = "💰Price: ₹_________________ 👇"
    else:
        price_text = f"💰 Price: ₹{price}"

    # ❌ removed markdown symbols (*)
    message = f"""
🔥 DEALS BABAI SPECIAL 🔥

🛍️ Product Name:
{title}

{price_text}

👉 Buy Now: {final_url}

━━━━━━━━━━━━━━━
"""

    for chat_id in chat_ids:
        try:
            if image:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=image,
                    caption=message
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message
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