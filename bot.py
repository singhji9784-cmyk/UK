import os
import re
import difflib
import time
import threading
import asyncio
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
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

# Render Live URL (e.g., https://your-app-name.onrender.com)
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "").strip()

# GitHub Configurations
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip() 
GITHUB_REPO = os.getenv("GITHUB_REPO", "singhji9784-cmyk/UK").strip()
GITHUB_FILE_PATH = os.getenv("GITHUB_FILE_PATH", "questions.txt").strip()
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main").strip()

# Admin check (khali chhodne par sab use kar sakte hain)
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()

QUESTIONS = []

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
        self.wfile.write(b"OK - UK Visa Bot is Online 24/7!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        return

def run_web_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), PingServerHandler)
    print(f"[Keep-Alive] Server listening on port {port}")
    server.serve_forever()

def auto_keep_alive_ping():
    time.sleep(15)
    headers = {"User-Agent": "Mozilla/5.0 KeepAlivePing/3.0"}
    
    while True:
        target_url = RENDER_EXTERNAL_URL
        if target_url:
            if not target_url.startswith("http://") and not target_url.startswith("https://"):
                target_url = f"https://{target_url}"
            try:
                res = requests.get(target_url, headers=headers, timeout=12)
                t_str = time.strftime("%H:%M:%S")
                print(f"[{t_str}] [Keep-Alive Ping] -> Status: {res.status_code}")
            except Exception as e:
                print(f"[Keep-Alive Warning] Ping error: {e}")
        else:
            print("[Keep-Alive Alert] 'RENDER_EXTERNAL_URL' set nahi hai! Render dashboard me dalein.")
        
        # Har 150 seconds (2.5 minute) me ping repeat hoga
        time.sleep(150)

# ==================== 2. GITHUB ASYNC BACKUP ====================
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

def serialize_questions(qa_list):
    entries = []
    for item in qa_list:
        entries.append(f"Q: {item['question']}\nA: {item['answer']}")
    return "\n---\n".join(entries)

def background_sync_github():
    """Background thread me GitHub par questions.txt update hota rahega"""
    if not GITHUB_TOKEN:
        return
    try:
        content_text = serialize_questions(QUESTIONS)
        if not QUESTIONS:
            _, sha = get_github_file()
            if sha:
                url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
                payload = {"message": "All questions cleared", "sha": sha, "branch": GITHUB_BRANCH}
                requests.delete(url, headers=get_github_headers(), json=payload, timeout=10)
            return

        file_bytes = content_text.encode("utf-8")
        _, sha = get_github_file()
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
        payload = {
            "message": "Auto-sync questions via Telegram Bot",
            "content": base64.b64encode(file_bytes).decode("utf-8"),
            "branch": GITHUB_BRANCH
        }
        if sha:
            payload["sha"] = sha
        requests.put(url, headers=get_github_headers(), json=payload, timeout=12)
        print("[GitHub Sync] Background backup completed successfully.")
    except Exception as e:
        print(f"[GitHub Sync Error] {e}")

def trigger_background_sync():
    threading.Thread(target=background_sync_github, daemon=True).start()

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
        # Support Q: and A:
        if ("Q:" in entry or "q:" in entry) and ("A:" in entry or "a:" in entry):
            # Split case-insensitively on A: or a:
            parts = re.split(r'\n?[Aa]:\s*', entry, maxsplit=1)
            if len(parts) == 2:
                q_part = re.sub(r'^[Qq]:\s*', '', parts[0].strip()).strip()
                a_part = parts[1].strip()
                if q_part and a_part:
                    qa_list.append({"question": q_part, "answer": a_part})
    return qa_list

def reload_questions():
    global QUESTIONS
    QUESTIONS = []

    if GITHUB_TOKEN:
        content, _ = get_github_file()
        if content:
            QUESTIONS = parse_questions_content(content)
            if QUESTIONS:
                with open("questions.txt", "w", encoding="utf-8") as f:
                    f.write(content)
                return True, f"GitHub se {len(QUESTIONS)} questions load ho gaye!"

    if os.path.exists("questions.txt"):
        try:
            with open("questions.txt", "r", encoding="utf-8") as f:
                QUESTIONS = parse_questions_content(f.read())
            if QUESTIONS:
                return True, f"Local memory se {len(QUESTIONS)} questions load ho gaye!"
        except Exception as e:
            print(f"File read error: {e}")

    QUESTIONS = []
    return False, "Abhi 0 questions hain. Nayi .txt file bhejein!"

recognizer = sr.Recognizer()

def is_admin(user_id):
    if not ADMIN_ID:
        return True
    return str(user_id) == str(ADMIN_ID)

# ==================== 4. SPEECH EVALUATION ====================
def extract_keywords(text):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

def evaluate_speech(user_text, expected_answer, audio_duration_sec, google_confidence):
    duration_sec = max(1.0, audio_duration_sec)
    spoken_words = user_text.strip().split()
    word_count = len(spoken_words)
    wpm = int((word_count / duration_sec) * 60)

    if 115 <= wpm <= 155:
        fluency_score = min(100.0, 92.0 + (8.0 * (1 - abs(135 - wpm) / 20.0)))
        fluency_remark = "🎯 Perfect Speaking Pace"
    elif 90 <= wpm < 115:
        fluency_score = 75.0 + ((wpm - 90) / 25.0) * 15.0
        fluency_remark = "🐢 Thoda slow tha, flow badhayein"
    elif 155 < wpm <= 185:
        fluency_score = 75.0 + ((185 - wpm) / 30.0) * 15.0
        fluency_remark = "⚡ Thoda fast tha, aaram se bole"
    elif wpm < 90:
        fluency_score = max(35.0, 45.0 + (wpm / 90.0) * 25.0)
        fluency_remark = "⚠️ Ruk-ruk ke bola, flow me bole"
    else:
        fluency_score = max(40.0, 70.0 - ((wpm - 185) / 50.0) * 25.0)
        fluency_remark = "⚠️ Jyada tezi se bola, shanti se bole"

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
        pronun_remark = "🌟 Clear Accent"
    elif pronun_score >= 70:
        pronun_remark = "👍 Good Clarity"
    else:
        pronun_remark = "⚠️ Words spasht bole"

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

# ==================== 5. KEYBOARDS ====================
def build_question_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("⏭️ Next Question", callback_data="btn_next"),
            InlineKeyboardButton("🔄 Repeat", callback_data="btn_repeat")
        ],
        [
            InlineKeyboardButton("🗑️ Delete This Question", callback_data="btn_delete_this")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==================== 6. BOT LOGIC (APPEND MODE) ====================
def add_new_questions_to_pool(parsed_items):
    """Purane questions ko mitaye bina naye questions ko append karta hai"""
    global QUESTIONS
    added_count = 0
    updated_count = 0

    for item in parsed_items:
        q_clean = item["question"].strip().lower()
        matched = False
        for existing in QUESTIONS:
            if existing["question"].strip().lower() == q_clean:
                existing["answer"] = item["answer"]
                matched = True
                updated_count += 1
                break
        if not matched:
            QUESTIONS.append(item)
            added_count += 1

    # Local file me pura merged list save karein
    with open("questions.txt", "w", encoding="utf-8") as f:
        f.write(serialize_questions(QUESTIONS))

    # GitHub par background me sync trigger karein
    trigger_background_sync()

    return added_count, updated_count

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not QUESTIONS:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="⚠️ Abhi koi questions nahi hain. Nayi `.txt` file bhejein ya `Q:` aur `A:` likhkar send karein!"
        )
        return

    idx = context.user_data.get("q_index", 0)
    if idx >= len(QUESTIONS):
        idx = 0
        context.user_data["q_index"] = 0

    q_text = QUESTIONS[idx]["question"]
    msg = (
        f"🎙️ *Question {idx + 1}/{len(QUESTIONS)}:*\n\n"
        f"👉 *{q_text}*\n\n"
        f"_(Voice Note me answer bole ya button use karein)_"
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=msg,
        parse_mode="Markdown",
        reply_markup=build_question_keyboard()
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q_index"] = 0
    if not QUESTIONS:
        reload_questions()

    if not QUESTIONS:
        await update.message.reply_text(
            "🇬🇧 UK Visa Interview Bot me swagat hai!\n\n"
            "⚠️ Abhi koi questions upload nahi hain.\n"
            "👉 Questions wali `.txt` file send karein ya seedha `Q:` aur `A:` likhkar message karein."
        )
        return

    await update.message.reply_text(
        f"🇬🇧 UK Visa Interview Practice Bot Started!\n"
        f"📊 Kul Questions: *{len(QUESTIONS)}*\n"
        f"🔹 Answer bolne ke liye Voice Note bhejein.\n"
        f"🔹 Aage badhne ke liye 'Next' button dabayein."
    )
    await ask_question(update, context)

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data
    idx = context.user_data.get("q_index", 0)

    if action == "btn_next":
        if not QUESTIONS:
            await query.edit_message_text("⚠️ Questions khali hain! Naye sawal upload karein.")
            return
        context.user_data["q_index"] = (idx + 1) % len(QUESTIONS)
        await ask_question(update, context)

    elif action == "btn_repeat":
        await ask_question(update, context)

    elif action == "btn_delete_this":
        if not is_admin(update.effective_user.id):
            await query.message.reply_text("❌ Question delete karne ki permission nahi hai!")
            return

        if not QUESTIONS or idx >= len(QUESTIONS):
            await query.edit_message_text("⚠️ Koi active question nahi mila.")
            return

        deleted_q = QUESTIONS.pop(idx)
        # Update local file & GitHub
        with open("questions.txt", "w", encoding="utf-8") as f:
            f.write(serialize_questions(QUESTIONS))
        trigger_background_sync()

        await query.edit_message_text(f"🗑️ *Deleted:* \"{deleted_q['question']}\"", parse_mode="Markdown")

        if QUESTIONS:
            if idx >= len(QUESTIONS):
                context.user_data["q_index"] = 0
            await ask_question(update, context)
        else:
            await query.message.reply_text("Sabhi questions delete ho gaye! Bot abhi khali hai.")

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global QUESTIONS
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Permission nahi hai!")
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "📌 *Question Delete Karne Ke Tarike:*\n\n"
            "1️⃣ Number se: `/delete 2`\n"
            "2️⃣ Title/Word se: `/delete why uk`\n"
            "3️⃣ Sabhi sawal delete karne ke liye: `/delete all`",
            parse_mode="Markdown"
        )
        return

    query_str = " ".join(args).strip().lower()

    if query_str == "all":
        QUESTIONS = []
        context.user_data["q_index"] = 0
        with open("questions.txt", "w", encoding="utf-8") as f:
            f.write("")
        trigger_background_sync()
        await update.message.reply_text("🗑️ Sabhi questions successfully delete ho gaye!")
        return

    if query_str.isdigit():
        target_num = int(query_str)
        if 1 <= target_num <= len(QUESTIONS):
            deleted = QUESTIONS.pop(target_num - 1)
            with open("questions.txt", "w", encoding="utf-8") as f:
                f.write(serialize_questions(QUESTIONS))
            trigger_background_sync()
            context.user_data["q_index"] = min(context.user_data.get("q_index", 0), max(0, len(QUESTIONS) - 1))
            await update.message.reply_text(f"✅ Question {target_num} Deleted:\n👉 *{deleted['question']}*", parse_mode="Markdown")
            return
        else:
            await update.message.reply_text(f"❌ Invalid number! 1 se {len(QUESTIONS)} ke beech number dalein.")
            return

    matched_idx = -1
    for i, q in enumerate(QUESTIONS):
        if query_str in q["question"].lower():
            matched_idx = i
            break

    if matched_idx != -1:
        deleted = QUESTIONS.pop(matched_idx)
        with open("questions.txt", "w", encoding="utf-8") as f:
            f.write(serialize_questions(QUESTIONS))
        trigger_background_sync()
        context.user_data["q_index"] = min(context.user_data.get("q_index", 0), max(0, len(QUESTIONS) - 1))
        await update.message.reply_text(f"✅ Question Deleted:\n👉 *{deleted['question']}*", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ \"{query_str}\" se related koi sawal nahi mila.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """File upload hone par purane questions ke sath NAYA QUESTION APPEND HOGA"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Permission denied!")
        return

    doc = update.message.document
    if not doc.file_name.lower().endswith(".txt"):
        await update.message.reply_text("⚠️ Kripya sirf `.txt` format wali file bhejein!")
        return

    try:
        file = await doc.get_file()
        file_bytes = await file.download_as_bytearray()
        content_text = file_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        await update.message.reply_text(f"❌ Download error: {e}")
        return

    parsed = parse_questions_content(content_text)
    if not parsed:
        await update.message.reply_text(
            "❌ Format Galat Hai! File me `Q:` aur `A:` hona chahiye.\n\n"
            "Example:\n"
            "Q: Why UK?\n"
            "A: Because..."
        )
        return

    added, updated = add_new_questions_to_pool(parsed)

    msg = (
        f"✅ *Questions Successfully Added!* 🚀\n\n"
        f"➕ Naye Questions Jude: *+{added}*\n"
    )
    if updated > 0:
        msg += f"🔄 Updated (Already Existed): *{updated}*\n"
    msg += f"📊 Ab Bot Me Kul Questions: *{len(QUESTIONS)}*\n\nNiche practice karein 👇"

    await update.message.reply_text(msg, parse_mode="Markdown")
    
    # Naye sawal par le jayein
    context.user_data["q_index"] = len(QUESTIONS) - 1
    await ask_question(update, context)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Agar user seedha chat me 'Q: ... A: ...' type karke bheje toh bina file ke add kar lega"""
    text = update.message.text.strip()
    
    # Check if text contains Q: and A:
    if ("q:" in text.lower()) and ("a:" in text.lower()):
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Permission denied!")
            return
        
        parsed = parse_questions_content(text)
        if parsed:
            added, updated = add_new_questions_to_pool(parsed)
            msg = (
                f"⚡ *Quick Question Added via Text!*\n\n"
                f"➕ Naye Questions: *+{added}*\n"
                f"📊 Ab Kul Questions: *{len(QUESTIONS)}*\n\n"
                f"Niche practice karein 👇"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
            context.user_data["q_index"] = len(QUESTIONS) - 1
            await ask_question(update, context)
            return

    # Normal text ho toh user ko guide karein
    await update.message.reply_text(
        "🎙️ Sawal ka jawab dene ke liye **Voice Note (Aawaz)** bhejein.\n"
        "👉 Naya question jodne ke liye `.txt` file bhejein ya format me likhein:\n"
        "`Q: Your Question`\n`A: Your Answer`",
        parse_mode="Markdown"
    )

def convert_and_transcribe(oga_path, wav_path):
    audio = AudioSegment.from_file(oga_path)
    duration_sec = len(audio) / 1000.0
    audio.export(wav_path, format="wav")

    user_text = ""
    confidence = None
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        result = recognizer.recognize_google(audio_data, language="en-GB", show_all=True)
        if result and isinstance(result, dict) and result.get("alternative"):
            best = result["alternative"][0]
            user_text = best.get("transcript", "").strip()
            confidence = best.get("confidence", None)
    return user_text, confidence, duration_sec

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = context.user_data.get("q_index", 0)
    if not QUESTIONS or idx >= len(QUESTIONS):
        await update.message.reply_text("⚠️ Pehle sawal upload karein ya /start dabayein.")
        return

    status_msg = await update.message.reply_text("⏳ Evaluating speech metrics...")

    user_id = update.message.from_user.id
    oga_path = f"temp_{user_id}.oga"
    wav_path = f"temp_{user_id}.wav"

    voice_file = await update.message.voice.get_file()
    await voice_file.download_to_drive(oga_path)

    loop = asyncio.get_running_loop()
    try:
        user_text, google_conf, audio_duration = await loop.run_in_executor(
            None, convert_and_transcribe, oga_path, wav_path
        )
    except sr.UnknownValueError:
        await status_msg.edit_text("❌ Aawaz saaf nahi aayi! Shanti wali jagah se dobara bole.")
        return
    except Exception as e:
        await status_msg.edit_text(f"❌ Audio error: {e}")
        return
    finally:
        if os.path.exists(oga_path): os.remove(oga_path)
        if os.path.exists(wav_path): os.remove(wav_path)

    expected_answer = QUESTIONS[idx]["answer"]
    report = evaluate_speech(user_text, expected_answer, audio_duration, google_conf)

    covered_str = ", ".join(report["covered"][:6]) if report["covered"] else "None"
    missed_str = ", ".join(report["missed"][:6]) if report["missed"] else "None (Sabhi bole 🎉)"

    feedback = (
        f"🗣️ *Aapne bola:*\n\"{user_text}\"\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏆 *OVERALL SCORE: {report['overall']:.1f}%*\n"
        f"🎖️ *Grade:* {report['grade']}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *Accuracy:* {report['accuracy']:.1f}%\n"
        f"🗣️ *Pronunciation:* {report['pronun']:.1f}% ({report['pronun_remark']})\n"
        f"⚡ *Fluency:* {report['fluency']:.1f}% ({report['wpm']} WPM)\n"
        f"⏱️ *Duration:* {report['duration']:.1f}s | {report['fluency_remark']}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📌 *Key Points ({len(report['covered'])}/{report['total_kw']}):*\n"
        f"✅ *Covered:* `{covered_str}`\n"
        f"❌ *Missed:* `{missed_str}`\n\n"
        f"📖 *Expected Answer:*\n\"{expected_answer}\""
    )

    await status_msg.edit_text(feedback, parse_mode="Markdown")

    # Automatically Next question par le jayein
    context.user_data["q_index"] = (idx + 1) % len(QUESTIONS)
    await ask_question(update, context)

# ==================== MAIN ====================
def main():
    # 1. Start Keep-Alive Server
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()

    # 2. Start Self-Ping Thread (2.5 min interval)
    ping_thread = threading.Thread(target=auto_keep_alive_ping, daemon=True)
    ping_thread.start()

    # 3. Load Existing Questions
    reload_questions()

    # 4. Telegram Application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("delete", delete_command))
    
    # Inline Buttons
    app.add_handler(CallbackQueryHandler(button_callback_handler))

    # Handlers (Files, Text for quick Q/A add, and Voice)
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    print("[Ready] Bot is active with 1-by-1 Append Mode!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
