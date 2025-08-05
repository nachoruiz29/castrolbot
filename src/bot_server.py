import os
from dotenv import load_dotenv
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from rag_utils import get_relevant_context  # opcional

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# --- PROMPT BASE ---
SYSTEM_PROMPT = """Eres un experto en lubricantes CASTROL en Argentina.
Según el tipo de vehículo, condiciones de uso, edad del motor, uso urbano o rutero, y kilometraje,
debés recomendar el tipo y la línea de aceite CASTROL más adecuada disponible en el país.
Usá nombres comerciales reales: EDGE, GTX, MAGNATEC, VECTON, etc.
Siempre aclarás si es mineral, sintético o semisintético. Si hay dudas, hacé preguntas para afinar la recomendación."""

# --- PROCESAMIENTO DE PREGUNTAS ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    # Consulta a RAG (opcional)
    context_text = get_relevant_context(user_input)  # puede devolver "" si no hay index

    full_prompt = f"{context_text}\n\nUsuario: {user_input}"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.3,
        max_tokens=800
    )

    reply = response.choices[0].message["content"]
    await update.message.reply_text(reply)

# --- MAIN ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 BOT ACTIVO")
    app.run_polling()