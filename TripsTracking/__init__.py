from flask import Flask
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config(SECRET_KEY='dev')

    with app.app_context():
        from .views import views
        from .auth import auth
        app.register_blueprint(views)
        app.register_blueprint(auth)
    return app