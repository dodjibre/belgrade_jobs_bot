import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets Setup
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1SXzsGMhPsZqog1W-LjK6Ml0AB1rXbQMf6CNLXz9L7KY").sheet1


# Conversation states
FULLNAME, EMAIL, PHONE, CVLINK, JOBTYPE = range(5)

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to *Belgrade Jobs Bot!* \n\n"
        "Let's start your job application.\n\n"
        "👉 First, type your FULL NAME:",
        parse_mode="Markdown"
    )
    return FULLNAME

async def fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fullname"] = update.message.text
    await update.message.reply_text("📧 Enter your EMAIL:")
    return EMAIL

async def email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    await update.message.reply_text("📱 Enter your PHONE NUMBER:")
    return PHONE

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("🔗 Paste a link to your CV (Google Drive / PDF link):")
    return CVLINK

async def cvlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cvlink"] = update.message.text

    keyboard = [["Game Presenter"], ["Other"]]
    await update.message.reply_text(
        "💼 Choose job type:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )
    return JOBTYPE

async def jobtype(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["jobtype"] = update.message.text

    # Save to Google Sheets
    sheet.append_row([
        context.user_data["fullname"],
        context.user_data["email"],
        context.user_data["phone"],
        context.user_data["cvlink"],
        context.user_data["jobtype"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

    await update.message.reply_text(
        "✅ *Application submitted successfully!*\n\n"
        "We will contact you soon.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Application cancelled.")
    return ConversationHandler.END


def main():
    TOKEN = "8399538096:AAGNFXXUAJknz3P4EbFMLfXep4sG5_8Fz_c"

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FULLNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, fullname)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            CVLINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, cvlink)],
            JOBTYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, jobtype)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
