import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from groq import Groq
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)

# --- Dummy Web Server to pass Render Healthchecks ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Length", "15")
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Length", "15")
        self.end_headers()

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()
# -----------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your AI bot (Hermes), powered by Groq (Llama 3.3). How can I help you today?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are Hermes, a helpful AI assistant. Always respond in Bengali or English based on the user's language. Keep answers concise but friendly."},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        reply = f"Sorry, I encountered an error: {e}"
    await update.message.reply_text(reply)

def main():
    if not TELEGRAM_TOKEN or not GROQ_API_KEY:
        print("Error: Missing API keys in environment variables!")
        return
        
    print("Starting bot...")
    app = Application.builder().token(TELEGRAM_TOKEN).read_timeout(60).write_timeout(60).connect_timeout(60).pool_timeout(60).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
