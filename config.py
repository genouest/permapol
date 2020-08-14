import os
from apollo import ApolloInstance


class Config(object):
    APOLLO_USER = os.environ.get('APOLLO_USER')
    APOLLO_PASSWORD = os.environ.get('APOLLO_PASSWORD')
    APOLLO_URL = os.environ.get('APOLLO_URL')
    APOLLO_INSTANCE = ApolloInstance(APOLLO_URL, APOLLO_USER, APOLLO_PASSWORD)
    SECRET_KEY = os.urandom(32)
