import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔐 API keys
TELEGRAM_BOT_TOKEN = "7769288032:AAEjoz_6A0F8LegZ8sj_Dsr6Fp2aqad7o4A"
AFTERSHIP_API_KEY = "asat_5f44f63363474b8db81bfd0ae9aee7ae"

# 🧠 Function to get tracking status
def get_tracking_info(tracking_number, slug="dhl-global-mail-asia"):
    url = f"https://api.aftership.com/v4/trackings/{slug}/{tracking_number}"
    headers = {
        "aftership-api-key": AFTERSHIP_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()["data"]["tracking"]
        return {
            "number": data["tracking_number"],
            "slug": data["slug"],
            "status": data["tag"],
            "last_update": data.get("expected_delivery", data.get("updated_at", "Not Available"))
        }
    else:
        return None

# 📥 Handle user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tracking_number = update.message.text.strip()
    info = get_tracking_info(tracking_number)
    if info:
        reply = (
            f"📦 *Tracking Info*\n\n"
            f"🔢 *Number*: `{info['number']}`\n"
            f"🚚 *Courier*: `{info['slug']}`\n"
            f"📍 *Status*: `{info['status']}`\n"
            f"🕒 *Last Updated*: `{info['last_update']}`"
        )
    else:
        reply = "❌ Tracking number not found or invalid."

    await update.message.reply_text(reply, parse_mode="Markdown")

# ▶️ Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me your tracking number (e.g., `AELKS04667409DEX`) to get status!")

# 🔁 Main
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()
