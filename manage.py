import os
from app import create_app
from flask_script import Manager, Server

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

manager.add_command("runserver", Server(host=app.config['HOST'], port=app.config['PORT']))

if __name__ == '__main__':
    manager.run()
