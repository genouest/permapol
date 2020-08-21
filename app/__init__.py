from app import routes
from app.middleware import PrefixMiddleware

from config import Config

from flask import Flask

from flask_bootstrap import Bootstrap

from flask_caching import Cache

from flask_fontawesome import FontAwesome
from flask_apscheduler import APScheduler

app = Flask(__name__)
bootstrap = Bootstrap(app)
fa = FontAwesome(app)
app.config.from_object(Config)
cache = Cache(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

if app.config.get("PROXY_PREFIX"):
    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=app.config.get("PROXY_PREFIX").rstrip("/"))

if app.config.get("USER_AUTOCOMPLETE").lower() == "true":
    # Cache user list
    routes._get_all_users()
    scheduler.add_job(func=routes._get_all_users, trigger='interval', args=["True"], minutes=59, id="users_job")

if app.config.get("CRON_SYNC").lower() == "true":
    scheduler.add_job(func=routes._sync_permissions, trigger='interval', days=1, id="sync_job")
