from telegram import Update
from telegram.ext import ContextTypes
import math

# Mock de estaciones (nombre, lat, lon)
STATIONS = [
    ("Axion Pilar", -34.4701, -58.9146),
    ("Distribuidor Castrol Pilar", -34.4605, -58.9188),
    ("Axion Ruta 25", -34.4531, -58.9081),
    ("Castrol Express KM50", -34.4539, -58.9119),
    # Agregá más si querés
]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2)
    return R * 2 * math.asin(math.sqrt(a))

def get_nearby_stations(user_lat, user_lon, max_km=10):
    return [
        (name, lat, lon)
        for name, lat, lon in STATIONS
        if haversine(user_lat, user_lon, lat, lon) <= max_km 
    ]

async def send_location_map(update: Update, context: ContextTypes.DEFAULT_TYPE, stations):
    for name, lat, lon in stations:
        await context.bot.send_location(chat_id=update.effective_chat.id, latitude=lat, longitude=lon)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{name}")