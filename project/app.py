import os

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_pymongo import PyMongo


MONGODB_PASSWD = os.environ.get('MONGODB_PASSWD', '')
MONGODB_USER = os.environ.get('MONGODB_USER', '')
MONGODB_LOCAL = os.environ.get('MONGODB_LOCAL', False)
MONGODB_HOSTNAME = os.environ.get('MONGODB_HOSTNAME', 'localhost')
MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE', 'videothemes')

csrf = CSRFProtect()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='zY0ZI4BtQ50OuZBftm6ckA',
        STATIC_FOLDER='./static',
        MONGODB_DATABASE=MONGODB_DATABASE,
    )
    csrf.init_app(app)

    if test_config:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if MONGODB_PASSWD and not MONGODB_LOCAL:  # it's *production*
        app.config['MONGO_URI'] = \
            "mongodb+srv://{}:{}@cluster0.jhacs.mongodb.net/{}?retryWrites=true&w=majority".format(
                MONGODB_USER, MONGODB_PASSWD, app.config['MONGODB_DATABASE'])
    else:
        app.config['MONGO_URI'] = "mongodb://%s:27017/%s" % (MONGODB_HOSTNAME,
                                                             app.config['MONGODB_DATABASE'])

    # mongo client last
    mongo = PyMongo(app)
    app.mongo = mongo

    try:
        from my_app import bp  # noqa - when runing from container
    except ImportError:
        from .my_app import bp
    app.register_blueprint(bp)
    return app


if __name__ == "__main__":
    ENV_DEBUG = os.environ.get("APP_DEBUG", True)
    ENV_PORT = os.environ.get("APP_PORT", 5000)
    app = create_app()
    app.run(host='0.0.0.0', port=ENV_PORT, debug=ENV_DEBUG)
