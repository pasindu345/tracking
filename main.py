import logging
import requests
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔐 API keys
TELEGRAM_BOT_TOKEN = "7769288032:AAEjoz_6A0F8LegZ8sj_Dsr6Fp2aqad7o4A"
AFTERSHIP_API_KEY = "asat_5f44f63363474b8db81bfd0ae9aee7ae"

# File to store tracking numbers and their updates
TRACKING_HISTORY_FILE = "tracking_history.json"

# 🧠 Function to get tracking info
def get_tracking_info(tracking_number, slug="dhl-global-mail-asia"):
    url = f"https://api.aftership.com/v4/trackings/{slug}/{tracking_number}"
    headers = {
        "aftership-api-key": AFTERSHIP_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()["data"]["tracking"]
        status = data["tag"]
        custom_message = ""

        # Custom messages based on status
        if status == "in_transit":
            custom_message = "🚚 Your package is in transit. It’s on the way!"
        elif status == "arrived":
            custom_message = "✈️ Your package has arrived at the airport."
        elif status == "delivered":
            custom_message = "📦 Your package has been delivered."
        elif status == "expired":
            custom_message = "❌ The tracking information has expired."
        elif status == "failed":
            custom_message = "⚠️ Delivery failed. Please contact the courier."
        else:
            custom_message = "📍 Status update is not available."

        return {
            "number": data["tracking_number"],
            "slug": data["slug"],
            "status": status,
            "last_update": data.get("expected_delivery", data.get("updated_at", "Not Available")),
            "custom_message": custom_message
        }
    else:
        return None

# 🧠 Function to store tracking history
def store_tracking_history(tracking_number, status):
    try:
        with open(TRACKING_HISTORY_FILE, "r") as file:
            history = json.load(file)
    except FileNotFoundError:
        history = {}

    history[tracking_number] = status

    with open(TRACKING_HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

# 📥 Handle user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tracking_number = update.message.text.strip()
    info = get_tracking_info(tracking_number)
    if info:
        # Store the tracking update
        store_tracking_history(tracking_number, info["status"])

        reply = (
            f"📦 *Tracking Info*\n\n"
            f"🔢 *Number*: `{info['number']}`\n"
            f"🚚 *Courier*: `{info['slug']}`\n"
            f"📍 *Status*: `{info['status']}`\n"
            f"🕒 *Last Updated*: `{info['last_update']}`\n\n"
            f"📝 *Message*: {info['custom_message']}"
        )
    else:
        reply = "❌ Tracking number not found or invalid."

    await update.message.reply_text(reply, parse_mode="Markdown")

# 📜 List all tracking numbers
async def list_trackings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(TRACKING_HISTORY_FILE, "r") as file:
            history = json.load(file)
        if history:
            reply = "📜 *Tracking Numbers History*\n\n"
            for tracking, status in history.items():
                reply += f"🔢 *Number*: `{tracking}` - *Status*: `{status}`\n"
        else:
            reply = "❌ No tracking numbers found."
    except FileNotFoundError:
        reply = "❌ No tracking history found."
    
    await update.message.reply_text(reply, parse_mode="Markdown")

# ▶️ Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me your tracking number (e.g., `AELKS04667409DEX`) to get status!\n\nUse /trackings to view your tracking history.")

# 🔁 Main
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trackings", list_trackings))  # Add /trackings command
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()
