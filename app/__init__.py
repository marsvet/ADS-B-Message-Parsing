from flask import Flask
from config import config
from datetime import datetime

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.template_filter('ctime')
    def timectime(s):
        return format(datetime.fromtimestamp(s), '%Y-%m-%d %H:%M:%S')

    return app
