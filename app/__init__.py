from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bcrypt = Bcrypt()


def create_app(config_object=None):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_object or 'app.config.ProductionConfig')

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bcrypt.init_app(app)

    # register blueprints
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .entries import bp as entries_bp
    app.register_blueprint(entries_bp)

    # simple index route
    @app.route('/ping')
    def ping():
        return 'pong'

    return app