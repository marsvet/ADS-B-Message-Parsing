import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = True
    TESTING = False
    HOST = '127.0.0.1'
    PORT = 5000

    @staticmethod
    def init_app(app):
        pass

config = {
    'default': Config
}
