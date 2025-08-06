# CastrolBot

Bot de Telegram para recomendar aceites Castrol en Argentina y mostrar puntos de venta cercanos según la ubicación del usuario.

## Características

- Recomienda aceites Castrol personalizados usando IA.
- Solicita y procesa la ubicación del usuario.
- Muestra puntos de venta cercanos en el mapa.
- Conversa en español neutro.
- Utiliza un catálogo de ubicaciones en CSV.

## Estructura del proyecto

```
castrolBot/
├── src/
│   ├── bot_server.py
│   ├── location_handler.py
│   ├── message_handler.py
│   ├── map_utils.py
│   ├── session_store.py
│   └── ...
├── saleslocations/
│   └── sites.csv
├── .env
├── requirements.txt
└── README.md
```

## Instalación

1. Clona el repositorio.
2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Crea el archivo `.env` con tu token de Telegram:
   ```
   TELEGRAM_BOT_TOKEN=tu_token_aqui
   ```

## Uso

Ejecuta el bot:
```
python src/bot_server.py
```

## Formato del archivo CSV

El archivo `saleslocations/sites.csv` debe tener el siguiente encabezado:

```
Name,Dirección,Ciudad,Provincia,LATITUD,LONGITUD
```

## Créditos

Desarrollado por el equipo Castrol Argentina.

##