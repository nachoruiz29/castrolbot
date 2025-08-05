# src/session_store.py

# En memoria: user_id ➝ (lat, lon)
user_locations = {}

# Mensaje pendiente cuando el usuario aún no compartió ubicación
pending_messages = {}

# Historial por usuario (para mantener conversación)
user_histories = {}