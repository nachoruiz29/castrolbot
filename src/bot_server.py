# src/bot_server.py
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
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
    user_input = update.message.text.strip().lower() if update.message and update.message.text else ""
    # Asegura que user_data sea un dict
    if context.user_data is None:
        context.user_data = {}

    # Pregunta inicial para mejorar recomendación con ubicación
    if not context.user_data.get("ubicacion_preguntada"):
        context.user_data["ubicacion_preguntada"] = True
        context.user_data["awaiting_location_permission"] = True
        pending_messages[user_id] = update.message.text if update.message else ""
        await update.message.reply_text("Para hacer una mejor recomendación (considerando clima y puntos de venta), ¿quieres compartirme tu ubicación?")
        return

    # Si estamos esperando respuesta sobre la ubicación
    if context.user_data.get("awaiting_location_permission"):
        if user_input in ["no", "no quiero", "prefiero que no"]:
            context.user_data["location_permission_denied"] = True
            context.user_data["awaiting_location_permission"] = False
            await update.message.reply_text("Perfecto, no te pediré la ubicación. Continuemos con el análisis.")
            # Procesa el mensaje pendiente si existe
            if pending_messages.get(user_id):
                if update.message:
                    update.message.text = pending_messages[user_id]
                await handle_message(update, context)
                pending_messages.pop(user_id, None)
                # Enviar explícitamente la recomendación si fue detectada
                if context.user_data.get("producto_detectado"):
                    producto = context.user_data["producto_detectado"]
                    await update.message.reply_text(f"Producto detectado: {producto}")
                    # Aquí podrías agregar la lógica para enviar la recomendación completa si no se envió
            return
        elif user_input in ["sí", "si", "dale", "ok", "quiero"]:
            context.user_data["awaiting_location_permission"] = False
            # Si ya tenemos la ubicación, no la volvemos a pedir
            print(f"[LOG] ¿El usuario tiene ubicación? {'Sí' if user_id in user_locations else 'No'} (user_id={user_id})")
            if user_id in user_locations:
                await update.message.reply_text("Ya tengo tu ubicación, la usaré para mejorar la recomendación y mostrarte puntos de venta.")
                if pending_messages.get(user_id):
                    if update.message:
                        update.message.text = pending_messages[user_id]
                    await handle_message(update, context)
                    pending_messages.pop(user_id, None)
                # No enviar ningún mensaje extra aquí, solo continuar
                return
            else:
                await ask_for_location(update, context)
                return
        else:
            await update.message.reply_text("¿Quieres compartirme tu ubicación para mejorar la recomendación?")
            return

    # Si ya tiene ubicación y hay mensaje pendiente, procesa ese mensaje
    print("donde no entra:",user_id in user_locations)
    if user_id in user_locations and pending_messages.get(user_id):
        if update.message:
            update.message.text = pending_messages[user_id]
        await handle_message(update, context)
        pending_messages.pop(user_id, None)
        # Preguntar por puntos de venta justo después de la recomendación
        if context.user_data.get("producto_detectado") and user_id in user_locations and not context.user_data.get("awaiting_map_confirmation"):
            producto = context.user_data.get("producto_detectado")
            lat, lon = user_locations.get(user_id, (None, None))
            print(f"[LOG] Producto detectado: {producto}. Ubicación usuario: lat={lat}, lon={lon} (user_id={user_id})")
            if update.message:
                await update.message.reply_text(f"Recomendación: {producto}")
                await update.message.reply_text(f"¿Te gustaría ver los puntos de venta más cercanos?")
            context.user_data["awaiting_map_confirmation"] = True
        return

    # Si no hay nada pendiente, sigue el flujo normal
    await handle_message(update, context)
    # Preguntar por puntos de venta justo después de la recomendación en el flujo normal
    if context.user_data.get("producto_detectado") and user_id in user_locations and not context.user_data.get("awaiting_map_confirmation"):
        producto = context.user_data.get("producto_detectado")
        lat, lon = user_locations.get(user_id, (None, None))
        print(f"[LOG] Producto detectado: {producto}. Ubicación usuario: lat={lat}, lon={lon} (user_id={user_id}) [flujo normal]")
        if update.message:
            await update.message.reply_text(f"Recomendación: {producto}")
            await update.message.reply_text(f"¿Te gustaría ver los puntos de venta más cercanos?")
        context.user_data["awaiting_map_confirmation"] = True
    # Manejo de respuesta a puntos de venta usando awaiting_map_confirmation
    if context.user_data.get("awaiting_map_confirmation"):
        if user_input in ["sí", "si", "dale", "ok", "quiero"]:
            context.user_data["awaiting_map_confirmation"] = False
            pending_messages.pop(user_id, None)
            producto = context.user_data.get("producto_detectado")
            lat, lon = user_locations.get(user_id, (None, None))
            print(f"[LOG] Mostrando puntos de venta para producto: {producto}, ubicación: lat={lat}, lon={lon} (user_id={user_id})")
            if update.message:
                await update.message.reply_text("Aquí tienes los puntos de venta más cercanos:")
            stations = get_nearby_stations(user_lat=lat, user_lon=lon)
            await send_location_map(update, context, stations)
            return
        elif user_input in ["no", "prefiero que no", "no quiero"]:
            context.user_data["awaiting_map_confirmation"] = False
            pending_messages.pop(user_id, None)
            if update.message:
                await update.message.reply_text("Perfecto, si necesitas ver los puntos de venta más adelante, solo avísame.")
            return

# --- MAIN ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_error_handler(error_handler)

    # Orden importa: primero ubicación, luego entrypoint
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, entrypoint))

    print("🤖 BOT ACTIVO")
    app.run_polling()