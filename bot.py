import os
che diya gaya **pura updated code** copy karein. Isme GitHub API se real-time fetch, memory clear aur local file sync fix kar diyaimport difflib
import time
import threading
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
     gaya hai:

```python
import os
import difflib
import time
import threading
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from telegram import Update
from telegram.ext import (
    MessageHandler, 
    filters, 
    ContextTypes
)
import speech_recognition as sr
from pydub import AudioSegment
import imageio_ffmpeg

# Set ffmpeg path for pydub
AudioSegment.converter = imageio_ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)ffmpeg.get_ffmpeg_exe()

# ==================== CONFIGURATIONS ====================
BOT_TOKEN =
import speech_recognition as sr
from pydub import AudioSegment
import imageio_ffmpeg

# Set ffm os.getenv("BOT_TOKEN", "YAHAN_BOT_TOKEN_DAALEIN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "")

# GitHub Configurations
GITHUB_TOKEN = os.getenvpeg path for pydub
AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()

# ==================== CONFIGURATIONS ====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YAHAN_BOT_TOKEN_DAALEIN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "")

# GitHub Configurations
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip() 
GITHUB_REPO = os.getenv("GITHUB_REPO", "singhji9784-cmyk/UK").strip()
GITHUB_FILE_PATH = os.getenv("GITHUB_FILE_PATH", "questions.txt").strip()
("GITHUB_TOKEN", "").strip() 
GITHUB_REPO = os.getenv("GITHUB_REPO", "singhji9784-cmyk/UK").strip()
GITHUB_FILE_PATH = os.getenv("GITHUB_FILE_PATH", "questions.txt").strip()
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main").strip()

# Admin check (khali chhodne par sab use kar sakte hain)
ADMIN_ID = os.getenv("ADMIN_ID", "").strip() 

QUESTIONS = []

# =GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main").strip()

# Admin check (khali=================== 1. KEEP-ALIVE PING SERVER ====================
class PingServerHandler(BaseHTTPRequestHandler chhodne par sab use kar sakte hain)
ADMIN_ID = os.getenv("ADMIN_ID", "").):
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
    time.sleep(strip() 

QUESTIONS = []

# ==================== 1. KEEP-ALIVE PING SERVER ====================
class PingServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

    def log_30)
    while True:
        try:
            target_url = RENDER_EXTERNAL_URL
            if not target_url:
                port = int(os.getenv("PORT", 8080))
                target_message(self, format, *args):
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
                target_url = f"http://127.0.0.1:{url = f"http://127.0.0.1:{port}/"

            res = requests.get(target_url, timeout=10)
            print(f"[Keep-Alive] Ping sent! Status: {res.status_code}")
        except Exception as e:
            print(f"port}/"

            res = requests.get(target_url, timeout=10)
            print(f"[Keep-Alive] Ping sent! Status: {res.status_code}")
        except Exception as e[Keep-Alive] Ping error: {e}")

        time.sleep(600)  # Har 10 minute me ping

# ==================== 2. GITHUB API FUNCTIONS ====================
def get_github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github:
            print(f"[Keep-Alive] Ping error: {e}")

        time.sleep(600)  # Har 10 minute me ping

# ==================== 2. GITHUB API FUNCTIONS ====================
def get_github_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent+json",
        "User-Agent": "UKVisa-Telegram-Bot",
        "X-GitHub-Api-Version": "2022-11-28"
    }

def get_github_": "UKVisa-Telegram-Bot",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if GITHUB_TOKEN:
        headersfile():
    """Live GitHub API se file content aur sha fetch karta hai (No Cache Issue)"""
    if not GITHUB_TOKEN:
        return None, None
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers

def get_github_file_sha():
    """File ka SHA nikalta hai agar file exist karti ho"""
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

def upload_file_to_githubGITHUB_FILE_PATH}?ref={GITHUB_BRANCH}"
    try:
        res = requests.get(url, headers=get_github_headers(), timeout=10)
        if res.status_code == 200:
            data = res.json()
            # GitHub API base64 content return karti hai
            content_b64 = data.get("content", "")
            raw_text = base64.b64decode(content_b64).decode("utf-8", errors="ignore")
            return raw_text, data.get("sha")(file_bytes):
    """GitHub API ke through file upload ya update karega"""
    if not GITHUB_TOKEN:
        return False, "GITHUB_TOKEN Render me set nahi hai!"

    sha = get_github_file_sha()
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB
        elif res.status_code == 404:
            # File GitHub par nahi hai / delete ho chuki_FILE_PATH}"
    
    b64_content = base64.b64encode( hai
            return False, None
    except Exception as e:
        print(f"GitHub fetch error:file_bytes).decode("utf-8")
    payload = {
        "message": "Update questions via Telegram Bot",
        "content": b64_content,
        "branch": GITHUB_BRANCH
    }
    if sha:
        payload["sha"] = sha

    try:
        res = requests {e}")
    return None, None

def get_github_file_sha():
    _, sha = get_github_file()
    return sha

def upload_file_to_github(file_bytes):
    """GitHub API ke through file upload ya update karega"""
    if not GITHUB_TOKEN:
        return False, "GITHUB_TOKEN Render me set nahi hai!"

    sha = get_github_file_sha()
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    
    b64_content = base64.b64encode(file_bytes).decode("utf-8")
    payload = {
        "message": "Update questions via Telegram Bot",
        .put(url, headers=get_github_headers(), json=payload, timeout=15)
        if res.status_code in [200, 201]:
            return True, "File GitHub par successfully save ho gayi!"
        elif res.status_code == 404:
            return"content": b64_content,
        "branch": GITHUB_BRANCH
    }
    if False, f"GitHub Repo nahi mili! Check karein: '{GITHUB_REPO}'"
        else:
 sha:
        payload["sha"] = sha

    try:
        res = requests.put(url, headers=get_github_headers(), json=payload, timeout=15)
        if res.status_code in [200, 201]:
            return True, "File GitHub par successfully save ho            return False, f"GitHub Error ({res.status_code}): {res.text}"
    except Exception as e:
        return False, f"Upload Connection Error: {str(e)}"

def delete_file_from_github():
    if not GITHUB_TOKEN:
        return False, "GITHUB_TOKEN set nahi hai!"

    sha = get_github_file_sha gayi!"
        elif res.status_code == 404:
            return False, f"GitHub()
    if not sha:
        return True, "File pehle se GitHub par nahi hai."

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    payload Repo nahi mili! Check karein: '{GITHUB_REPO}'"
        else:
            return False, f"GitHub Error ({res = {
        "message": "Deleted questions.txt via Telegram Bot",
        "sha": sha,
.status_code}): {res.text}"
    except Exception as e:
        return False, f"Upload Connection Error: {str(e)}"

def delete_file_from_github():
    if not GITHUB_TOKEN:
        return False, "GITHUB_TOKEN set nahi hai!"

    sha = get_github        "branch": GITHUB_BRANCH
    }

    try:
        res = requests.delete(url, headers=get_github_headers(), json=payload, timeout=15)
        if res.status_file_sha()
    if not sha:
        return True, "File GitHub par pehle se hi delete hai."

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents_code in [200, 204]:
            return True, "File GitHub se delete ho/{GITHUB_FILE_PATH}"
    payload = {
        "message": "Deleted questions.txt via Telegram Bot",
        "sha": sha,
        "branch": GITHUB_BRANCH
    }

    try:
        res = requests.delete(url, headers=get_github_headers(), json=payload, timeout=15)
        if res.status_code in [200, 204]:
            return True, "File GitHub gayi!"
        elif res.status_code == 404:
            return True, "File pehle se delete ho chuki hai."
        else:
            return False, f"GitHub Error ({res.status_code}): {res.text}"
    except Exception as e:
        return False, f"Delete Connection Error: {str(e)}"

# ==================== 3. QUESTIONS PARSER & RELOAD ====================
def se delete ho gayi!"
        else:
            return False, f"GitHub Error ({res.status_code parse_questions_content(content):
    if not content:
        return []
    entries = content.}): {res.text}"
    except Exception as e:
        return False, f"Delete Connection Error:split("---")
    qa_list = []
    for entry in entries:
        entry = entry. {str(e)}"

# ==================== 3. QUESTIONS PARSER ====================
def parse_questions_content(content):
    if not content:
        return []
    entries = content.split("---")
    qa_list = []
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        if "Q:" in entry and "A:" in entry:
            parts = entry.split("strip()
        if not entry:
            continue
        if "Q:" in entry and "A:" in entry:
            parts = entry.split("A:", 1)
            q_part = parts[0].replace("Q:", "", 1).strip()
            a_part = parts[1].strip()
            if q_part and a_part:
                qa_list.append({
                    "question": q_part,
                    "A:", 1)
            q_part = parts[0].replace("Q:", "", 1).strip()
            a_part = parts[1].strip()
            if q_part and a_part:answer": a_part
                })
    return qa_list

def reload_questions():
    """Real-time GitHub API se questions load karega bina cache delay ke"""
    global QUESTIONS

    # 1. GitHub API se content fetch karein (No Caching)
    if GITHUB_TOKEN:
        url = f"https://api.github.com/
                qa_list.append({
                    "question": q_part,
                    "answer": a_repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}?ref={GITHUB_BRANCH}"
        try:
            res = requests.get(url, headers=get_github_headers(), timeout=10)
            if res.status_code == 200:
                data = res.json()
                contentpart
                })
    return qa_list

def reload_questions():
    global QUESTIONS
    QUESTIONS = []  # Har baar reload shuru hote hi pehle memory clear karein

    if GITHUB_TOKEN:
        content, sha = get_github_file()
        if content is False:
            # File GitHub par 404 (Deleted) hai -> Local file bhi uda do
            if os.path.exists("questions.txt"):
                try_b64 = data.get("content", "")
                decoded_content = base64.b64decode(content_b64).decode("utf-8", errors="ignore")
                parsed = parse_questions_content(decoded_content)
                
                QUESTIONS = parsed  # Hamesha update karega chahe list khali ho
                if: os.remove("questions.txt")
                except: pass
            return False, "GitHub par file nahi hai ( QUESTIONS:
                    with open("questions.txt", "w", encoding="utf-8") as f:
                        Deleted). Sabhi questions clear hain!"
        
        elif content:
            parsed = parse_questions_content(content)
            QUESTIONS = parsed
            # Local backup update karein
            with open("questions.txt", "w", encodingf.write(decoded_content)
                    return True, f"GitHub se {len(QUESTIONS)} questions load ho gaye!"
                else:
                    if os.path.exists("questions.txt"):
                        os.remove("questions.txt")
                    return False, "GitHub file khali hai, koi question nahi mila!"

            elif res.status_code="utf-8") as f:
                f.write(content)
            if QUESTIONS:
                return True, f"GitHub se {len(QUESTIONS)} questions load ho gaye!"
            else:
                return False, "File khali hai, koi question nahi mila."

    # Agar GitHub token nahi hai tabhi local check karein
    if == 404:
                # Agar GitHub par file delete ho chuki hai
                QUESTIONS = []
                if os.path.exists("questions.txt"):
                    os.remove("questions.txt")
                return False, "GitHub par file delete ho chuki hai!"
        except Exception as e:
            print(f"GitHub API fetch error: {e}")

    # 2. Agar GitHub Token nahi hai ya API fail ho gayi, fallback to local file os.path.exists("questions.txt"):
        with open("questions.txt", "r", encoding="utf-8") as f:
            QUESTIONS = parse_questions_content(f.read())
        if QUESTIONS:
            return True, f"Local file se {len(QUESTIONS)} questions load ho gaye!"

    return False, "Koi questions nahi mile
    if os.path.exists("questions.txt"):
        try:
            with open("questions.txt", "r", encoding="utf-8") as f:
                parsed = parse_questions_content(f.read())
            QUESTIONS = parsed
            if QUESTIONS:
                return True, f"Local file se! Bot abhi poori tarah khali hai."

reload_questions()
recognizer = sr.Recognizer()

def is_admin(user_id):
    if not ADMIN_ID:
        return True
    return str(user_ {len(QUESTIONS)} questions load ho gaye!"
        except Exception as e:
            print(f"Localid) == str(ADMIN_ID)

# ==================== 4. BOT HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q_index"] = 0
    reload_questions()

    if not QUESTIONS:
        await update.message.reply_text(
            "⚠️ Abhi koi questions upload nahi hain!\n\n" read error: {e}")

    # Agar koi file nahi mili
    QUESTIONS = []
    return False, "Koi questions nahi mile!"

reload_questions()
recognizer = sr.Recognizer()

def is_admin(user_id):
    if not ADMIN_ID:
            "👉 Nayi .txt file bhejein jisme questions ho."
        )
        return

    
        return True
    return str(user_id) == str(ADMIN_ID)

# ==================== 4. BOT HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q_index"] = 0
    reload_questions()

    if not QUESTIONS:
        await update.message.reply_text(
            "⚠️ Abhi koi questions upload nahi hain!\await update.message.reply_text(
        "🇬🇧 UK Visa Interview Practice Bot me aapka swagat hai!\n\n"
        "🔹 Sawal aane par apna answer Voice Note (bolkar) bhejein.\n"
        "🔹 Nayi file lagane ke liye sirf .txt file send kar dein.\n"
        "🔹 Sabhi sawal hatane ke liye /delete dabayein.\n\n"
        "Pehla sawal niche dekhein 👇"
    )
    await ask_question(update, context)

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_datan\n"
            "👉 Aap seedha apni .txt file yahan send karein, bot automatic ise save kar lega."
        )
        return

    await update.message.reply_text(
        f"🇬🇧 UK Visa Interview Practice Bot me aapka swagat hai!\n\n"
        f"📊["q_index"] = 0
    success, msg = reload_questions()
    if success and QUESTIONS:
        await Total Questions: {len(QUESTIONS)}\n"
        "🔹 Sawal aane par apna answer Voice Note ( update.message.reply_text(f"🔄 Reset Successful!\n\n{msg}")
        await askbolkar) bhejein.\n"
        "🔹 Nayi file lagane ke liye sirf .txt file send kar dein.\n"
        "🔹 Sabhi sawal hatane ke liye /delete dabayein.\_question(update, context)
    else:
        await update.message.reply_text(f"ℹ️ {msg}\n\nKripya pehle questions wali .txt file bhejein.")

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global QUESTIONS
    if not is_admin(update.effective_usern\n"
        "Pehla sawal niche dekhein 👇"
    )
    await ask_question(update, context)

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q_index"] = 0
    success, msg =.id):
        await update.message.reply_text("❌ Aapko delete karne ki permission nahi hai!")
        return

    status_msg = await update.message.reply_text("⏳ GitHub se file delete ho reload_questions()
    
    if success and QUESTIONS:
        await update.message.reply_text(f"🔄 Reset Successful!\n\n{msg}")
        await ask_question(update, context)
    else:
        # QUESTIONS ko zero kar dein agar koi question nahi bacha
        context.user_data["q_index"] = 0
        await update.message.reply_text(
            f"ℹ️ {msg}\n\ rahi hai...")
    success, msg = delete_file_from_github()

    # Memory aur local disk dono se questions hamesha saaf karein
    QUESTIONS = []
    context.user_data["q_index"] = 0
n"
            "Abhi bot me 0 questions hain. Naya interview shuru karne ke liye `.txt` file bhejein!"
        )

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global QUESTIONS
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("    if os.path.exists("questions.txt"):
        try: os.remove("questions.txt")
        except: pass

    if success:
        await status_msg.edit_text("🗑️ Sabhi Questions Delete ho gaye! Ab bot bilkul khali hai.")
    else:
        await status_msg.edit_text(f"⚠️ Warning: {msg}\nLekin Bot memory se questions hata diye gaye hain.")

async def handle_document❌ Aapko delete karne ki permission nahi hai!")
        return

    status_msg = await update.message.reply_text("⏳(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global QUESTIONS
    if not is_ Questions delete kiye ja rahe hain...")
    success, msg = delete_file_from_github()

    # Memory aur Local File ko hamesha empty karein
    QUESTIONS = []
    context.user_data["q_index"] = 0
    if os.path.exists("questions.txt"):
        try:
admin(update.effective_user.id):
        await update.message.reply_text("❌ Aapko file upload karne ki permission nahi hai!")
        return

    doc = update.message.document
    if not doc.file_name.lower().endswith(".txt"):
        await update.message.reply_text("⚠️            os.remove("questions.txt")
        except Exception:
            pass

    if success:
         Kripya sirf .txt format wali file hi bhejein!")
        return

    status_msg = await update.message.reply_text("📥 File download ho rahi hai...")
    
    try:
        file = await doc.get_file()
        file_bytes = await file.download_as_bytearray()
        content_text = file_bytes.decode("utf-8", errors="ignore")
    except Exceptionawait status_msg.edit_text("🗑️ Sabhi Questions Delete ho gaye! Ab bot bilkul khali hai.")
    else:
        await status_msg.edit_text(f"⚠️ Notice: {msg}\n(Bot as e:
        await status_msg.edit_text(f"❌ File download error: {str(e)}")
        return

    parsed = parse_questions_content(content_text)
    if not parsed:
        await status_msg.edit_text(
            "❌ File me Q: aur A: format ke questions nahi mile!\n"
            "Format example:\n\nQ: Why UK?\nA: Because ki memory aur local file clear kar di gayi hai)")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global QUESTIONS
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Aapko file upload karne ki permission nahi hai!")
        ...\n---"
        )
        return

    await status_msg.edit_text("🚀 GitHub par automatically upload kiya jaa raha hai...")

    success, msg = upload_file_to_github(file_bytes)
    if success:
        QUESTIONS = parsed
        context.user_data["q_index"] = 0
        with openreturn

    doc = update.message.document
    if not doc.file_name.lower().endswith(".("questions.txt", "w", encoding="utf-8") as f:
            f.write(contenttxt"):
        await update.message.reply_text("⚠️ Kripya sirf .txt format wali file hi_text)

        await status_msg.edit_text(
            f"✅ File Successfully GitHub Par Save Ho bhejein!")
        return

    status_msg = await update.message.reply_text("📥 File download ho rahi hai...")
    
    try:
        file = await doc.get_file()
        file_bytes = await file.download_as_bytearray()
        content_text = file_bytes.decode("utf-8", errors="ignore")
    except Exception Gayi!\n\n"
            f"📊 Kul {len(QUESTIONS)} questions load ho chuke hain.\n"
            f"Interview shuru karne ke liye /start dabayein."
        )
    else:
        await status as e:
        await status_msg.edit_text(f"❌ File download error: {str(_msg.edit_text(f"❌ Upload Failed:\n{msg}")

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not QUESTIONS:
        await update.effective_chat.send_e)}")
        return

    parsed = parse_questions_content(content_text)
    if not parsed:
        await status_msg.edit_text(
            "❌ File me Q: aur A: format ke questions nahi mile!\n\n"
            "Format example:\n"
            "Q: Why UK?\n"
            "A: Because...\n"
            "---"
        )
        return

    awaitmessage("⚠️ Abhi koi questions nahi hain. Kripya pehle .txt file upload karein.")
        return

     status_msg.edit_text("🚀 GitHub par automatically upload kiya jaa raha hai...")

    success, msg = upload_file_to_github(file_bytes)
    if success:
        QUESTIONS = parsed
        context.user_data["q_index"] = 0
        with open("questions.txt", "idx = context.user_data.get("q_index", 0)
    if idx < len(QUESTIONS):
        q_text = QUESTIONS[idx]["question"]
        msg = f"🎙️ Question {idx + 1}/{len(QUESTIONS)}:\n\n👉 {q_text}\n\n(Apna answer bolkar Voice Note bhejein)"
        if update.message:
            await update.message.w", encoding="utf-8") as f:
            f.write(content_text)

        awaitreply_text(msg)
        else:
            await update.effective_chat.send_message(msg)
    else:
        await update.effective_chat.send_message(
            "🎉 Interview Complete!\nNaye questions upload karne ke liye file bhejein ya /reset dabayein."
        )

 status_msg.edit_text(
            f"✅ File Successfully GitHub Par Save Ho Gayi!\n\n"
            f"📊 Kul {len(QUESTIONS)} questions load ho chuke hain.\n"
            f"Interview shuru karne ke liye /start dabayein."
        )
    else:
        await status_msg.edit_text(f"❌ Upload Failed:\n{msg}")

async def ask_question(updateasync def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = context.user_data.get("q_index", 0)
    if not QUESTIONS or idx >= len(QUESTIONS):
        await update.message.reply_text("Koi active interview nahi hai. Shuru karne ke liye /start dabayein.")
        return

    status_msg = await update.message.reply_text("⏳ Processing audio...")

    voice_file = await update.message.voice.get_file()
    user_id = update.message: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = context.user_data.get("q_index", 0)
    if idx < len(QUESTIONS):
        q_text = QUESTIONS[idx]["question"]
        msg = f".from_user.id
    oga_path = f"temp_{user_id}.oga"
    wav_path = f"temp_{user_id}.wav"
    await voice_file.download_to🎙️ Question {idx + 1}/{len(QUESTIONS)}:\n\n👉 {q_text}\n_drive(oga_path)

    try:
        audio = AudioSegment.from_file(oga_path)
        audio.\n(Apna answer bolkar Voice Note bhejein)"
        if update.message:
            awaitexport(wav_path, format="wav")
    except Exception as e:
        await status_msg.edit_text(f"❌ Audio convert error: {str(e)}")
        if os.path.exists update.message.reply_text(msg)
        else:
            await update.effective_chat.send_message(msg)
    else:
        await update.effective_chat.send_message(
            "🎉 Interview Complete!\nNaye questions upload karne ke liye file bhejein ya /reset dabayein."
        )

async def handle(oga_path): os.remove(oga_path)
        return

    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            user_text = recognizer.recognize_google(audio_data, language="en-GB")
    except sr.UnknownValueError:
        await status_msg.edit_text("❌ Aapki aawaz saaf nahi aayi. Kripya dubara bolkar bhejein.")
        if os.path_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = context.user_data.get("q_index", 0)
    if not QUESTIONS or idx >= len(QUESTIONS):
        await update.message.reply.exists(oga_path): os.remove(oga_path)
        if os.path.exists(wav_path): os.remove(wav_path)
        return
    except Exception as e:
        _text("⚠️ Koi active question nahi hai. Naye sawal daalne ke liye .txt file bhejein ya /startawait status_msg.edit_text(f"❌ Error: {str(e)}")
        if os.path.exists(oga_path): os.remove(oga_path)
        if os.path.exists(wav_path): os.remove(wav_path)
        return

    if os.path.exists(oga_path): os.remove(oga_path)
    if os.path.exists(wav_path): os.remove(wav_path)

    expected_answer = QUESTIONS[idx]["answer"]
     dabayein.")
        return

    status_msg = await update.message.reply_text("⏳ Processing audio...")

    voice_file = await update.message.voice.get_file()
    user_id = update.message.from_user.id
    oga_path = f"temp_{user_id}.oga"
    clean_user = " ".join(user_text.lower().split())
    clean_exp = " ".join(expected_answer.lower().split())
    similarity = difflib.SequenceMatcher(None, clean_user, clean_exp).ratio() * 100

    feedback = (
        f"🗣wav_path = f"temp_{user_id}.wav"
    await voice_file.download_to_drive(oga_path)

    try:
        audio = AudioSegment.from_file(oga_path)
        audio.️ Aapne bola:\n\"{user_text}\"\n\n"
        f"✅ Expected Answer:\n\"{expected_answer}\"\n\n"
        f"📊 Accuracy Score: {similarity:.1f}%"
    )
    await status_msg.edit_text(feedback)

    context.user_data["q_index"] = idx + 1
    await ask_question(update, context)

def main():
    export(wav_path, format="wav")
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
        if os.path.exists(oga_path):server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()

    ping_thread = threading.Thread(target=auto_keep_alive_ping, daemon=True)
    ping_thread.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler os.remove(oga_path)
        if os.path.exists(wav_path): os.remove(wav_path)
        return
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")
        if os.path.exists(oga_path): os.remove(oga_path)
        if os.path.exists(wav_path): os.(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("reload", reset_command))
    app.add_handler(CommandHandler("delete", delete_command))
    
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandlerremove(wav_path)
        return

    if os.path.exists(oga_path): os.(filters.VOICE, handle_voice))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
