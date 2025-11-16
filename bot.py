import os
import json
import gspread
from google.oauth2 import service_account
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === GOOGLE AUTH ===
def init_gspread():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")

    if not creds_json:
        raise Exception("ERROR: GOOGLE_CREDENTIALS env var is missing!")

    creds_dict = json.loads(creds_json)

    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    client = gspread.authorize(creds)
    return client

client = init_gspread()
sheet = client.open_by_key("1SXzsGMhPsZqog1W-LjK6Ml0AB1rXbQMf6CNLXz9L7KY").sheet1


# === BOT HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Zdravo! Pošalji mi svoj CV ili poruku i upisujem u tabelu!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    sheet.append_row([user.id, user.username, user.first_name, text])

    await update.message.reply_text("Upisano! ✔️")


# === MAIN ===
def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise Exception("ERROR: Missing BOT_TOKEN env variable!")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot je pokrenut na Renderu...")
    app.run_polling()


if __name__ == "__main__":
    main()
