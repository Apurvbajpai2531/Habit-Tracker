import logging

from flask import Flask

from config import Config
from extensions import db, jwt, migrate, cors
from routes.auth_routes import auth_bp
from routes.habit_routes import habit_bp
from utils import error


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(habit_bp, url_prefix="/api")

    # Health Check
    @app.get("/api/health")
    def health():
        return {"status": "ok"}, 200

    # Error Handlers
    @app.errorhandler(404)
    def not_found(e):
        return error("Route not found", 404)

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.exception(e)
        return error("Internal server error", 500)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=Config.DEBUG,
    )