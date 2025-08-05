# src/location_handler.py
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from session_store import user_locations, pending_messages
from message_handler import handle_message

async def ask_for_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = KeyboardButton("📍 Compartí tu ubicación", request_location=True)
    markup = ReplyKeyboardMarkup([[button]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "¿Querés que te recomiende un aceite según el clima donde estás?",
        reply_markup=markup
    )

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    location = update.message.location  # type: ignore

    # Guardar ubicación
    user_locations[user_id] = (location.latitude, location.longitude)

    if user_id in pending_messages:
        restored_text = pending_messages.pop(user_id)

        # Simular el mensaje original llamando directamente con override
        await handle_message(update, context, override_text=restored_text)
    else:
        await update.message.reply_text("¡Gracias! Ahora podés hacerme tu consulta 😉")