from telegram import Update
from telegram.ext import ContextTypes
import math
import os
import csv

def load_stations_from_csv():
    stations = []
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saleslocations", "sites.csv")
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
          #  print("lee row:", row)
            name =  row.get("Name") or row.get("\ufeffName")
            try:
                lat = float(row["LATITUD"])
                lon = float(row["LONGITUD"])
                stations.append((name, lat, lon))
            except (ValueError, KeyError):
                continue
    return stations

STATIONS = load_stations_from_csv()
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2)
    return R * 2 * math.asin(math.sqrt(a))

def get_nearby_stations(user_lat, user_lon, max_km=10):
    print(f"[LOG] get_nearby_stations: user_lat={user_lat}, user_lon={user_lon}, max_km={max_km}")
    return [
        (name, lat, lon)
        for name, lat, lon in STATIONS
        if haversine(user_lat, user_lon, lat, lon) <= max_km 
    ]

async def send_location_map(update: Update, context: ContextTypes.DEFAULT_TYPE, stations):
    for name, lat, lon in stations[:3]:
        await context.bot.send_location(chat_id=update.effective_chat.id, latitude=lat, longitude=lon)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{name}")