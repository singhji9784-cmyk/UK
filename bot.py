import os
import difflib
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import speech_recognition as sr
from pydub import AudioSegment
import imageio_ffmpeg

# Set ffmpeg path for pydub
AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()

# --- Configurations ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "YAHAN_APNA_TELEGRAM_BOT_TOKEN_DAALEIN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "")

GITHUB_RAW_URL = os.getenv(
    "GITHUB_RAW_URL", 
    "https://raw.githubusercontent.com/singhji97/UK/main/questions.txt"
)

QUESTIONS = []

# --- Keep-Alive HTTP Server ---
class PingServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

    def log_message(self, format, *args):
        return

def run_web_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), PingServerHandler)
    print(f"Keep-Alive Server started on port {port}")
    server.serve_forever()

def auto_keep_alive_ping():
    time.sleep(30)
    while True:
        try:
            target_url = RENDER_EXTERNAL_URL
            if not target_url:
                port = int(os.getenv("PORT", 8080))
                target_url = f"http://127.0.0.1:{port}/"

            res = requests.get(target_url, timeout=10)
            print(f"[Keep-Alive] Ping sent! Status: {res.status_code}")
        except Exception as e:
            print(f"[Keep-Alive] Ping error: {e}")

        time.sleep(600)

# --- Parser & Logic ---
def parse_questions_content(content):
    entries = content.split("---")
    qa_list = []
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        if "Q:" in entry and "A:" in entry:
            parts = entry.split("A:", 1)
            q_part = parts[0].replace("Q:", "", 1).strip()
            a_part = parts[1].strip()
            if q_part and a_part:
                qa_list.append({
                    "question": q_part,
                    "answer": a_part
                })
    return qa_list

def reload_questions():
    global QUESTIONS
    if GITHUB_RAW_URL and "githubusercontent.com" in GITHUB_RAW_URL:
        try:
            url = f"{GITHUB_RAW_URL}?t={int(time.time())}"
            headers = {
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                QUESTIONS = parse_questions_content(response.text)
                return True, f"GitHub se {len(QUESTIONS)} questions load ho gaye!"
        except Exception as e:
            print(f"GitHub fetch error: {e}")

    if os.path.exists("questions.txt"):
        with open("questions.txt", "r", encoding="utf-8") as f:
            QUESTIONS = parse_questions_content(f.read())
        return True, f"Local questions.txt se {len(QUESTIONS)} questions load ho gaye!"
    
    return False, "questions.txt file nahi mili!"

reload_questions()
recognizer = sr.Recognizer()

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q_index"] = 0
    if not QUESTIONS:
        reload_questions()

    if not QUESTIONS:
        await update.message.reply_text("⚠️ questions.txt file me koi questions nahi mile!")
        return

    await update.message.reply_text(
        "🇬🇧 *UK Visa Interview Practice Bot* me aapka swagat hai!\n\n"
        "🔹 Sawal aane par apna answer **Voice Note (bolkar)** bhejein.\n"
        "🔹 GitHub par kuch bhi badalne ke baad **/reset** dabayein.\n\n"
        "Taiyaar hone par niche pehla sawal dekhein 👇",
        parse_mode="Markdown"
    )
    await ask_question(update, context)

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q_index"] = 0
    success, msg = reload_questions()
    
    if success:
        await update.message.reply_text(
            f"🔄 *Reset Successful!*\n\n{msg}\n\n"
            "Chaliye shuru karte hain 👇",
            parse_mode="Markdown"
        )
        await ask_question(update, context)
    else:
        await update.message.reply_text(f"❌ Error: {msg}")

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = context.user_data.get("q_index", 0)
    if idx < len(QUESTIONS):
        q_text = QUESTIONS[idx]["question"]
        msg = f"🎙️ *Question {idx + 1}/{len(QUESTIONS)}:*\n\n👉 *{q_text}*\n\n*(Apna answer bolkar Voice Note bhejein)*"
        if update.message:
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.effective_chat.send_message(msg, parse_mode="Markdown")
    else:
        await update.effective_chat.send_message(
            "🎉 *Interview Complete! Sabhi questions poore ho gaye.*\n"
            "Naye questions ke sath shuru karne ke liye **/reset** dabayein.",
            parse_mode="Markdown"
        )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = context.user_data.get("q_index", 0)
    if idx >= len(QUESTIONS):
        await update.message.reply_text("Interview complete ho chuka hai. Dobara shuru karne ke liye /reset dabayein.")
        return

    status_msg = await update.message.reply_text("⏳ Processing audio...")

    voice_file = await update.message.voice.get_file()
    user_id = update.message.from_user.id
    oga_path = f"temp_{user_id}.oga"
    wav_path = f"temp_{user_id}.wav"
    await voice_file.download_to_drive(oga_path)

    try:
        audio = AudioSegment.from_file(oga_path)
        audio.export(wav_path, format="wav")
    except Exception as e:
        await status_msg.edit_text(f"❌ Audio convert error: {str(e)}")
        if os.path.exists(oga_path): os.remove(oga_path)
        return

    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            user_text = recognizer.recognize_google(audio_data, language="en-GB")
    except sr.UnknownValueError:
        await status_msg.edit_text("❌ Aapki aawaz saaf nahi aayi. Kripya dubara bolkar bhejein.")
        if os.path.exists(oga_path): os.remove(oga_path)
        if os.path.exists(wav_path): os.remove(wav_path)
        return
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")
        if os.path.exists(oga_path): os.remove(oga_path)
        if os.path.exists(wav_path): os.remove(wav_path)
        return

    if os.path.exists(oga_path): os.remove(oga_path)
    if os.path.exists(wav_path): os.remove(wav_path)

    expected_answer = QUESTIONS[idx]["answer"]
    clean_user = " ".join(user_text.lower().split())
    clean_exp = " ".join(expected_answer.lower().split())
    similarity = difflib.SequenceMatcher(None, clean_user, clean_exp).ratio() * 100

    feedback = (
        f"🗣️ *Aapne bola:*\n\"{user_text}\"\n\n"
        f"✅ *Expected Answer:*\n\"{expected_answer}\"\n\n"
        f"📊 *Accuracy Score:* {similarity:.1f}%\n"
    )
    await status_msg.edit_text(feedback, parse_mode="Markdown")

    context.user_data["q_index"] = idx + 1
    await ask_question(update, context)

def main():
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()

    ping_thread = threading.Thread(target=auto_keep_alive_ping, daemon=True)
    ping_thread.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("reload", reset_command))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
