from flask import Flask
from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome
from config import Config

app = Flask(__name__)
bootstrap = Bootstrap(app)
fa = FontAwesome(app)
app.config.from_object(Config)

from app import routes
