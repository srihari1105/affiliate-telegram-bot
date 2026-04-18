import requests
from bs4 import BeautifulSoup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler
import os

TOKEN = os.getenv("TOKEN")

# ------------------------------
# load + save functions
# ------------------------------

def load_allowed_users():
    try:
        with open("allowed_users.json", "r") as f:
            return set(json.load(f))
    except:
        return set()
    


def save_allowed_users():
    with open("allowed_users.json", "w") as f:
        json.dump(list(ALLOWED_USERS), f)
        
#------------------------------
#initialize users
#------------------------------

ALLOWED_USERS = set(load_allowed_users())

# first time empty unte nee ID add cheyyi
if not ALLOWED_USERS:
    ALLOWED_USERS.add(1825323355)  # owner telegram id
    save_allowed_users()
    
# ------------------------------
# auth check
# ------------------------------

def is_owner(user_id):
    return user_id==OWNER_ID

def is_allowed(user_id):
    return user_id in ALLOWED_USERS or user_id == OWNER_ID

#-------------------------------
#owner system
#-------------------------------
OWNER_ID = 1825323355  # owner telegram id

    
#-------------------------------
# add_user 
#-------------------------------

async def add_user(update, context):

    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Only owner can add users")
        return

    if not context.args:
        await update.message.reply_text("Usage:\n/add_user <user_id>")
        return

    new_user = int(context.args[0])

    ALLOWED_USERS.add(new_user)
    save_allowed_users()

    await update.message.reply_text(f"✅ Added user: {new_user}")
    
#-------------------------------
# remove user 
#-------------------------------

async def remove_user(update, context):

    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Only owner can remove users")
        return

    if not context.args:
        return

    rem_user = int(context.args[0])

    if rem_user in ALLOWED_USERS:
        ALLOWED_USERS.remove(rem_user)
        save_allowed_users()
        await update.message.reply_text(f"❌ Removed user: {rem_user}")


#------------------------------
#ADD CHANNEL/GROUP
#------------------------------

async def add_chat(update, context):

    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Only owner can add chat")
        return

    if not context.args:
        await update.message.reply_text("Usage:\n/add_chat <chat_id>")
        return

    chat_id = int(context.args[0])

    chat_ids.add(chat_id)
    save_chat_ids()

    await update.message.reply_text(f"✅ Added chat: {chat_id}")
    

#------------------------------
#remove chat
#------------------------------

async def remove_chat(update, context):

    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Only owner can remove chat")
        return

    if not context.args:
        await update.message.reply_text("Usage:\n/remove_chat <chat_id>")
        return

    chat_id = int(context.args[0])

    if chat_id in chat_ids:
        chat_ids.remove(chat_id)
        save_chat_ids()

    await update.message.reply_text(f"❌ Removed chat: {chat_id}")


# ------------------------------
# START command
# ------------------------------



async def start(update, context):
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open("bot-image.jpeg", "rb"),
        caption="""👋 Welcome to Deals Babai Bot!
Mee Budget ki Best Friend 😊🤝💥

Use MENU to see commands

Instagram:
https://www.instagram.com/dealsbabai.official

Youtube:
https://youtube.com/@dealsbabaiofficial

Telegram channel:
https://t.me/dealsbabaiofficial

Whatsapp channel:
https://whatsapp.com/channel/0029Vb7xOWKKWEKoN0Pd5z1I
"""
    )



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

# # ------------------------------
# # HANDLE MESSAGES (MAIN LOGIC)
# # ------------------------------

# async def handle_message(update, context: ContextTypes.DEFAULT_TYPE):

#     if not update.message or not update.message.text:
#         return

#     url = update.message.text

#     if not url.startswith("http"):
#         return

#     print("Received:", url)
#     print("All chat IDs:", chat_ids)

#     title, price, image, final_url = get_product_details(url)

#     # fallback title
#     if not title or title == "No title":
#         title = "🔥 New Deal Alert"

#     # price text
#     if price == "N/A":
#         price_text = "💰Price: ₹_________________ 👇"
#     else:
#         price_text = f"💰 Price: ₹{price}"

#     # ❌ removed markdown symbols (*)
#     message = f"""
# 🔥 DEALS BABAI SPECIAL 🔥

# 🛍️ Product Name:
# {title}

# {price_text}

# 👉 Buy Now: {final_url}

# ━━━━━━━━━━━━━━━
# """

#     for chat_id in chat_ids:
#         try:
#             if image:
#                 await context.bot.send_photo(
#                     chat_id=chat_id,
#                     photo=image,
#                     caption=message
#                 )
#             else:
#                 await context.bot.send_message(
#                     chat_id=chat_id,
#                     text=message
#                 )
#         except Exception as e:
#             print(f"Failed to send to {chat_id}:", e)
            
            
# ------------------------------
# generate post 
# ------------------------------        
            
async def generate_post(update, context: ContextTypes.DEFAULT_TYPE):
    
    user_id = update.effective_user.id

    if not is_allowed(user_id):
        await update.message.reply_text("❌ You are not authorized")
        return

    if not context.args:
        await update.message.reply_text("Send link like:\n/generate_post <link>")
        return

    url = context.args[0]

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
# generate post func
# ------------------------------

async def generate_message(update, context):

    user_id = update.effective_user.id

    if not is_allowed(user_id):
        await update.message.reply_text("❌ You are not authorized")
        return

    # 🔥 FULL TEXT CAPTURE FIX
    text = update.message.text

    if " " not in text:
        await update.message.reply_text("Usage:\n/generate_message Your message")
        return

    message = text.split(" ", 1)[1]

    print("Broadcasting:", message)

    for chat_id in chat_ids:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=message
            )
        except Exception as e:
            print(f"Failed to send to {chat_id}:", e)

    await update.message.reply_text("✅ Message sent to all channels!")
            
# ------------------------------
# RUN BOT
# ------------------------------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("generate_post", generate_post))
app.add_handler(CommandHandler("generate_message", generate_message))

#add and remove user handlers 
app.add_handler(CommandHandler("add_user", add_user))
app.add_handler(CommandHandler("remove_user", remove_user))

#filter last lo vundali 
app.add_handler(MessageHandler(filters.ALL, save_chat))

print("Bot running... 🚀")
from telegram import Update

app.run_polling(allowed_updates=Update.ALL_TYPES)