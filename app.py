"""
OratorHub - Debate & Public Speaking Tournament Platform
Main Flask application
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os

from config import config
from models import db

# Import blueprints
from api.auth import auth_bp
from api.tournaments import tournaments_bp
from api.registrations import registrations_bp
from api.teams import teams_bp
from api.rounds import rounds_bp
from api.scores import scores_bp
from api.sse import sse_bp

def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__, static_folder='.')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tournaments_bp, url_prefix='/api/tournaments')
    app.register_blueprint(registrations_bp, url_prefix='/api/registrations')
    app.register_blueprint(teams_bp, url_prefix='/api/teams')
    app.register_blueprint(rounds_bp, url_prefix='/api/rounds')
    app.register_blueprint(scores_bp, url_prefix='/api/scores')
    app.register_blueprint(sse_bp, url_prefix='/api/stream')
    
    # Serve frontend files
    @app.route('/')
    def index():
        """Serve the main HTML file"""
        return send_from_directory('.', 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        """Serve static files"""
        if os.path.exists(path):
            return send_from_directory('.', path)
        return send_from_directory('.', 'index.html')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'OratorHub API',
            'version': '1.0.0'
        })
    
    # Initialize database
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(host='0.0.0.0', port=5000, debug=True)
