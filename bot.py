import os
import re
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
from pydub import Audio
    server = HTTPServer(("0.0.0.0", port), PingServerHandler)
    print(f"Segment
import imageio_ffmpeg

# Set ffmpeg path for pydub
AudioSegment.converter = image[Web-Server] Health Check Server running on port {port}")
    server.serve_forever()

def auto_keep_alive_ping():
    """
    Render Free Tier 15 minutes inactive hone par sleep mode me chala jata hai.
    Yeio_ffmpeg.get_ffmpeg_exe()

# ==================== CONFIGURATIONS ====================
BOT_ loop har 3 minute (180s) me Render ke external URL par request bhej kar use 24/7 jagTOKEN = os.getenv("BOT_TOKEN", "").strip()

# Render ka External Live URL (Jaise: https://your-bot-name.onrender.com)
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URLaye rakhta hai.
    """
    time.sleep(15)  # App start hone ka thoda wait karein", "").strip()

# GitHub Configurations
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip() 
GITHUB_REPO = os.getenv("GITHUB_REPO", "singhji9784-c
    print("[Keep-Alive] Self-ping background service initiated.")

    while True:
        target_url = RENDER_EXTERNAL_myk/UK").strip()
GITHUB_FILE_PATH = os.getenv("GITHUB_FILE_PATH", "questions.txt").strip()
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main").stripURL
        if target_url:
            if not target_url.startswith("http://") and not target_url.startswith("https://"):
                target_url = f"https://{target_url}"

()

# Admin check (khali chhodne par sab use kar sakte hain)
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()

QUESTIONS = []

# Basic English Stopwords (Keywords filter karne ke liye            try:
                headers = {"User-Agent": "Render-KeepAlive-Worker/2.0"}
                res = requests.)
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "get(target_url, headers=headers, timeout=20)
                print(f"[Keep-Alive] Pingas", "at", "be", "because", "been", "before", "being", "below", " sent to {target_url} -> Status: {res.status_code}")
            except Exception as e:
                printbetween", "both", "but", 
    "by", "can", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", (f"[Keep-Alive] Warning: Ping failed ({e})")
        else:
            print("
    "from", "further", "had", "has", "have", "having", "he", "[Keep-Alive] ⚠️ WARNING: RENDER_EXTERNAL_URL set nahi hai! Render Environment variables me ise add karein taher", "here", "hers", "herself", 
    "him", "himself", "hisaki bot sleep na ho.")

        # Har 3 minute (180 seconds) me loop chalega (Render 15 min me", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", 
    "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", 
    "or", "other", "our", "ours", "ourselves", "out", sota hai)
        time.sleep(180)

# ==================== 2. GITHUB API FUNCTIONS ================= "over", "own", "same", "she", "should", 
    "so", "some",===
def get_github_headers():
    headers = {
        "Accept": "application/vnd. "such", "than", "that", "the", "their", "theirs", "them", "themselves", "github+json",
        "User-Agent": "UKVisa-Telegram-Bot",
        "X-then", 
    "there", "these", "they", "this", "those", "through", "to", "tooGitHub-Api-Version": "2022-11-28"
    }
    if", "under", "until", "up", 
    "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers

def get_github_file", 
    "with", "would", "you", "your", "yours", "yourself", "yourselves"
}():
    """Live GitHub API se direct data lata hai taaki CDN cache issue na ho"""
    if not GITHUB_TOKEN:
        return None, None
    url = f"https://api.github.com

# ==================== 1. KEEP-ALIVE HTTP SERVER & AUTO-PING ====================
class Ping/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}?ref={GITHUB_BRANCH}"
    try:
        res = requests.get(url, headers=get_github_headers(), timeout=10)
        if resServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        .status_code == 200:
            data = res.json()
            content_b6self.end_headers()
        self.wfile.write(b"OK - Bot is alive and active4 = data.get("content", "")
            raw_text = base64.b64decode(!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        # Consolecontent_b64).decode("utf-8", errors="ignore")
            return raw_text, data.get("sha")
        elif res.status_code == 404:
            return False, None
    except Exception as e:
        print(f"GitHub fetch error: {e}")
    return None, None

def get_github_file_sha():
    _, sha = get_github_file()
    return sha

def upload me bekar ke ping logs na bharein
        return

def run_web_server():
    port = int_file_to_github(file_bytes):
    if not GITHUB_TOKEN:
        return False,(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0. "GITHUB_TOKEN Render me set nahi hai!"

    sha = get_github_file_sha()
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    
    b64_content = base64.b64encode(file_bytes).0.0", port), PingServerHandler)
    print(f"[Web Server] Keep-Alive Server listening on port {port}")
    server.serve_forever()

def auto_keep_alive_ping():
decode("utf-8")
    payload = {
        "message": "Update questions via Telegram Bot",
    """Har 5 minute (300s) me Render ke external URL par HTTP call bhejta hai taaki server sleep        "content": b64_content,
        "branch": GITHUB_BRANCH
    }
    if sha:
        payload["sha"] = sha

    try:
        res = requests.put(url na ho"""
    time.sleep(20)  # Bot start hone ke 20s baad pehla ping shuru hoga
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10, headers=get_github_headers(), json=payload, timeout=15)
        if res.status_code in [200, 201]:
            return True, "File GitHub par successfully save ho gayi!"
        elif.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 KeepAliveBot/ res.status_code == 404:
            return False, f"GitHub Repo nahi mili! Check karein: '{GITHUB_REPO}'"
        else:
            return False, f"GitHub Error ({res.status_code}): {res.text}"
    except Exception as e:
        return False, f"2.0"
    }

    while True:
        target_url = RENDER_EXTERNAL_URL
        if target_url:Upload Connection Error: {str(e)}"

def delete_file_from_github():
    if not GITHUB_TOKEN:
        return False, "GITHUB_TOKEN set nahi hai!"

    sha = get_github_file_sha()
    if not sha:
        return True, "File pehle se GitHub par nahi hai."

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    payload = {
        "message": "Deleted questions.txt via Telegram Bot",
        "sha": sha,
        "branch": GITHUB_BRANCH
    }

    try:
            # Agar user ne 'https://' nahi lagaya ho toh jod do
            if not target_url.startswith("http://") and not target_url.startswith("https://"):
                target_url = f"https://{target_url}"
            
            try:
                res = requests.get(target_
        res = requests.delete(url, headers=get_github_headers(), json=payload, timeout=15)
        if res.status_code in [200, 204]:
            return True, "File GitHub seurl, headers=headers, timeout=15)
                current_time = time.strftime("%H:%M:%S delete ho gayi!"
        elif res.status_code == 404:
            return True, "File pehle se delete ho chuki hai."
        else:
            return False, f"GitHub Error ({")
                print(f"[{current_time}] [Keep-Alive] Ping sent to {target_url} ->res.status_code}): {res.text}"
    except Exception as e:
        return False, f"Delete Connection Error: {str(e)}"

# ==================== 3. QUESTIONS PARSER & RELO Status: {res.status_code}")
            except Exception as e:
                print(f"[Keep-Alive ERROR] Ping request fail: {e}")
        else:
            print("[Keep-Alive WARNING] 'RENDER_EXTERNALAD ====================
def parse_questions_content(content):
    if not content:
        return []
    entries = content.split("---")
    qa_list = []
    for entry in entries:
        entry = entry._URL' set nahi hai! Render 15 min baad sleep ho jayega. Environment Variables me set karein!")

strip()
        if not entry:
            continue
        if "Q:" in entry and "A:" in entry:
            parts = entry.split("A:", 1)
            q_part = parts        # Har 5 minute (300 seconds) me ping karega
        time.sleep(300)

# ==================== 2. GITHUB API FUNCTIONS ====================
def get_github_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent":[0].replace("Q:", "", 1).strip()
            a_part = parts[1].strip()
            if q_part and a_part:
                qa_list.append({
                    "question": q "UKVisa-Telegram-Bot",
        "X-GitHub-Api-Version": "2022_part,
                    "answer": a_part
                })
    return qa_list

def reload_questions():
    global QUESTIONS
    QUESTIONS = []

    if GITHUB_TOKEN:
        content, sha = get_github_file()
        if content is False:
            if os.path.exists("questions.txt"):
                try: os.remove("questions.txt")
                except: pass
            return False, "GitHub par file nahi mili-11-28"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers

def get_github_file():
    """Live GitHub API se direct data lata hai taaki CDN cache issue na ho"""
    if not GITHUB_TOKEN:
        return None, None
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB (Deleted). Sabhi questions clear hain!"
        elif content:
            parsed = parse_questions_content(_FILE_PATH}?ref={GITHUB_BRANCH}"
    try:
        res = requests.get(url, headers=get_github_content)
            QUESTIONS = parsed
            with open("questions.txt", "w", encoding="utf-8") as f:
                f.write(content)
            if QUESTIONS:
                return True, f"headers(), timeout=10)
        if res.status_code == 200:
            data = res.json()
            content_b64 = data.get("content", "")
            raw_text = base64.b64decode(content_b64).decode("utf-8", errorsGitHub se {len(QUESTIONS)} questions load ho gaye!"
            else:
                if os.path.exists("questions.txt"):
                    try: os.remove("questions.txt")
                    except: pass
                return False, "File khali hai, koi question nahi mila."

    if os.path.exists("questions="ignore")
            return raw_text, data.get("sha")
        elif res.status_code.txt"):
        try:
            with open("questions.txt", "r", encoding="utf-8") as f:
                parsed = parse_questions_content(f.read())
            QUESTIONS = parsed
            if QUESTIONS:
                return True, f"Local file se {len(QUESTIONS)} questions load ho gaye!"
        except Exception as e:
            print(f"Local read error: {e}")

    QUESTIONS = == 404:
            return False, None
    except Exception as e:
        print(f"GitHub fetch error: {e}")
    return None, None

def get_github_file_sha():
    _, sha = get_github_file()
    return sha

def upload_file_to_github(file_bytes):
     []
    return False, "Koi questions nahi mile! Bot abhi poori tarah khali hai."

reload_questions()
recognizer = sr.Recognizer()

def is_admin(user_id):
    ifif not GITHUB_TOKEN:
        return False, "GITHUB_TOKEN Render me set nahi hai!"

    sha = get_github_file_sha()
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    
    b64_content = not ADMIN_ID:
        return True
    return str(user_id) == str(ADMIN_ID base64.b64encode(file_bytes).decode("utf-8")
    payload = {)

# ==================== 4. SPEECH EVALUATION ENGINE ====================
def extract_keywords(text
        "message": "Update questions via Telegram Bot",
        "content": b64_content,
        "branch": GITHUB_):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

def evaluate_speech(BRANCH
    }
    if sha:
        payload["sha"] = sha

    try:
        res = requests.put(url, headers=get_github_headers(), json=payload, timeout=15)
        if res.status_user_text, expected_answer, audio_duration_sec, google_confidence):
    # 1. Fluency & WPM Calculation
    duration_sec = max(1.0, audio_duration_sec)
    spoken_words = user_text.strip().split()
    word_count = len(spoken_words)
    wpm =code in [200, 201]:
            return True, "File GitHub par successfully save ho gayi!"
        elif res.status_code == 404:
            return False, f"GitHub int((word_count / duration_sec) * 60)

    # Visa/IELTS Interview Standard Repo nahi mili! Check karein: '{GITHUB_REPO}'"
        else:
            return False, f"GitHub Error ({res.status_code}): {res.text}"
    except Exception as e:
        return False, f"Upload Connection Speed: 110 - 150 WPM
    if 115 <= wpm <= 155:
        fluency_score = min(100.0, 92.0 + Error: {str(e)}"

def delete_file_from_github():
    if not GITHUB_TOKEN:
        return False, "GITHUB_TOKEN set nahi hai!"

    sha = get_github_file_sha()
    if not (8.0 * (1 - abs(135 - wpm) / 20.0)))
        fluency_remark = "🎯 Perfect Speaking Pace (Ekdum sahi speed)"
    elif 90 <= wpm < 11 sha:
        return True, "File pehle se GitHub par nahi hai."

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    payload5:
        fluency_score = 75.0 + ((wpm - 90) / 25.0) * 15.0
        fluency_remark = "🐢 Thoda slow tha, thodi flow badhayein"
    elif 155 < wpm <= 185:
        flu = {
        "message": "Deleted questions.txt via Telegram Bot",
        "sha": sha,
        "branch": GITHUB_BRANCH
    }

    try:
        res = requests.delete(url, headers=get_github_headers(), json=payload, timeout=15)
        if res.statusency_score = 75.0 + ((185 - wpm) / 30.0) * 15.0_code in [200, 204]:
            return True, "File GitHub se delete ho gayi!"
        elif res.status_code == 404:
            return True, "File pe
        fluency_remark = "⚡ Thoda fast tha, aaram se clear bole"
    elif wpm < 90:
        fluency_score = max(35.0, 45.hle se delete ho chuki hai."
        else:
            return False, f"GitHub Error ({res.status_code}): {res.text}"
    except Exception as e:
        return False, f"Delete0 + (wpm / 90.0) * 25.0)
        fluency_remark = "⚠️ Bahut ruk-ruk ke bola, bina dare flow me bole"
    else:
        fluency_score = max( Connection Error: {str(e)}"

# ==================== 3. QUESTIONS PARSER & RELOAD ====================
def parse_questions_content(content):
    if not content:
        return []
    40.0, 70.0 - ((wpm - 185) / 50.0) * 25.0)
        fluency_remark = "⚠️ Bahut jyada teentries = content.split("---")
    qa_list = []
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        if "Q:" in entry and "A:" in entry:
            parts = entry.split("A:", 1)
            q_partzi se bola, shanti se bole"

    # 2. Accuracy & Content Matching (Keywords + Sequence)
    clean_user = " ".join(user_text.lower().split())
    clean_exp = " ".join(expected_answer.lower().split())
    seq_ratio = difflib.SequenceMatcher(None, = parts[0].replace("Q:", "", 1).strip()
            a_part = parts[1].strip()
            if q_part and a_part:
                qa_list.append({
                     clean_user, clean_exp).ratio() * 100

    exp_keywords = list(dict.fromkeys(extract_keywords(expected_answer)))
    user_words_set = set(extract_keywords(user_text))

    covered_keywords ="question": q_part,
                    "answer": a_part
                })
    return qa_list

def reload_questions():
    global QUESTIONS
    QUESTIONS = []

    if GITHUB_TOKEN:
        content, sha = [w for w in exp_keywords if w in user_words_set]
    missed_keywords = [w for w in exp_keywords if w not in user_words_set]

    if exp_keywords:
        kw_ratio = (len(covered_ get_github_file()
        if content is False:
            if os.path.exists("questions.txt"):
                try: os.remove("questions.txt")
                except: pass
            return False, "GitHub par file nahi milikeywords) / len(exp_keywords)) * 100
        # Accuracy is 65% based on Key Points and 35% on Sentence Formation
        accuracy_score = (kw_ratio * 0.65) + (seq_ratio * 0.35)
    else:
        accuracy_score = seq_ratio

    accuracy_score = min(100.0, max(0.0, accuracy_score))

    # 3. Pronunciation & Clarity Score
    if google_confidence is not (Deleted). Sabhi questions clear hain!"
        elif content:
            parsed = parse_questions_content(content)
            QUESTIONS = parsed
            with open("questions.txt", "w", encoding="utf-8") as f:
                f.write(content)
            if QUESTIONS:
                return True, f"GitHub se {len(QUESTIONS)} questions load ho gaye!"
            else:
                if os.path.exists("questions.txt"):
                    try: os.remove("questions.txt")
                    except: pass
                 None and google_confidence > 0:
        pronun_score = min(100.0, google_confidence * 1return False, "File khali hai, koi question nahi mila."

    if os.path.exists("questions00)
    else:
        pronun_score = min(95.0, max(60.0, 70.0 + (accuracy_score * 0.25)))

    if pronun_score >= 85:
        pronun_remark = "🌟 Clear & Natural Accent (Sp.txt"):
        try:
            with open("questions.txt", "r", encoding="utf-8") as f:
                parsed = parse_questions_content(f.read())
            QUESTIONS = parsed
            if QUESTIONS:
                return True, f"Local file se {len(QUESTIONS)} questions load ho gaye!"
        except Exception as e:
            print(f"Local read error: {e}")

    QUESTIONS =asht Aawaz)"
    elif pronun_score >= 70:
        pronun_remark = "👍 Good, thoda aur clarity laane ki koshish karein"
    else:
         []
    return False, "Koi questions nahi mile! Bot abhi poori tarah khali hai."

reloadpronun_remark = "⚠️ Words ko thoda aur saaf aur khol kar bole"

    # 4. Overall Interview Score
    overall_score = (accuracy_score * 0.40) + (fluency_score * 0.30) + (pronun_score * 0.30)_questions()
recognizer = sr.Recognizer()

def is_admin(user_id):
    if not ADMIN_ID:
        return True
    return str(user_id) == str(ADMIN_ID)

# ==================== 4. SPEECH EVALUATION ENGINE ====================
def extract_keywords(text):
    words = re.
    
    if overall_score >= 85:
        grade = "A (Excellent - Visa Ready 🇬🇧)"
    elif overall_score >= 70:
        grade = "B (Good -findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

def evaluate_speech(user_text, expected Minor Practice Needed)"
    elif overall_score >= 55:
        grade = "C (Average - More Practice Required)"
    else:
        grade = "D (Needs Improvement)"

    return {
        "_answer, audio_duration_sec, google_confidence):
    # 1. Fluency & WPM Calculation
    duration_sec = max(1.0, audio_duration_sec)
    spoken_wordsoverall": overall_score,
        "grade": grade,
        "accuracy": accuracy_score,
        "fluency": fluency_score,
        "fluency_remark": fluency_remark,
        "pronun": pronun_score,
        "pronun_remark": pronun_remark,
        "wpm": wpm,
        "duration": duration_sec,
        "covered": covered_keywords,
        "missed": = user_text.strip().split()
    word_count = len(spoken_words)
    wpm = int((word_count / duration_sec) * 60)

    # Visa/IELTS missed_keywords,
        "total_kw": len(exp_keywords)
    }

# ================= Interview Standard Speed: 115 - 155 WPM
    if 115 <= w=== 5. BOT HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q_index"] = 0
    reload_questions()

    if not QUESTIONS:
        await update.message.reply_text(
            "⚠️ Abhi koi questions upload nahi hain!\n\n"
            "👉 Nayi .txt file bhejein jisme questions ho."
        )pm <= 155:
        fluency_score = min(100.0, 92.0 + (8.0 * (1 - abs(135 - wpm) / 20.0)))
        fluency_remark = "🎯 Perfect Speaking Pace (Ekdum sahi speed)"
    elif 90 <= wpm < 115:
        fluency_score = 75.0 + ((wpm -
        return

    await update.message.reply_text(
        f"🇬🇧 UK Visa Interview Practice 90) / 25.0) * 15.0
        fluency_remark = "🐢 Thoda slow tha, thodi flow badhayein"
    elif 155 < w Bot me aapka swagat hai!\n\n"
        f"📊 Total Questions: {len(QUESTIONS)}\n"pm <= 185:
        fluency_score = 75.0 + ((185
        "🔹 Sawal aane par apna answer Voice Note (bolkar) bhejein.\n"
        "🔹 Bot aapko Accuracy, Fluency, Pronunciation aur WPM ka scorecard dega.\n"
        "🔹 Nayi file lagane ke liye sirf .txt file send kar dein.\n\n"
        "Pehla sawal niche dekhein 👇"
    )
    await ask_question(update, context)

async def reset - wpm) / 30.0) * 15.0
        fluency_remark = "⚡ Thoda fast tha, aaram se clear bole"
    elif wpm < 90:
        fluency_score = max(35.0, 45.0 + (wpm / 90.0) * 25.0)
        fluency_remark = "⚠️ Bahut ruk-_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_dataruk ke bola, bina dare flow me bole"
    else:
        fluency_score = max(40.0, 70["q_index"] = 0
    success, msg = reload_questions()
    
    if success and QUESTIONS:
        await update.message.reply_text(f"🔄 Reset Successful!\n\n{msg}")
        await ask_question(update, context)
    else:
        context.user_data.0 - ((wpm - 185) / 50.0) * 25.["q_index"] = 0
        await update.message.reply_text(
            f"ℹ️ {msg}\n\n"
            "Abhi bot me 0 questions hain. Naya interview shuru karne ke liye `.txt` file0)
        fluency_remark = "⚠️ Bahut jyada tezi se bola, shanti se bole"

    # 2. Accuracy & Content Matching (Keywords + Sequence)
    clean_user = " ".join(user_text.lower().split())
    clean_exp = " ".join(expected_answer.lower().split bhejein!"
        )

async def delete_command(update: Update, context: ContextTypes.DEFAULT())
    seq_ratio = difflib.SequenceMatcher(None, clean_user, clean_exp)._TYPE):
    global QUESTIONS
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Aapko delete karne ki permission nahi hai!")
        return

    status_msg = await update.message.reply_text("⏳ Questions delete kiye ja rahe hain...")
    success, msg = delete_ratio() * 100

    exp_keywords = list(dict.fromkeys(extract_keywords(expected_answer)))
    user_words_set = set(extract_keywords(user_text))

    file_from_github()

    QUESTIONS = []
    context.user_data["q_index"] = 0
    if os.path.exists("questions.txt"):
        try: os.remove("questionscovered_keywords = [w for w in exp_keywords if w in user_words_set]
    missed_keywords = [w for w in exp_keywords if w not in user_words_set]

    if.txt")
        except: pass

    if success:
        await status_msg.edit_text("🗑️ Sabhi Questions Delete ho gaye! Ab bot bilkul khali hai.")
    else:
        await exp_keywords:
        kw_ratio = (len(covered_keywords) / len(exp_keywords)) status_msg.edit_text(f"⚠️ Notice: {msg}\n(Bot ki memory aur local file clear kar di gayi hai)")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global QUESTIONS
    if not is_admin(update.effective_user.id):
         * 100
        accuracy_score = (kw_ratio * 0.65) + (seq_ratio * 0.35)
    else:
        accuracy_score = seq_ratio

    accuracy_score = min(100.0, max(0.0, accuracy_score))

    # 3. Pronunciation & Clarity Score
    if google_confidence is not None and google_confidence >await update.message.reply_text("❌ Aapko file upload karne ki permission nahi hai!")
        return

    doc = update.message.document
    if not doc.file_name.lower().endswith(".txt"):
        await update.message.reply_text("⚠️ Kripya sirf .txt format wali file hi bhejein!")
         0:
        pronun_score = min(100.0, google_confidence * 100)
    else:
        pronun_score = min(95.0, max(6return

    status_msg = await update.message.reply_text("📥 File download ho rahi hai...")
0.0, 70.0 + (accuracy_score * 0.25)))

    if pronun_score >= 85:
        pronun_remark = "🌟 Clear & Natural Accent (Sp    
    try:
        file = await doc.get_file()
        file_bytes = await file.download_as_bytearray()
        content_text = file_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        await status_msg.edit_text(f"asht Aawaz)"
    elif pronun_score >= 70:
        pronun_remark❌ File download error: {str(e)}")
        return

    parsed = parse_questions_content(content = "👍 Good, thoda aur clarity laane ki koshish karein"
    else:
        _text)
    if not parsed:
        await status_msg.edit_text(
            "❌ File me Q: aur A: format ke questions nahi mile!\n\n"
            "Format example:\n"
            "Q: Why UK?\n"
            "A: Because...\n"
            "---"
        )
        return

    await status_msg.edit_text("🚀 GitHub par automatically upload kiya jaa raha haipronun_remark = "⚠️ Words ko thoda aur saaf aur khol kar bole"

    # 4. Overall Interview Score
    overall_score = (accuracy_score * 0.40) + (fluency_score * 0.30) + (pronun_score * 0.30)
    
    if overall_score >= 85:
        grade = "A (Excellent - Visa Ready...")

    success, msg = upload_file_to_github(file_bytes)
    if success:
        QUESTIONS = parsed
        context.user_data["q_index"] = 0
        with open 🇬🇧)"
    elif overall_score >= 70:
        grade = "B (Good -("questions.txt", "w", encoding="utf-8") as f:
            f.write(content_text)

         Minor Practice Needed)"
    elif overall_score >= 55:
        grade = "C (Average - More Practice Required)"
    else:
        grade = "D (Needs Improvement)"

    return {
        await status_msg.edit_text(
            f"✅ File Successfully GitHub Par Save Ho Gayi!\n\n"
            f"📊 Kul {len(QUESTIONS)} questions load ho chuke hain.\n"
            "overall": overall_score,
        "grade": grade,
        "accuracy": accuracy_score,
f"Interview shuru karne ke liye /start dabayein."
        )
    else:
        await status_msg.edit_text(f"❌ Upload Failed:\n{msg}")

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not QUESTIONS:
        await update.effective_chat.send        "fluency": fluency_score,
        "fluency_remark": fluency_remark,
        "_message("⚠️ Abhi koi questions nahi hain. Kripya pehle .txt file upload karein.")
        return

    idx = context.user_data.get("q_index", 0)
    ifpronun": pronun_score,
        "pronun_remark": pronun_remark,
        "wpm": wpm,
        "duration": duration_sec,
        "covered": covered_keywords,
        "missed": missed_keywords,
        "total_kw": len(exp_keywords)
    }

# ================= idx < len(QUESTIONS):
        q_text = QUESTIONS[idx]["question"]
        msg = f"=== 5. BOT HANDLERS ====================
async def start(update: Update, context: ContextTypes🎙️ Question {idx + 1}/{len(QUESTIONS)}:\n\n👉 {q_text}\n\n(Apna answer bolkar Voice Note bhejein)"
        if update.message:
            await update.message.reply_text(msg)
        else:
            await update.effective_chat.send_message(msg)
    else:
        await update.effective_chat.send_message(
            .DEFAULT_TYPE):
    context.user_data["q_index"] = 0
    reload_questions()

    if not QUESTIONS:
        await update.message.reply_text(
            "⚠️ Abhi koi questions upload nahi hain!\n\n"
            "👉 Nayi .txt file bhejein jisme questions ho."
        )"🎉 Interview Complete!\nNaye questions upload karne ke liye file bhejein ya /reset dabayein."
        )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = context.user_data.get("q_index", 0)
    if not QUESTIONS or idx >= len(QUESTIONS):
        await update.message.reply
        return

    await update.message.reply_text(
        f"🇬🇧 UK Visa Interview Practice_text("⚠️ Koi active question nahi hai. Naye sawal daalne ke liye .txt file bhejein ya /start dabayein.")
        return

    status_msg = await update.message.reply_text("⏳ Processing speech & evaluating metrics Bot me aapka swagat hai!\n\n"
        f"📊 Total Questions: {len(QUESTIONS)}\n"
        "🔹 Sawal aane par apna answer Voice Note (bolkar) bhejein.\n...")

    voice_file = await update.message.voice.get_file()
    user_id = update.message.from_"
        "🔹 Bot aapko Accuracy, Fluency, Pronunciation aur WPM ka scorecard dega.\n"
        "🔹 Nayiuser.id
    oga_path = f"temp_{user_id}.oga"
    wav_path file lagane ke liye sirf .txt file send kar dein.\n\n"
        "Pehla sawal niche dekhein 👇"
    )
    await ask_question(update, context)

async def reset = f"temp_{user_id}.wav"
    await voice_file.download_to_drive(oga_path)

    audio_duration = 0.0
    try:
        audio = AudioSegment.from_file(oga_path)
        audio_duration = len(audio) / 1000.0  # seconds me
        audio.export(wav_path, format="wav")
    except Exception as e:
_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q_index"] = 0
    success, msg = reload_questions()
    
    if success and        await status_msg.edit_text(f"❌ Audio convert error: {str(e)}")
        if os.path.exists(oga_path): os.remove(oga_path)
        return

     QUESTIONS:
        await update.message.reply_text(f"🔄 Reset Successful!\n\n{msguser_text = ""
    google_confidence = None

    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            result = recognizer.recognize_google(audio_data, language="en-GB", show_all=True)
            
            if not result or not isinstance(result, dict) or not result.get("alternative"):
                raise sr.UnknownValueError()
            
            best_match = result["alternative"][0]
            user_text =}")
        await ask_question(update, context)
    else:
        context.user_data["q_index"] = 0
        await update.message.reply_text(
            f"ℹ️ best_match.get("transcript", "").strip()
            google_confidence = best_match.get("confidence", None)

    except sr.UnknownValueError:
        await status_msg.edit_text("❌ Aap {msg}\n\n"
            "Abhi bot me 0 questions hain. Naya interview shuru karne keki aawaz saaf nahi aayi. Kripya shanti wali jagah se dubara bolkar bhejein.")
        if os.path.exists(oga_path): os.remove(oga_path)
        if os.path.exists(wav_path): os.remove(wav_path)
        return
    except Exception as e:
        await status_msg.edit_text(f"❌ Speech Error: liye `.txt` file bhejein!"
        )

async def delete_command(update: Update, context {str(e)}")
        if os.path.exists(oga_path): os.remove(oga_path)
        if os.path.exists(wav_path): os.remove(wav_path)
: ContextTypes.DEFAULT_TYPE):
    global QUESTIONS
    if not is_admin(update.effective_        return

    if os.path.exists(oga_path): os.remove(oga_path)
    if os.path.exists(wav_path): os.remove(wav_path)

    expected_answer = QUESTIONS[idx]["answer"]
    report = evaluate_speech(user_text, expected_answer, audio_duration, google_confidence)

    covered_str = ", ".join(report["covered"][:6]) if reportuser.id):
        await update.message.reply_text("❌ Aapko delete karne ki permission nahi hai["covered"] else "None"
    missed_str = ", ".join(report["missed"]!")
        return

    status_msg = await update.message.reply_text("⏳ Questions delete kiye ja rahe hain...")
    success, msg = delete_file_from_github()

    QUESTIONS = []
    context[:6]) if report["missed"] else "None (Sabhi bole 🎉)"

    feedback = (
        f"🗣️ *Aapne bola:*\n\"{user_text}\"\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏆 *OVERALL SCORE: {report['overall']:.1f}%*\n"
        f"🎖️ *Grade:* {report['grade']}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f".user_data["q_index"] = 0
    if os.path.exists("questions.txt🎯 *Accuracy (Content):* {report['accuracy']:.1f}%\n"
        f"🗣️ *Pronunciation:* {report['pronun']:.1f}% ({report['pronun_remark']})\n"
        f"⚡ *Fluency:* {report['fluency']:.1f}% ({report['wpm']} WPM)\n"
        f"⏱"):
        try: os.remove("questions.txt")
        except: pass

    if success:
️ *Duration:* {report['duration']:.1f}s | {report['fluency_remark']}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📌 *Key Points Analysis ({len(report['covered'])}/{report['total_kw']}):*\n"
        f"✅ *Covered:*        await status_msg.edit_text("🗑️ Sabhi Questions Delete ho gaye! Ab bot bilkul kh `{covered_str}`\n"
        f"❌ *Missed:* `{missed_str}`\n\ali hai.")
    else:
        await status_msg.edit_text(f"⚠️ Notice: {n"
        f"📖 *Expected Answer:*\n\"{expected_answer}\""
    )
    
    await status_msg.edit_text(feedback, parse_mode="Markdown")

    context.user_datamsg}\n(Bot ki memory aur local file clear kar di gayi hai)")

async def handle_document(update["q_index"] = idx + 1
    await ask_question(update, context)

# ==================== MAIN RUNNER ====================
def main():
    # 1. Start HTTP Server for Render Health Check
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread: Update, context: ContextTypes.DEFAULT_TYPE):
    global QUESTIONS
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Aapko file upload.start()

    # 2. Start Self-Ping Thread (Every 3 minutes)
    ping_thread = threading.Thread(target=auto_keep_alive_ping, daemon=True)
    ping_ karne ki permission nahi hai!")
        return

    doc = update.message.document
    if not doc.thread.start()

    # 3. Start Telegram Bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("reload", reset_command))
    app.add_handler(file_name.lower().endswith(".txt"):
        await update.message.reply_text("⚠️ Kripya sirf .txt format wali file hi bhejein!")
        return

    status_msg = await update.message.reply_text("📥CommandHandler("delete", delete_command))
    
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice File download ho rahi hai...")
    
    try:
        file = await doc.get_file()
        file_bytes = await file.download_as_bytearray()
        content_text = file_bytes))

    print("UK Visa Bot is active and polling...")
    app.run_polling()

if __name__ == "__.decode("utf-8", errors="ignore")
    except Exception as e:
        await status_msgmain__":
    main()
