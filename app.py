# app.py - Dash initialization

from dash import Dash
import os
from dotenv import load_dotenv
from config import FONT_URL, LOCAL_STYLES_PATH

load_dotenv()

app = Dash(
    __name__,
    external_stylesheets=[FONT_URL, LOCAL_STYLES_PATH],
    suppress_callback_exceptions=True
)

server = app.server  # Para despliegue (Gunicorn/Procfile)
