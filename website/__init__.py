import json

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mqtt import Mqtt

db = SQLAlchemy()
mqtt = Mqtt()


def create_app():
    from .secret import SECRET_KEY, MQTT_NAME, MQTT_PASS
    from .settings import DB_NAME, DB_URL, MQTT_BROKER

    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['MQTT_BROKER_URL'] = MQTT_BROKER
    app.config['MQTT_BROKER_PORT'] = 1883  # default port for non-tls connection
    app.config['MQTT_USERNAME'] = MQTT_NAME
    app.config['MQTT_PASSWORD'] = MQTT_PASS
    app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
    app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes
    # app.config['MQTT_TLS_INSECURE'] = True

    with app.app_context():
        db.init_app(app)
        mqtt.init_app(app)

    @mqtt.on_connect()
    def handle_connect(client, userdata, flags, rc):
        if rc == 0:
            print('Connected successfully')
            mqtt.subscribe('home/prezencka')  # subscribe topic
            mqtt.subscribe('home/ospravedlnenie')  # subscribe topic
        else:
            print('Bad connection. Code:', rc)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Ziak, Predmet, predmety_ucitelov, MQTT, Hodina, Attendance

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    from .settings import DB_NAME

    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print("Created DB!")
