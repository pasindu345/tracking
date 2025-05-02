import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Replace this with your own Telegram bot token
BOT_TOKEN = "7769288032:AAEjoz_6A0F8LegZ8sj_Dsr6Fp2aqad7o4A"
AFTERSHIP_API_KEY = "asat_5f44f63363474b8db81bfd0ae9aee7ae"
AFTERSHIP_API_URL = "https://api.aftership.com/v4/trackings"

headers = {
    "aftership-api-key": AFTERSHIP_API_KEY,
    "Content-Type": "application/json"
}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to AliExpress Tracking Bot!\nSend me your tracking number to get the latest status.")

# Function to create tracking
def create_tracking(tracking_number):
    payload = {
        "tracking": {
            "tracking_number": tracking_number
        }
    }
    response = requests.post(AFTERSHIP_API_URL, headers=headers, json=payload)
    return response.status_code in [200, 201, 409]  # 409 = already exists

# Function to get tracking info
def get_tracking_info(tracking_number):
    url = f"{AFTERSHIP_API_URL}/{tracking_number}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()["data"]["tracking"]
        status = data["tag"]
        courier = data.get("slug", "Unknown Courier")
        checkpoints = data.get("checkpoints", [])
        last_update = checkpoints[-1]["message"] if checkpoints else "No updates yet."
        return f"📦 Tracking Number: {tracking_number}\n🚚 Courier: {courier}\n📍 Status: {status}\n🕒 Last Update: {last_update}"
    else:
        return "❌ Tracking info not found. Please check the tracking number."

# Handle tracking numbers
async def handle_tracking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tracking_number = update.message.text.strip()
    created = create_tracking(tracking_number)
    if created:
        status_message = get_tracking_info(tracking_number)
        await update.message.reply_text(status_message)
    else:
        await update.message.reply_text("❌ Failed to create or fetch tracking info.")

# Run bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tracking))

    print("Bot is running...")
    app.run_polling()
