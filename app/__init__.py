from flask import Flask
from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome
from flask_caching import Cache
from config import Config
from flask_apscheduler import APScheduler

app = Flask(__name__)
bootstrap = Bootstrap(app)
fa = FontAwesome(app)
app.config.from_object(Config)
cache = Cache(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from app import routes
