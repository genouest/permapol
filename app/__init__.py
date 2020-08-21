from . import routes

from config import Config

from .middleware import PrefixMiddleware

from flask import Flask

from flask_apscheduler import APScheduler

from flask_bootstrap import Bootstrap

from flask_caching import Cache

from flask_fontawesome import FontAwesome

app = Flask(__name__)
with app.app_context():
    bootstrap = Bootstrap(app)
    fa = FontAwesome(app)
    app.config.from_object(Config)
    cache = Cache(app)
    app.cache = cache
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    app.register_blueprint(routes.app)

    if app.config.get("PROXY_PREFIX"):
        app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=app.config.get("PROXY_PREFIX").rstrip("/"))

    if app.config.get("USER_AUTOCOMPLETE").lower() == "true":
        # Cache user list
        routes._get_all_users()
        scheduler.add_job(func=routes._get_all_users, trigger='interval', args=["True"], minutes=59, id="users_job")

    if app.config.get("CRON_SYNC").lower() == "true":
        scheduler.add_job(func=routes._sync_permissions, trigger='interval', days=1, id="sync_job")
