"""
Main Flask application entry point.
"""
import os
import sys
import logging
from pathlib import Path
from flask import Flask, jsonify

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import DATABASE_URI
from extensions import db, cors

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Application factory pattern."""
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB max

    # Initialize extensions
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from routes.feedback import feedback_bp
    from routes.dashboard import dashboard_bp
    from routes.model_routes import model_bp
    from routes.export import export_bp

    app.register_blueprint(feedback_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(model_bp, url_prefix='/api/model')
    app.register_blueprint(export_bp, url_prefix='/api/export')

    # Health check
    @app.route('/api/health')
    def health():
        from ml.predict import is_model_loaded
        model_ready = is_model_loaded()
        try:
            with app.app_context():
                db.session.execute(db.text('SELECT 1'))
            db_ready = True
        except Exception:
            db_ready = False

        status = "healthy" if (model_ready and db_ready) else "degraded"
        return jsonify({
            "status": status,
            "model_loaded": model_ready,
            "database_connected": db_ready,
            "api_version": "1.0.0",
        }), 200 if status == "healthy" else 503

    # Courses list
    @app.route('/api/courses')
    def get_courses():
        from models import Course
        courses = Course.query.order_by(Course.course_name).all()
        return jsonify({
            "success": True,
            "courses": [c.to_dict() for c in courses]
        })

    # Global error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "error": "Bad request", "message": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

    # Create tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables initialized")
        _seed_model_info()

    return app


def _seed_model_info():
    """Seed model information from saved config if available."""
    import json
    from models import ModelInformation
    from config import MODEL_CONFIG_PATH
    from datetime import datetime

    if MODEL_CONFIG_PATH.exists() and ModelInformation.query.count() == 0:
        try:
            with open(MODEL_CONFIG_PATH, 'r') as f:
                config = json.load(f)
            info = ModelInformation(
                model_name=config.get('model_name', 'Bi-LSTM Emotion Classifier'),
                model_version=config.get('model_version', '1.0'),
                dataset_name=config.get('dataset', 'GoEmotions'),
                accuracy=config.get('test_accuracy'),
                macro_f1=None,
                training_date=datetime.fromisoformat(config['trained_at']) if 'trained_at' in config else None,
            )
            db.session.add(info)
            db.session.commit()
        except Exception as e:
            logger.warning(f"Could not seed model info: {e}")


if __name__ == '__main__':
    app = create_app()
    logger.info("Starting Flask development server...")
    logger.info("Backend API: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
