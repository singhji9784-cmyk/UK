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
from pydub import AudioSegment
import imageio_ffmpeg

# Set ffmpeg path for pydub
AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()

# ==================== CONFIGURATIONS ====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Render Live URL (e.g., https://your-service-name.onrender.com)
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "").strip()

# GitHub Configurations
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip() 
GITHUB_REPO = os.getenv("GITHUB_REPO", "singhji9784-cmyk/UK").strip()
GITHUB_FILE_PATH = os.getenv("GITHUB_FILE_PATH", "questions.txt").strip()
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main").strip()

# Admin check (khali chhodne par sab use kar sakte hain)
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()

QUESTIONS = []

# Basic English Stopwords
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", 
    "by", "can", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", 
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", 
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", 
    "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", 
    "or", "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", 
    "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", 
    "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", 
    "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", 
    "with", "would", "you", "your", "yours", "yourself", "yourselves"
}

# ==================== 1. KEEP-ALIVE SERVER & SELF-PING ====================
class PingServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK - Bot is running 24/7!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        # Console logs ko clean rakhne ke liye access logs mute rakhe hain
        return

def run_web_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), PingServerHandler)
    print(f"[Keep-Alive] Server running on port {port}")
    server.serve_forever()

def auto_keep_alive_ping():
    """
    Render Free Tier 15 minutes idle hone par sleep mode me chala jata hai.
    Ye background thread har 3 minute (180s) me Render ke live URL par ping karta hai.
    """
    time.sleep(20)  # Bot startup hone tak intezar karein
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) KeepAlivePing/1.0"
    }

    while True:
        target_url = RENDER_EXTERNAL_URL
        if target_url:
            if not target_url.startswith("http://") and not target_url.startswith("https://"):
                target_url = f"https://{target_url}"
            try:
                res = requests.get(target_url, headers=headers, timeout=15)
                current_time = time.strftime("%H:%M:%S")
                print(f"[{current_time}] [Keep-Alive] Ping sent to {target_url} -> Status: {res.status_code}")
            except Exception as e:
                print(f"[Keep-Alive Warning] Ping failed: {e}")
        else:
            print("[Keep-Alive Alert] 'RENDER_EXTERNAL_URL' set nahi hai! Render ke Environment Variables me ise add karein.")

        # Har 3 minute (180 seconds) me ping repeat hoga
        time.sleep(180)

# ==================== 2. GITHUB API FUNCTIONS ====================
def get_github_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "UKVisa-Telegram-Bot",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers

def get_github_file():
    if not GITHUB_TOKEN:
        return None, None
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}?ref={GITHUB_BRANCH}"
    try:
        res = requests.get(url, headers=get_github_headers(), timeout=10)
        if res.status_code == 200:
            data = res.json()
            content_b64 = data.get("content", "")
            raw_text = base64.b64decode(content_b64).decode("utf-8", errors="ignore")
            return raw_text, data.get("sha")
        elif res.status_code == 404:
            return False, None
    except Exception as e:
        print(f"GitHub fetch error: {e}")
    return None, None

def get_github_file_sha():
    _, sha = get_github_file()
    return sha

def upload_file_to_github(file_bytes):
    if not GITHUB_TOKEN:
        return False, "GITHUB_TOKEN Render me set nahi hai!"

    sha = get_github_file_sha()
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    
    b64_content = base64.b64encode(file_bytes).decode("utf-8")
    payload = {
        "message": "Update questions via Telegram Bot",
        "content": b64_content,
        "branch": GITHUB_BRANCH
    }
    if sha:
        payload["sha"] = sha

    try:
        res = requests.put(url, headers=get_github_headers(), json=payload, timeout=15)
        if res.status_code in [200, 201]:
            return True, "File GitHub par successfully save ho gayi!"
        elif res.status_code == 404:
            return False, f"GitHub Repo nahi mili! Check karein: '{GITHUB_REPO}'"
        else:
            return False, f"GitHub Error ({res.status_code}): {res.text}"
    except Exception as e:
        return False, f"Upload Connection Error: {str(e)}"

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
        res = requests.delete(url, headers=get_github_headers(), json=payload, timeout=15)
        if res.status_code in [200, 204]:
            return True, "File GitHub se delete ho gayi!"
        elif res.status_code == 404:
            return True, "File pehle se delete ho chuki hai."
        else:
            return False, f"GitHub Error ({res.status_code}): {res.text}"
    except Exception as e:
        return False, f"Delete Connection Error: {str(e)}"

# ==================== 3. QUESTIONS PARSER & RELOAD ====================
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
    QUESTIONS = []

    if GITHUB_TOKEN:
        content, sha = get_github_file()
        if content is False:
            if os.path.exists("questions.txt"):
                try: os.remove("questions.txt")
                except: pass
            return False, "GitHub par file nahi mili (Deleted). Sabhi questions clear hain!"
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
                return False, "File khali hai, koi question nahi mila."

    if os.path.exists("questions.txt"):
        try:
            with open("questions.txt", "r", encoding="utf-8") as f:
                parsed = parse_questions_content(f.read())
            QUESTIONS = parsed
            if QUESTIONS:
                return True, f"Local file se {len(QUESTIONS)} questions load ho gaye!"
        except Exception as e:
            print(f"Local read error: {e}")

    QUESTIONS = []
    return False, "Koi questions nahi mile! Bot abhi poori tarah khali hai."

recognizer = sr.Recognizer()

def is_admin(user_id):
    if not ADMIN_ID:
        return True
    return str(user_id) == str(ADMIN_ID)

# ==================== 4. SPEECH EVALUATION ENGINE ====================
def extract_keywords(text):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

def evaluate_speech(user_text, expected_answer, audio_duration_sec, google_confidence):
    duration_sec = max(1.0, audio_duration_sec)
    spoken_words = user_text.strip().split()
    word_count = len(spoken_words)
    wpm = int((word_count / duration_sec) * 60)

    # Visa/IELTS Standard Pace (115 - 155 WPM)
    if 115 <= wpm <= 155:
        fluency_score = min(100.0, 92.0 + (8.0 * (1 - abs(135 - wpm) / 20.0)))
        fluency_remark = "🎯 Perfect Speaking Pace (Ekdum sahi speed)"
    elif 90 <= wpm < 115:
        fluency_score = 75.0 + ((wpm - 90) / 25.0) * 15.0
        fluency_remark = "🐢 Thoda slow tha, thodi flow badhayein"
    elif 155 < wpm <= 185:
        fluency_score = 75.0 + ((185 - wpm) / 30.0) * 15.0
        fluency_remark = "⚡ Thoda fast tha, aaram se clear bole"
    elif wpm < 90:
        fluency_score = max(35.0, 45.0 + (wpm / 90.0) * 25.0)
        fluency_remark = "⚠️ Bahut ruk-ruk ke bola, flow me bole"
    else:
        fluency_score = max(40.0, 70.0 - ((wpm - 185) / 50.0) * 25.0)
        fluency_remark = "⚠️ Bahut jyada tezi se bola, shanti se bole"

    clean_user = " ".join(user_text.lower().split())
    clean_exp = " ".join(expected_answer.lower().split())
    seq_ratio = difflib.SequenceMatcher(None, clean_user, clean_exp).ratio() * 100

    exp_keywords = list(dict.fromkeys(extract_keywords(expected_answer)))
    user_words_set = set(extract_keywords(user_text))

    covered_keywords = [w for w in exp_keywords if w in user_words_set]
    missed_keywords = [w for w in exp_keywords if w not in user_words_set]

    if exp_keywords:
        kw_ratio = (len(covered_keywords) / len(exp_keywords)) * 100
        accuracy_score = (kw_ratio * 0.65) + (seq_ratio * 0.35)
    else:
        accuracy_score = seq_ratio

    accuracy_score = min(100.0, max(0.0, accuracy_score))

    if google_confidence is not None and google_confidence > 0:
        pronun_score = min(100.0, google_confidence * 100)
    else:
        pronun_score = min(95.0, max(60.0, 70.0 + (accuracy_score * 0.25)))

    if pronun_score >= 85:
        pronun_remark = "🌟 Clear & Natural Accent"
    elif pronun_score >= 70:
        pronun_remark = "👍 Good, thoda aur clarity laane ki koshish karein"
    else:
        pronun_remark = "⚠️ Words ko thoda aur saaf aur khol kar bole"

    overall_score = (accuracy_score * 0.40) + (fluency_score * 0.30) + (pronun_score * 0.30)
    
    if overall_score >= 85:
        grade = "A (Excellent - Visa Ready 🇬🇧)"
    elif overall_score >= 70:
        grade = "B (Good - Minor Practice Needed)"
    elif overall_score >= 55:
        grade = "C (Average - More Practice Required)"
    else:
        grade = "D (Needs Improvement)"

    return {
        "overall": overall_score,
        "grade": grade,
        "accuracy": accuracy_score,
        "fluency": fluency_score,
        "fluency_remark": fluency_remark,
        "pronun": pronun_score,
        "pronun_remark": pronun_remark,
        "wpm": wpm,
        "duration": duration_sec,
        "covered": covered_keywords,
        "missed": missed_keywords,
        "total_kw": len(exp_keywords)
    }

# ==================== 5. BOT HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q_index"] = 0
    reload_questions()

    if not QUESTIONS:
        await update.message.reply_text(
            "⚠️ Abhi koi questions upload nahi hain!\n\n"
            "👉 Nayi .txt file bhejein jisme questions ho."
        )
        return

    await update.message.reply_text(
        f"🇬🇧 UK Visa Interview Practice Bot me aapka swagat hai!\n\n"
        f"📊 Total Questions: {len(QUESTIONS)}\n"
        "🔹 Sawal aane par apna answer Voice Note (bolkar) bhejein.\n"
        "🔹 Bot aapko Accuracy, Fluency, Pronunciation aur WPM ka scorecard dega.\n"
        "🔹 Nayi file lagane ke liye sirf .txt file send kar dein.\n\n"
        "Pehla sawal niche dekhein 👇"
    )
    await ask_question(update, context)

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q_index"] = 0
    success, msg = reload_questions()
    
    if success and QUESTIONS:
        await update.message.reply_text(f"🔄 Reset Successful!\n\n{msg}")
        await ask_question(update, context)
    else:
        context.user_data["q_index"] = 0
        await update.message.reply_text(
            f"ℹ️ {msg}\n\n"
            "Abhi bot me 0 questions hain. Naya interview shuru karne ke liye `.txt` file bhejein!"
        )

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global QUESTIONS
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Aapko delete karne ki permission nahi hai!")
        return

    status_msg = await update.message.reply_text("⏳ Questions delete kiye ja rahe hain...")
    success, msg = delete_file_from_github()

    QUESTIONS = []
    context.user_data["q_index"] = 0
    if os.path.exists("questions.txt"):
        try: os.remove("questions.txt")
        except: pass

    if success:
        await status_msg.edit_text("🗑️ Sabhi Questions Delete ho gaye! Ab bot bilkul khali hai.")
    else:
        await status_msg.edit_text(f"⚠️ Notice: {msg}\n(Bot ki memory aur local file clear kar di gayi hai)")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global QUESTIONS
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Aapko file upload karne ki permission nahi hai!")
        return

    doc = update.message.document
    if not doc.file_name.lower().endswith(".txt"):
        await update.message.reply_text("⚠️ Kripya sirf .txt format wali file hi bhejein!")
        return

    status_msg = await update.message.reply_text("📥 File download ho rahi hai...")
    
    try:
        file = await doc.get_file()
        file_bytes = await file.download_as_bytearray()
        content_text = file_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        await status_msg.edit_text(f"❌ File download error: {str(e)}")
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

    await status_msg.edit_text("🚀 GitHub par automatically upload kiya jaa raha hai...")

    success, msg = upload_file_to_github(file_bytes)
    if success:
        QUESTIONS = parsed
        context.user_data["q_index"] = 0
        with open("questions.txt", "w", encoding="utf-8") as f:
            f.write(content_text)

        await status_msg.edit_text(
            f"✅ File Successfully GitHub Par Save Ho Gayi!\n\n"
            f"📊 Kul {len(QUESTIONS)} questions load ho chuke hain.\n"
            f"Interview shuru karne ke liye /start dabayein."
        )
    else:
        await status_msg.edit_text(f"❌ Upload Failed:\n{msg}")

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not QUESTIONS:
        await update.effective_chat.send_message("⚠️ Abhi koi questions nahi hain. Kripya pehle .txt file upload karein.")
        return

    idx = context.user_data.get("q_index", 0)
    if idx < len(QUESTIONS):
        q_text = QUESTIONS[idx]["question"]
        msg = f"🎙️ Question {idx + 1}/{len(QUESTIONS)}:\n\n👉 {q_text}\n\n(Apna answer bolkar Voice Note bhejein)"
        if update.message:
            await update.message.reply_text(msg)
        else:
            await update.effective_chat.send_message(msg)
    else:
        await update.effective_chat.send_message(
            "🎉 Interview Complete!\nNaye questions upload karne ke liye file bhejein ya /reset dabayein."
        )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = context.user_data.get("q_index", 0)
    if not QUESTIONS or idx >= len(QUESTIONS):
        await update.message.reply_text("⚠️ Koi active question nahi hai. Naye sawal daalne ke liye .txt file bhejein ya /start dabayein.")
        return

    status_msg = await update.message.reply_text("⏳ Processing speech & evaluating metrics...")

    voice_file = await update.message.voice.get_file()
    user_id = update.message.from_user.id
    oga_path = f"temp_{user_id}.oga"
    wav_path = f"temp_{user_id}.wav"
    await voice_file.download_to_drive(oga_path)

    audio_duration = 0.0
    try:
        audio = AudioSegment.from_file(oga_path)
        audio_duration = len(audio) / 1000.0
        audio.export(wav_path, format="wav")
    except Exception as e:
        await status_msg.edit_text(f"❌ Audio convert error: {str(e)}")
        if os.path.exists(oga_path): os.remove(oga_path)
        return

    user_text = ""
    google_confidence = None

    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            result = recognizer.recognize_google(audio_data, language="en-GB", show_all=True)
            
            if not result or not isinstance(result, dict) or not result.get("alternative"):
                raise sr.UnknownValueError()
            
            best_match = result["alternative"][0]
            user_text = best_match.get("transcript", "").strip()
            google_confidence = best_match.get("confidence", None)

    except sr.UnknownValueError:
        await status_msg.edit_text("❌ Aapki aawaz saaf nahi aayi. Kripya shanti wali jagah se dubara bolkar bhejein.")
        if os.path.exists(oga_path): os.remove(oga_path)
        if os.path.exists(wav_path): os.remove(wav_path)
        return
    except Exception as e:
        await status_msg.edit_text(f"❌ Speech Error: {str(e)}")
        if os.path.exists(oga_path): os.remove(oga_path)
        if os.path.exists(wav_path): os.remove(wav_path)
        return

    if os.path.exists(oga_path): os.remove(oga_path)
    if os.path.exists(wav_path): os.remove(wav_path)

    expected_answer = QUESTIONS[idx]["answer"]
    report = evaluate_speech(user_text, expected_answer, audio_duration, google_confidence)

    covered_str = ", ".join(report["covered"][:6]) if report["covered"] else "None"
    missed_str = ", ".join(report["missed"][:6]) if report["missed"] else "None (Sabhi bole 🎉)"

    feedback = (
        f"🗣️ *Aapne bola:*\n\"{user_text}\"\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏆 *OVERALL SCORE: {report['overall']:.1f}%*\n"
        f"🎖️ *Grade:* {report['grade']}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *Accuracy (Content):* {report['accuracy']:.1f}%\n"
        f"🗣️ *Pronunciation:* {report['pronun']:.1f}% ({report['pronun_remark']})\n"
        f"⚡ *Fluency:* {report['fluency']:.1f}% ({report['wpm']} WPM)\n"
        f"⏱️ *Duration:* {report['duration']:.1f}s | {report['fluency_remark']}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📌 *Key Points Analysis ({len(report['covered'])}/{report['total_kw']}):*\n"
        f"✅ *Covered:* `{covered_str}`\n"
        f"❌ *Missed:* `{missed_str}`\n\n"
        f"📖 *Expected Answer:*\n\"{expected_answer}\""
    )
    
    await status_msg.edit_text(feedback, parse_mode="Markdown")

    context.user_data["q_index"] = idx + 1
    await ask_question(update, context)

# ==================== MAIN ====================
def main():
    # 1. Start Keep-Alive Server
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()

    # 2. Start Self-Ping Thread (har 3 minute me)
    ping_thread = threading.Thread(target=auto_keep_alive_ping, daemon=True)
    ping_thread.start()

    # 3. Reload questions
    reload_questions()

    # 4. Start Telegram Bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("reload", reset_command))
    app.add_handler(CommandHandler("delete", delete_command))
    
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("[Bot] UK Visa Bot is active and running...")
    app.run_polling()

if __name__ == "__main__":
    main()
