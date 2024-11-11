from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = 'trips.db',
        UPLOAD_FOLDER = 'upload_folder'
        )

    with app.app_context():
        from .views import views
        from .auth import auth
        from .db import init_db_command, close_db

        app.register_blueprint(views)
        app.register_blueprint(auth)
        app.teardown_appcontext(close_db)
        app.cli.add_command(init_db_command)
    return app