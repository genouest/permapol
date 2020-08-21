import os

from apollo import ApolloInstance


class Config(object):
    if not(os.environ.get('APOLLO_USER') and os.environ.get('APOLLO_PASSWORD') and os.environ.get('APOLLO_URL')):
        raise Exception("Missing either APOLLO_USER, APOLLO_PASSWORD or APOLLO_URL env variable")

    APOLLO_USER = os.environ.get('APOLLO_USER')
    APOLLO_PASSWORD = os.environ.get('APOLLO_PASSWORD')
    APOLLO_URL = os.environ.get('APOLLO_URL')
    PROXY_HEADER = os.environ.get("PROXY_HEADER", "REMOTE_USER")
    USER_AUTOCOMPLETE = os.environ.get('USER_AUTOCOMPLETE', "FALSE")
    CRON_SYNC = os.environ.get('CRON_SYNC', "FALSE")
    PROXY_PREFIX = os.environ.get('PROXY_PREFIX')

    APOLLO_INSTANCE = ApolloInstance(APOLLO_URL, APOLLO_USER, APOLLO_PASSWORD)
    SECRET_KEY = os.urandom(32)
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 3600
