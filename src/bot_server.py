# src/bot_server.py
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram.error import TelegramError
from telegram import Update

from location_handler import handle_location, ask_for_location
from message_handler import handle_message
from map_utils import get_nearby_stations, send_location_map
from session_store import user_locations, pending_messages

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"⚠️ Error: {context.error}")
    if update:
        print(f"🔁 Update problemático: {update}")

# --- Entrypoint unificado ---
async def entrypoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text.strip().lower()
    print("📥 Entró al entrypoint con mensaje:", user_input)

    # Si estamos esperando confirmación para mostrar el mapa
    if context.user_data.get("awaiting_map_confirmation") and user_input in ["sí", "si", "dale", "ok", "quiero", "por supuesto"]:
        context.user_data["awaiting_map_confirmation"] = False
        if user_id in user_locations:
            lat, lon = user_locations[user_id]
            stations = get_nearby_stations(lat, lon)
            if stations:
                await send_location_map(update, context, stations)
            else:
                await update.message.reply_text("No encontré puntos de venta a menos de 10 km de tu ubicación.")
        else:
            await update.message.reply_text("Necesito tu ubicación para mostrarte los puntos cercanos.")
        return

    # Si no tiene ubicación, la pedimos y guardamos el mensaje
    if user_id not in user_locations:
        print("📍 No hay ubicación. Pidiendo ubicación...")
        pending_messages[user_id] = update.message.text
        await ask_for_location(update, context)
        return

    # Continuar con el flujo normal
    await handle_message(update, context)

# --- MAIN ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_error_handler(error_handler)

    # Orden importa: primero ubicación, luego entrypoint
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, entrypoint))

    print("🤖 BOT ACTIVO")
    app.run_polling()