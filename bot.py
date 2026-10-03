import os
import re
import difflib
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import speech_recognition as sr
from pydub import AudioSegment
import imageio_ffmpeg

# Set ffmpeg path for pydub
AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()

# --- Configuration ---
# Render Environment variable se token le ya yaha direct dalein:
BOT_TOKEN = os.getenv("BOT_TOKEN", "YAHAN_APNA_TELEGRAM_BOT_TOKEN_DAALEIN")

# Questions load karne ka function
def load_questions(filename="questions.txt"):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    
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

QUESTIONS = load_questions()
recognizer = sr.Recognizer()

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q_index"] = 0
    if not QUESTIONS:
        await update.message.reply_text("⚠️ questions.txt file me koi questions nahi mile!")
        return

    await update.message.reply_text(
        "🇬🇧 *UK Visa Interview Practice Bot* me aapka swagat hai!\n\n"
        "Main aapse ek-ek karke interview questions poochhunga.\n"
        "Aapko Telegram par **Voice Message (Audio)** bhej kar jawab dena hai.\n\n"
        "Taiyaar hone par niche pehla sawal dekhein 👇",
        parse_mode="Markdown"
    )
    await ask_question(update, context)

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
            "🎉 *Badhai ho! Aapka Interview Session complete ho gaya hai.*\n"
            "Dobara practice karne ke liye /start dabayein.",
            parse_mode="Markdown"
        )

# Handle Voice Answers
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = context.user_data.get("q_index", 0)
    if idx >= len(QUESTIONS):
        await update.message.reply_text("Interview pehle hi khatam ho chuka hai. Dobara shuru karne ke liye /start dabayein.")
        return

    status_msg = await update.message.reply_text("⏳ Aapki aawaz sun raha hu aur process kar raha hu...")

    # 1. Download telegram voice file (.oga)
    voice_file = await update.message.voice.get_file()
    oga_path = f"temp_{update.message.from_user.id}.oga"
    wav_path = f"temp_{update.message.from_user.id}.wav"
    await voice_file.download_to_drive(oga_path)

    # 2. Convert .oga to .wav
    try:
        audio = AudioSegment.from_file(oga_path)
        audio.export(wav_path, format="wav")
    except Exception as e:
        await status_msg.edit_text(f"❌ Audio convert karne me issue aaya: {str(e)}")
        if os.path.exists(oga_path): os.remove(oga_path)
        return

    # 3. Speech to Text
    user_text = ""
    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            user_text = recognizer.recognize_google(audio_data, language="en-GB") # UK English
    except sr.UnknownValueError:
        await status_msg.edit_text("❌ Aapki aawaz saaf sunai nahi di. Kripya dobara ache se bolkar bhejein.")
        if os.path.exists(oga_path): os.remove(oga_path)
        if os.path.exists(wav_path): os.remove(wav_path)
        return
    except Exception as e:
        await status_msg.edit_text(f"❌ Speech recognition error: {str(e)}")
        if os.path.exists(oga_path): os.remove(oga_path)
        if os.path.exists(wav_path): os.remove(wav_path)
        return

    # Cleanup temp audio files
    if os.path.exists(oga_path): os.remove(oga_path)
    if os.path.exists(wav_path): os.remove(wav_path)

    # 4. Check Answer & Similarity
    expected_answer = QUESTIONS[idx]["answer"]
    similarity = difflib.SequenceMatcher(None, user_text.lower(), expected_answer.lower()).ratio() * 100

    feedback = (
        f"🗣️ *Aapne bola:*\n\"{user_text}\"\n\n"
        f"✅ *Ideal Answer:*\n\"{expected_answer}\"\n\n"
        f"📊 *Accuracy Score:* {similarity:.1f}%\n"
    )

    await status_msg.edit_text(feedback, parse_mode="Markdown")

    # Next Question
    context.user_data["q_index"] = idx + 1
    await ask_question(update, context)

# Main Application
def main():
    if BOT_TOKEN == "YAHAN_APNA_TELEGRAM_BOT_TOKEN_DAALEIN":
        print("Error: Kripya bot token dalein!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("Bot chalu ho gaya hai...")
    app.run_polling()

if __name__ == "__main__":
    main()
