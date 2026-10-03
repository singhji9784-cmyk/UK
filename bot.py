import os
import re
import difflib
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

# ⚠️ YAHAN APNI GITHUB RAW FILE KA LINK DAALEIN:
# Example: "https://raw.githubusercontent.com/singhji97/UK/main/questions.txt"
GITHUB_RAW_URL = os.getenv(
    "GITHUB_RAW_URL", 
    "https://raw.githubusercontent.com/singhji97/UK/main/questions.txt"
)

# Global list for questions
QUESTIONS = []

def parse_questions_content(content):
    entries = content.split("---")
    qa_list = []
    for entry in entries:
        q_match = re.search(r"Q:\s*(.+)", entry)
        a_match = re.search(r"A:\s*(.+)", entry)
        if q_match and a_match:
            qa_list.append({
                "question": q_match.group(1).strip(),
                "answer": a_match.group(1).strip()
            })
    return qa_list

# GitHub ya Local file se turant reload karne ka function
def reload_questions():
    global QUESTIONS
    # 1. Pehle GitHub raw link se live fetch karega (Bina deploy wait kiye)
    if GITHUB_RAW_URL and "githubusercontent.com" in GITHUB_RAW_URL:
        try:
            # Cache bypass karne ke liye timestamp lagaya hai
            url = f"{GITHUB_RAW_URL}?t={os.urandom(4).hex()}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                QUESTIONS = parse_questions_content(response.text)
                return True, f"GitHub se {len(QUESTIONS)} questions turant load ho gaye!"
        except Exception as e:
            print(f"GitHub fetch error: {e}")

    # 2. Agar GitHub link na mile to local questions.txt padhega
    if os.path.exists("questions.txt"):
        with open("questions.txt", "r", encoding="utf-8") as f:
            QUESTIONS = parse_questions_content(f.read())
        return True, f"Local questions.txt se {len(QUESTIONS)} questions load ho gaye!"
    
    return False, "questions.txt file nahi mili!"

# Shuru me questions load karein
reload_questions()
recognizer = sr.Recognizer()

# /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q_index"] = 0
    if not QUESTIONS:
        reload_questions()

    if not QUESTIONS:
        await update.message.reply_text("⚠️ Koi questions nahi mile! Kripya GitHub me questions.txt check karein.")
        return

    await update.message.reply_text(
        "🇬🇧 *UK Visa Interview Practice Bot* me aapka swagat hai!\n\n"
        "🔹 Sawal aane par apna answer **Voice Note (bolkar)** bhejein.\n"
        "🔹 Naye questions load karne ke liye **/reset** ya **/reload** dabayein.\n\n"
        "Taiyaar hone par niche pehla sawal dekhein 👇",
        parse_mode="Markdown"
    )
    await ask_question(update, context)

# /reset Command (Purana data hatayega aur naye questions load karega)
async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # User ka interview index reset karo
    context.user_data["q_index"] = 0
    
    # GitHub se naye questions turant download karo
    success, msg = reload_questions()
    
    if success:
        await update.message.reply_text(
            f"🔄 *Reset Successful!*\n\n{msg}\n"
            "Purana interview cancel ho gaya hai aur naye questions load ho chuke hain.\n\n"
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
            "🎉 *Interview Complete! Aapne sabhi sawalo ke jawab de diye hain.*\n"
            "Dobara shuru karne ke liye ya naye questions ke liye **/reset** dabayein.",
            parse_mode="Markdown"
        )

# Handle Voice Answers
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = context.user_data.get("q_index", 0)
    if idx >= len(QUESTIONS):
        await update.message.reply_text("Interview pehle hi khatam ho chuka hai. Naye questions ke liye /reset dabayein.")
        return

    status_msg = await update.message.reply_text("⏳ Processing audio...")

    # 1. Download voice file
    voice_file = await update.message.voice.get_file()
    user_id = update.message.from_user.id
    oga_path = f"temp_{user_id}.oga"
    wav_path = f"temp_{user_id}.wav"
    await voice_file.download_to_drive(oga_path)

    # 2. Convert to wav
    try:
        audio = AudioSegment.from_file(oga_path)
        audio.export(wav_path, format="wav")
    except Exception as e:
        await status_msg.edit_text(f"❌ Audio convert error: {str(e)}")
        if os.path.exists(oga_path): os.remove(oga_path)
        return

    # 3. Speech Recognition
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

    # Cleanup temp files
    if os.path.exists(oga_path): os.remove(oga_path)
    if os.path.exists(wav_path): os.remove(wav_path)

    # 4. Compare Answer
    expected_answer = QUESTIONS[idx]["answer"]
    similarity = difflib.SequenceMatcher(None, user_text.lower(), expected_answer.lower()).ratio() * 100

    feedback = (
        f"🗣️ *Aapne bola:*\n\"{user_text}\"\n\n"
        f"✅ *Expected Answer:*\n\"{expected_answer}\"\n\n"
        f"📊 *Accuracy Score:* {similarity:.1f}%\n"
    )
    await status_msg.edit_text(feedback, parse_mode="Markdown")

    # Next Question
    context.user_data["q_index"] = idx + 1
    await ask_question(update, context)

# Main
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("reload", reset_command))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
