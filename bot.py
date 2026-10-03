import os
import logging
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pydub import AudioSegment
import speech_recognition as sr
from gtts import gTTS

# Logging Config
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")  # Render Environment Variable
QUESTIONS_FILE = "questions.txt"

# Questions Load करने का फंक्शन
def load_questions():
    qa_dict = {}
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "|" in line:
                    parts = line.strip().split("|")
                    question = parts[0].strip()
                    answer = parts[1].strip()
                    qa_dict[question] = answer
    return qa_dict

# Questions Save करने का फंक्शन
def save_question(question, answer):
    with open(QUESTIONS_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{question} | {answer}")

# /start कमांड
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.first_name
    await update.message.reply_text(
        f"नमस्ते {user}! यूके स्टडी वीजा इंटरव्यू प्रैक्टिस बोट में आपका स्वागत है। 🇬🇧\n\n"
        "🎯 *उपलब्ध कमांड्स:*\n"
        "👉 /practice - बोट आपसे बोलकर और लिखकर सवाल पूछेगा\n"
        "👉 /add <सवाल> | <जवाब> - नया सवाल-जवाब बोट में डायरेक्ट जोड़ने के लिए\n"
        "👉 /list - बोट में जुड़े सभी सवालों को देखने के लिए\n"
        "👉 /upload - सीधे `.txt` फाइल भेजकर पूरी लिस्ट बदलने के लिए",
        parse_mode="Markdown"
    )

# Direct सवाल जोड़ने की कमांड (/add Question | Answer)
async def add_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if "|" not in text:
        await update.message.reply_text(
            "⚠️ सही फॉर्मेट में भेजें!\n"
            "उदाहरण:\n`/add Why UK? | I chose UK because of world class education.`",
            parse_mode="Markdown"
        )
        return

    parts = text.split("|")
    question = parts[0].strip()
    answer = parts[1].strip()

    save_question(question, answer)
    await update.message.reply_text(f"✅ *नया सवाल जुड़ गया है!*\n\n❓ *सवाल:* {question}\n💡 *जवाब:* {answer}", parse_mode="Markdown")

# बोट में मौजूद सभी सवाल देखना (/list)
async def list_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    qa_dict = load_questions()
    if not qa_dict:
        await update.message.reply_text("अभी बोट में कोई सवाल नहीं है। /add करके सवाल जोड़ें।")
        return

    msg = "📚 *आपके बोट में मौजूद सवाल:*\n\n"
    for idx, q in enumerate(qa_dict.keys(), 1):
        msg += f"{idx}. {q}\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

# /practice कमांड (बोलकर + लिखकर सवाल पूछना)
async def practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    qa_dict = load_questions()
    if not qa_dict:
        await update.message.reply_text("अभी कोई सवाल उपलब्ध नहीं है। पहले `/add` करके सवाल जोड़ें या `.txt` फाइल अपलोड करें।", parse_mode="Markdown")
        return

    # रैंडम सवाल चुनना
    question, expected_answer = random.choice(list(qa_dict.items()))
    context.user_data["current_question"] = question
    context.user_data["expected_answer"] = expected_answer

    # 1. टेक्स्ट मैसेज भेजना
    await update.message.reply_text(
        f"🎯 *इंटरव्यू प्रश्न:*\n\n*{question}*\n\n"
        "🎤 *सुनें और अपना उत्तर Voice Note रिकॉर्ड करके भेजें।*",
        parse_mode="Markdown"
    )

    # 2. सवाल का Voice Message (Text-to-Speech) तैयार करके भेजना
    try:
        tts_filename = "question_audio.mp3"
        tts = gTTS(text=question, lang='en', slow=False)
        tts.save(tts_filename)

        with open(tts_filename, 'rb') as audio:
            await update.message.reply_voice(voice=audio)

        if os.path.exists(tts_filename):
            os.remove(tts_filename)
    except Exception as e:
        print(f"Audio generation issue: {e}")

# यूजर के Voice Note का जवाब प्रोसेस करना
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "current_question" not in context.user_data:
        await update.message.reply_text("पहले /practice कमांड चलाएं ताकि मैं आपसे सवाल पूछ सकूं।")
        return

    msg = await update.message.reply_text("⏳ आपकी आवाज सुनी जा रही है, कृपया थोड़ा इंतजार करें...")

    try:
        # Telegram से Voice फाइल डाउनलोड करना
        voice_file = await update.message.voice.get_file()
        ogg_path = "user_voice.ogg"
        wav_path = "user_voice.wav"
        await voice_file.download_to_drive(ogg_path)

        # OGG को WAV में कन्वर्ट करना
        sound = AudioSegment.from_ogg(ogg_path)
        sound.export(wav_path, format="wav")

        # Speech to Text बदलना
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            spoken_text = recognizer.recognize_google(audio_data, language="en-US")

        expected_text = context.user_data.get("expected_answer", "")

        # टेंपरेरी फाइल डिलीट करना
        if os.path.exists(ogg_path): os.remove(ogg_path)
        if os.path.exists(wav_path): os.remove(wav_path)

        # उत्तर दिखाना
        response_text = (
            f"✅ *आपका बोला गया उत्तर:*\n\"{spoken_text}\"\n\n"
            f"💡 *सही उत्तर (फाइल के अनुसार):*\n\"{expected_text}\"\n\n"
            "अगले सवाल के लिए /practice टाइप करें।"
        )

        await msg.edit_text(response_text, parse_mode="Markdown")

    except sr.UnknownValueError:
        await msg.edit_text("❌ आपकी आवाज साफ समझ नहीं आई। कृपया थोड़ा तेज और साफ बोलकर दोबारा Voice Note भेजें।")
    except Exception as e:
        await msg.edit_text(f"⚠️️ एरर आया: {str(e)}")

# फाइल अपलोड संभालना (.txt file)
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if doc.file_name.endswith(".txt"):
        file = await doc.get_file()
        await file.download_to_drive(QUESTIONS_FILE)
        qa_dict = load_questions()
        await update.message.reply_text(f"✅ `questions.txt` फाइल अपडेट हो गई है! कुल {len(qa_dict)} सवाल लोड हुए।")
    else:
        await update.message.reply_text("❌ कृपया केवल `.txt` फॉर्मेट की ही फाइल भेजें।")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("practice", practice))
    app.add_handler(CommandHandler("add", add_question))
    app.add_handler(CommandHandler("list", list_questions))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("बोट शुरू हो गया है...")
    app.run_polling()

if __name__ == "__main__":
    main()
