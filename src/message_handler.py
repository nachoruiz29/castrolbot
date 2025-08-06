# src/message_handler.py
import os
from openai import OpenAI
from dotenv import load_dotenv
from rag_utils import get_relevant_context
from climate_utils import infer_climate_from_location
from telegram.ext import ContextTypes
from telegram import Update
from session_store import user_histories, user_locations, pending_messages
from extract_product_name import extract_product_name
from map_utils import get_nearby_stations, send_location_map

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """Sos un asesor técnico experto en lubricantes CASTROL Argentina.
Tu tarea es recomendar el aceite más adecuado para el motor consultado por el usuario,
pero solo si tenés suficiente información para hacerlo de manera responsable.

Debés pedir más detalles si falta alguno de los siguientes factores importantes:

- Marca y modelo del vehículo
- Año de fabricación
- Cantidad de kilómetros recorridos
- Tipo de uso: urbano, ruta, campo o mixto
- Presencia de filtro de partículas (DPF) si es diésel y solo si el vehiculo es diesel
- Si el vehiculo es nafta NO pedir la información del DPF

Si alguno de estos datos no fue proporcionado, DEBÉS pedirlos primero antes de responder PERO PIDELOS DE A UNO Y EN FORMA COLOQUIAL, como si fueras un vendedor.

Una vez que tengas los datos completos, buscá en el catálogo CASTROL Argentina el aceite más adecuado.
Si no sabés el clima del usuario, ofrecé dos opciones: una para clima frío (ej. Patagonia) y otra para templado o cálido.

Pero si sabés que el usuario está en clima {clima}, entonces recomendá SOLO la opción adecuada para ese clima.
Explicá las diferencias y en qué caso usar cada uno.

Respondé en forma de tabla con:
- Producto Castrol
- Tipo (Sintético, Semi, Mineral)
- Viscosidad (ej: 5W-30)
- Justificación técnica de la recomendación.

Si el usuario compartió su ubicación, luego de mostrar el producto ofrecé si desea ver puntos de venta cercanos.

Respondé siempre en español neutro para Argentina."""

users_last_product = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, override_text: str | None = None):
    user_id = update.effective_user.id  # type: ignore
    user_input = override_text if override_text else update.message.text  # type: ignore

    # Si no tiene ubicación todavía, guardamos el mensaje y pedimos ubicación
    if user_id not in user_locations:
        pending_messages[user_id] = user_input
        from location_handler import ask_for_location  # import local para evitar ciclos
        await ask_for_location(update, context)
        return

    # Clima si hay ubicación
    climate_hint = ""
    lat, lon = user_locations[user_id]
    clima = infer_climate_from_location(lat, lon)
    climate_hint = f"El usuario está en una zona de clima {clima}.\n"

    # Inicializar historial
    if user_id not in user_histories:
        user_histories[user_id] = []

    # Contexto RAG
    context_text = get_relevant_context(user_input)

    # Armar prompt para OpenAI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if climate_hint:
        messages.append({"role": "user", "content": climate_hint.strip()})
    messages.extend(user_histories[user_id])
    if context_text:
        messages.append({"role": "user", "content": context_text})
    messages.append({"role": "user", "content": user_input})

    # Consulta a OpenAI
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.3,
        max_tokens=800
    )
    reply = response.choices[0].message.content

    # Guardar historial
    user_histories[user_id].append({"role": "user", "content": user_input})
    user_histories[user_id].append({"role": "assistant", "content": reply})
    user_histories[user_id] = user_histories[user_id][-10:]

    await update.message.reply_text(reply)

    # Solo ofrecer puntos de venta si se detectó un producto
    product_name = extract_product_name(reply)
    print("Producto detectado:", product_name)

    if product_name and product_name.lower() != "el producto recomendado":
        users_last_product[user_id] = product_name
        context.user_data["product_for_map"] = product_name
        await update.message.reply_text(
            f"¿Querés ver dónde adquirir el *{product_name}* cerca tuyo?",
            parse_mode='Markdown'
        )
        context.user_data["awaiting_map_confirmation"] = True


async def handle_yes_no_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()

    if context.user_data.get("awaiting_map_confirmation") and text in ["sí", "si", "dale", "ok", "quiero", "por supuesto"]:
        context.user_data["awaiting_map_confirmation"] = False

        if user_id in user_locations:
            lat, lon = user_locations[user_id]
            product = context.user_data.get("product_for_map", "el producto")
            stations = get_nearby_stations(lat, lon)

            if stations:
                await update.message.reply_text(
                    f"Estos son los puntos de venta cercanos donde podrías conseguir *{product}*:",
                    parse_mode='Markdown'
                )
                await send_location_map(update, context, stations)
            else:
                await update.message.reply_text("No encontré puntos de venta a menos de 10 km de tu ubicación.")
        else:
            await update.message.reply_text("Necesito tu ubicación para mostrarte los puntos cercanos.")
    else:
        context.user_data["awaiting_map_confirmation"] = False