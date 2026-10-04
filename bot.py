import os
import difflib
import time
import threading
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)
import speech_recognition as sr
from pydub import AudioSegment
import imageio_ffmpeg

# Set ffmpeg path for pydub
AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()

# ==================== CONFIGURATIONS ====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YAHAN_BOT_TOKEN_DAALEIN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "")

# GitHub API Configurations
# Note: Token me 'repo' scope ka hona zaroori hai
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip() 
GITHUB_REPO = os.getenv("GITHUB_REPO", "singhji97/UK").strip()
GITHUB_FILE_PATH = os.getenv("GITHUB_FILE_PATH", "questions.txt").strip()
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main").strip()

# Security: Telegram User ID (Khali chhodne par sabhi use kar sakte hain)
ADMIN_ID = os.getenv("ADMIN_ID", "") 

QUESTIONS = []

# ==================== 1. KEEP-ALIVE PING SERVER ====================
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

        time.sleep(600)  # Har 10 minute me ping

# ==================== 2. GITHUB API FUNCTIONS ====================
def get_github_headers():
    """GitHub API ke standard headers (User-Agent aur Auth zaroori hote hain)"""
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "UKVisa-Telegram-Bot",
        "X-GitHub-Api-Version": "2022-11-28"
    }

def get_github_file_sha():
    """File ka SHA nikalta hai jo update karne ke liye zaroori hota hai"""
    if not GITHUB_TOKEN:
        return None
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}?ref={GITHUB_BRANCH}"
    try:
        res = requests.get(url, headers=get_github_headers(), timeout=10)
        if res.status_code == 200:
            return res.json().get("sha")
    except Exception as e:
        print(f"SHA fetch error: {e}")
    return None

def upload_file_to_github(file_bytes):
    """GitHub API ke through file ko create ya update karega"""
    if not GITHUB_TOKEN:
        return False, "GITHUB_TOKEN configure nahi hai! Render/Environment me GITHUB_TOKEN set karein."

    sha = get_github_file_sha()
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    
    b64_content = base64.b64encode(file_bytes).decode("utf-8")
    payload = {
        "message": "Update questions via Telegram Bot",
        "content": b64_content,
        "branch": GITHUB_BRANCH
    }
    
    # Agar file pehle se maujood hai toh SHA dena mandatory hai
    if sha:
        payload["sha"] = sha

    try:
        res = requests.put(url, headers=get_github_headers(), json=payload, timeout=15)
        if res.status_code in [200, 201]:
            return True, "File GitHub par successfully save/update ho gayi!"
        elif res.status_code == 404:
            return False, (
                f"GitHub Error (404 Not Found):\n"
                f"1. Check karein repo '{GITHUB_REPO}' sahi hai ya nahi.\n"
                f"2. GITHUB_TOKEN me 'repo' (write permission) tick hai ya nahi.\n"
                f"3. GitHub repo khali toh nahi hai? (README file banayein)."
            )
        else:
            return False, f"GitHub Error ({res.status_code}): {res.text}"
    except Exception as e:
        return False, f"Request failed: {str(e)}"

def delete_file_from_github():
    """GitHub API ke through file ko delete karega"""
    if not GITHUB_TOKEN:
        return False, "GITHUB_TOKEN configure nahi hai!"

    sha = get_github_file_sha()
    if not sha:
        return False, "File GitHub par nahi mili ya pehle se deleted hai."

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    payload = {
        "message": "Deleted questions.txt via Telegram Bot",
        "sha": sha,
        "branch": GITHUB_BRANCH
    }

    try:
        res = requests.delete(url, headers=get_github_headers(), json=payload, timeout=15)
        if res.status_code == 200:
            return True, "File GitHub se delete ho gayi!"
        else:
            return False, f"GitHub Error ({res.status_code}): {res.text}"
    except Exception as e:
        return False, f"Request failed: {str(e)}"

# ==================== 3. QUESTIONS PARSER ====================
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
    """GitHub Raw URL ya Local file se questions load karta hai"""
    global QUESTIONS
    raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_FILE_PATH}?t={int(time.time())}"
    try:
        headers = {"Cache-Control": "no-cache", "Pragma": "no-cache"}
        res = requests.get(raw_url, headers=headers, timeout=10)
        if res.status_code == 200:
            QUESTIONS = parse_questions_content(res.text)
            if QUESTIONS:
                return True, f"GitHub se {len(QUESTIONS)} questions load ho gaye!"
    except Exception as e:
        print(f"Error fetching questions: {e}")

    if os.path.exists("questions.txt"):
        with open("questions.txt", "r", encoding="utf-8") as f:
            QUESTIONS = parse_questions_content(f.read())
        return True, f"Local file se {len(QUESTIONS)} questions load ho gaye!"

    return False, "Koi questions nahi mile!"

# Initial load
reload_questions()
recognizer = sr.Recognizer()

# Admin Check Helper
def is_admin(user_id):
    if not ADMIN_ID:
        return True
    return str(user_id) == str(ADMIN_ID)

# ==================== 4. BOT HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q_index"] = 0
    if not QUESTIONS:
        reload_questions()

    if not QUESTIONS:
        await update.message.reply_text(
            "⚠️ Abhi koi questions upload nahi hain!\n\n"
            "👉 Aap seedha apni `.txt` file yahan send karein, bot automatic ise GitHub par save kar lega."
        )
        return

    await update.message.reply_text(
        "🇬🇧 *UK Visa Interview Practice Bot* me aapka swagat hai!\n\n"
        "🔹 Sawal aane par apna answer **Voice Note (bolkar)** bhejein.\n"
        "🔹 Nayi file lagane ke liye sirf **.txt file send** kar dein.\n"
        "🔹 Sabhi sawal hatane ke liye **/delete** dabayein.\n\n"
        "Pehla sawal niche dekhein 👇",
        parse_mode="Markdown"
    )
    await ask_question(update, context)

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q_index"] = 0
    success, msg = reload_questions()
    if success:
        await update.message.reply_text(f"🔄 *Reset Successful!*\n\n{msg}", parse_mode="Markdown")
        await ask_question(update, context)
    else:
        await update.message.reply_text(f"❌ Error: {msg}")

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global QUESTIONS
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Aapko delete karne ki permission nahi hai!")
        return

    status_msg = await update.message.reply_text("⏳ GitHub se file delete ho rahi hai...")
    success, msg = delete_file_from_github()

    if success:
        QUESTIONS = []
        context.user_data["q_index"] = 0
        if os.path.exists("questions.txt"):
            os.remove("questions.txt")
        await status_msg.edit_text("🗑️ *Sabhi Questions Delete ho gaye!* Ab bot khali hai.", parse_mode="Markdown")
    else:
        await status_msg.edit_text(f"❌ Delete Failed:\n`{msg}`", parse_mode="Markdown")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global QUESTIONS
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Aapko file upload karne ki permission nahi hai!")
        return

    doc = update.message.document
    if not doc.file_name.lower().endswith(".txt"):
        await update.message.reply_text("⚠️ Kripya sirf `.txt` format wali file hi bhejein!")
        return

    status_msg = await update.message.reply_text("📥 File download ho rahi hai...")
    
    file = await doc.get_file()
    file_bytes = await file.download_as_bytearray()
    content_text = file_bytes.decode("utf-8", errors="ignore")

    parsed = parse_questions_content(content_text)
    if not parsed:
        await status_msg.edit_text(
            "❌ File me `Q:` aur `A:` format ke questions nahi mile!\n"
            "Format example:\n\nQ: Why UK?\nA: Because...\n---"
        )
        return

    await status_msg.edit_text("🚀 GitHub par automatically upload kiya jaa raha hai...")

    success, msg = upload_file_to_github(file_bytes)
    if success:
        QUESTIONS = parsed
        context.user_data["q_index"] = 0
        with open("questions.txt", "w", encoding="utf-8") as f:
            f.write(content_text)

        await status_msg.edit_text(
            f"✅ *File Successfully GitHub Par Save Ho Gayi!*\n\n"
            f"📊 Kul *{len(QUESTIONS)}* questions load ho chuke hain.\n"
            f"Interview shuru karne ke liye **/start** dabayein.",
            parse_mode="Markdown"
        )
    else:
        await status_msg.edit_text(f"❌ {msg}", parse_mode="Markdown")

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
            "🎉 *Interview Complete!*\nNaye questions upload karne ke liye file bhejein ya **/reset** dabayein.",
            parse_mode="Markdown"
        )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = context.user_data.get("q_index", 0)
    if idx >= len(QUESTIONS):
        await update.message.reply_text("Koi active interview nahi hai. Shuru karne ke liye /start dabayein.")
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
    app.add_handler(CommandHandler("delete", delete_command))
    
    # Document / TXT file handler
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    # Voice handler
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
