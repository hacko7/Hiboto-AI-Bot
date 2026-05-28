import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import os

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# API Setup
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.0-pro')

# Menu Buttons
def get_menu():
    keyboard = [
        ['/start', 'Write Code'],
        ['Tell me a story', 'Help']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I am Hiboto. How can I help you today?",
        reply_markup=get_menu()
    )

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    if user_text == 'Write Code':
        await update.message.reply_text("Please provide the topic or language for the code you need.")
    elif user_text == 'Tell me a story':
        response = model.generate_content("Tell me a short interesting story")
        await update.message.reply_text(response.text)
    elif user_text == 'Help':
        await update.message.reply_text("I am Hiboto, your AI assistant. You can ask me anything!")
    else:
        try:
            response = model.generate_content(user_text)
            await update.message.reply_text(response.text)
        except Exception as e:
            logging.error(f"Gemini Error: {e}")
            await update.message.reply_text("Sorry, something went wrong.")

def main():
    # Start Telegram Bot
    app = Application.builder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
    
