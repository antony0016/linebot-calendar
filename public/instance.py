import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from flask import Flask
from flask_cors import CORS

from linebot import (
    LineBotApi, WebhookHandler
)

load_dotenv()

# db
Base = declarative_base()
engine = create_engine(os.getenv('CONNECT_STRING'), echo=True)

# linebot
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# flask instance
flask_instance: Flask = Flask(__name__)
CORS(flask_instance)


# flask_instance


def logger_setting(app: Flask):
    global flask_instance
    flask_instance = app
