import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from flask import Flask
import threading

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# API Setup
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
# v1beta లో నడిచే పాత మోడల్ టెక్స్ట్ నేమ్ ఇక్కడ ఇచ్చాను, ఇది పక్కా వర్క్ అవుతుంది
model = genai.GenerativeModel('gemini-1.0-pro')


# Dummy Web Server for Render Port Binding
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is running!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

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
    # Start Web Server in Background
    threading.Thread(target=run_web_server, daemon=True).start()

    # Start Telegram Bot
    app = Application.builder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
    
