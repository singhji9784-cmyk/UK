Yeh raha aapka **poora complete updated code**. 

Isme Python ka built-in `http.server` aur auto-ping dono laga diye gaye hain, jisse:
1. Render ke port par ek mini web server background thread me chalu rahega.
2. Bot har 10 minute me khud ko ping karega taaki Render sleep na ho aur 24/7 active rahe.
3. Iske liye koi nayi library (`flask` wagairah) install karne ki zaroorat nahi hai.

---

### File: `main.py` (ya `bot.py`)

```python
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

# Render automatically provides RENDER_EXTERNAL_URL if deployed as a Web Service
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "")

# Apni GitHub raw file ka URL yahan dalein:
GITHUB_RAW_URL = os.getenv(
    "GITHUB_RAW_URL", 
    "https://raw.githubusercontent.com/singhji97/UK/main/questions.txt"
)

QUESTIONS = []

# =========================================================
# 1. PING SYSTEM & MINI WEB SERVER (Sleep se bachane ke liye)
# =========================================================
class PingServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"UK Visa Practice Bot is Active & Running!")

    def log_message(self, format, *args):
        # Console me har ping ka faltu log na aaye isliye silent rakha hai
        return

def run_web_server():
    """Render ke assigned port par background me server chalayega"""
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), PingServerHandler)
    print(f"Keep-Alive Server started on port {port}")
    server.serve_forever()

def auto_keep_alive_ping():
    """Har 10 minute me app ko ping karega taaki Render sleep na kare"""
    time.sleep(30)  # Shuru me 30 second wait jab tak server fully ready na ho jaye
    while True:
        try:
            # Agar Render ka URL mila toh uspar request bhejega, warna local port par
            target_url = RENDER_EXTERNAL_URL
            if not target_url:
                port = int(os.getenv("PORT", 8080))
                target_url = f"http://127.0.0.1:{port}/"

            res = requests.get(target_url, timeout=10)
            print(f"[Keep-Alive] Ping sent! Status: {res.status_code}")
        except Exception as e:
            print(f"[Keep-Alive] Ping error: {e}")

        # 10 minute (600 seconds) wait
        time.sleep(600)

# =========================================================
# 2. QUESTIONS & TELEGRAM BOT LOGIC
# =========================================================
def parse_questions_content(content):
    entries = content.split("---")
    qa_list = []
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        
        # Q: aur A: ko bina kisi line limit ke poora extract karega
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
                return True, f"GitHub se {len(QUESTIONS)} questions (Full Answers ke sath) load ho gaye!"
        except Exception as e:
            print(f"GitHub fetch error: {e}")

    if os.path.exists("questions.txt"):
        with open("questions.txt", "r", encoding="utf-8") as f:
            QUESTIONS = parse_questions_content(f.read())
        return True, f"Local questions.txt se {len(QUESTIONS)} questions load ho gaye!"
    
    return False, "questions.txt file nahi mili!"

# Initial load
reload_questions()
recognizer = sr.Recognizer()

# /start Command
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

# /reset Command
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

# Ask Question
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

# Handle Voice
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

    # Convert to wav
    try:
        audio = AudioSegment.from_file(oga_path)
        audio.export(wav_path, format="wav")
    except Exception as e:
        await status_msg.edit_text(f"❌ Audio convert error: {str(e)}")
        if os.path.exists(oga_path): os.remove(oga_path)
        return

    # Speech Recognition
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

    # Clean text comparison
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
    # 1. Background me HTTP Server chalu karein
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()

    # 2. Background me Auto-Pinger chalu karein
    ping_thread = threading.Thread(target=auto_keep_alive_ping, daemon=True)
    ping_thread.start()

    # 3. Telegram Bot start karein
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("reload", reset_command))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
```

---

### Render ke liye Sirf Ek Chhota Sa Kaam:
1. Apne Render dashboard par jayein.
2. Ensure karein ki service **"Web Service"** ke roop me deployed ho (taaki isko Render ka ek free link mile jaise: `https://my-uk-bot.onrender.com`).
3. Bot deploy hote hi background me mini server aur ping system dono active ho jayenge. Render ise band nahi karega aur aapko bar-bar Render dashboard khol kar redeploy nahi karna padega.
