import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'marrakech-reviews-secret-key-2025')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-marrakech-2025')
app.config["MONGO_URI"] = os.getenv("MONGO_URI") # Remove the fallback

# Initialize extensions
mongo = PyMongo(app)
jwt = JWTManager(app)
CORS(app, origins="*")

# Initialize MongoDB connection
from src.models.database import mongo_db
mongo_db.init_app(app)

# Import and register blueprints
from src.routes.auth import auth_bp
from src.routes.users import users_bp
from src.routes.articles import articles_bp
from src.routes.reviews import reviews_bp
from src.routes.categories import categories_bp
from src.routes.wallet import wallet_bp
from src.routes.upload import upload_bp
from src.routes.settings import settings_bp
from src.routes.notifications import notifications_bp
from src.routes.analytics import analytics_bp
from src.routes.tripadvisor import tripadvisor_bp
from src.routes.search import search_bp
from src.routes.admin import admin_bp
from src.routes.media import media_bp
from src.routes.coupons import coupons_bp

app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
app.register_blueprint(users_bp, url_prefix='/api/v1/users')
app.register_blueprint(articles_bp, url_prefix='/api/v1/articles')
app.register_blueprint(reviews_bp, url_prefix='/api/v1/reviews')
app.register_blueprint(categories_bp, url_prefix='/api/v1/categories')
app.register_blueprint(wallet_bp, url_prefix='/api/v1/wallet')
app.register_blueprint(upload_bp, url_prefix='/api/v1/upload')
app.register_blueprint(settings_bp, url_prefix='/api/v1/settings')
app.register_blueprint(notifications_bp, url_prefix='/api/v1/notifications')
app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')
app.register_blueprint(tripadvisor_bp, url_prefix='/api/v1/tripadvisor')
app.register_blueprint(search_bp, url_prefix='/api/v1/search')
app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
app.register_blueprint(media_bp, url_prefix='/api/v1/media')
app.register_blueprint(coupons_bp, url_prefix='/api/v1/coupons')

# API info route
@app.route('/api/v1')
def api_info():
    return jsonify({
        "success": True,
        "message": "Marrakech Reviews API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users", 
            "reviews": "/api/v1/reviews",
            "articles": "/api/v1/articles",
            "categories": "/api/v1/categories",
            "media": "/api/v1/media",
            "admin": "/api/v1/admin"
        }
    })

# Health check route
@app.route('/health')
def health_check():
    return jsonify({
        "success": True,
        "message": "API is healthy",
        "status": "running"
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

