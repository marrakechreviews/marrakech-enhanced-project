import os
from dotenv import load_dotenv
from pymongo import MongoClient
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from bson.objectid import ObjectId
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# MongoDB connection
MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    print("Error: MONGODB_URI environment variable not set.")
    # Fallback for local testing if .env is not loaded, but should be set for deployment
    MONGO_URI = "mongodb://localhost:27017/marrakech_reviews"

try:
    client = MongoClient(MONGO_URI)
    db = client.get_default_database() # Gets the database specified in the URI
    print(f"Connected to MongoDB: {db.name}")
except Exception as e:
    print(f"MongoDB connection error: {e}")
    db = None # Set db to None if connection fails

# --- Helper function for CORS --- #
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response

@app.after_request
def after_request(response):
    return add_cors_headers(response)

@app.route("/api/v1/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "API is running"}), 200

# --- User Registration (for testing) ---
@app.route("/api/v1/register", methods=["POST"])
def register_user():
    if not db: return jsonify({"success": False, "error": "Database not connected"}), 500
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user") # Default role is user

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 400

    if db.users.find_one({"email": email}):
        return jsonify({"success": False, "error": "User with this email already exists"}), 409

    hashed_password = generate_password_hash(password)
    user_id = db.users.insert_one({
        "email": email,
        "password": hashed_password,
        "role": role,
        "username": email.split("@")[0], # Simple username from email
        "isActive": True,
        "createdAt": datetime.utcnow(),
        "lastLogin": datetime.utcnow()
    }).inserted_id

    return jsonify({"success": True, "message": "User registered successfully", "userId": str(user_id)}), 201

# --- User Login ---
@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    if not db: return jsonify({"success": False, "error": "Database not connected"}), 500
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = db.users.find_one({"email": email})

    if user and check_password_hash(user["password"], password):
        access_token = create_access_token(identity=str(user["_id"]), additional_claims={"role": user["role"]})
        return jsonify({"success": True, "message": "Login successful", "access_token": access_token, "role": user["role"]}), 200
    else:
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

# --- Articles API ---
@app.route("/api/v1/articles", methods=["GET"])
def get_articles():
    if not db: return jsonify({"success": False, "error": "Database not connected"}), 500
    try:
        articles = list(db.articles.find({}))
        for article in articles:
            article["_id"] = str(article["_id"])
        return jsonify({"success": True, "data": articles, "message": "Articles retrieved successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- Reviews API ---
@app.route("/api/v1/reviews", methods=["GET"])
def get_reviews():
    if not db: return jsonify({"success": False, "error": "Database not connected"}), 500
    try:
        reviews = list(db.reviews.find({}))
        for review in reviews:
            review["_id"] = str(review["_id"])
        return jsonify({"success": True, "data": reviews, "message": "Reviews retrieved successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- Users API (Admin only) ---
@app.route("/api/v1/users", methods=["GET"])
@jwt_required()
def get_users():
    if not db: return jsonify({"success": False, "error": "Database not connected"}), 500
    current_user_id = get_jwt_identity()
    user = db.users.find_one({"_id": ObjectId(current_user_id)})

    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    users = list(db.users.find({}))
    for u in users:
        u["_id"] = str(u["_id"])
        u.pop("password", None) # Remove password hash for security
    return jsonify({"success": True, "data": users, "message": "Users retrieved successfully"}), 200

# Vercel entry point
from vercel_app import app as vercel_app

if __name__ == "__main__":
    app.run(debug=True)


