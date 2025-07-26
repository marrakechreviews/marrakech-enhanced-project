from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime, timedelta
import re
import secrets
import string

from src.models.database import mongo_db, create_response, serialize_doc

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def generate_verification_token():
    """Generate random verification token"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'firstName', 'lastName']
        for field in required_fields:
            if not data.get(field):
                return jsonify(create_response(
                    success=False,
                    error={"code": "MISSING_FIELD", "message": f"{field} is required"}
                )), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        first_name = data['firstName'].strip()
        last_name = data['lastName'].strip()
        
        # Validate email format
        if not validate_email(email):
            return jsonify(create_response(
                success=False,
                error={"code": "INVALID_EMAIL", "message": "Invalid email format"}
            )), 400
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify(create_response(
                success=False,
                error={"code": "WEAK_PASSWORD", "message": message}
            )), 400
        
        # Check if user already exists
        existing_user = mongo_db.db.users.find_one({
            "$or": [{"email": email}, {"username": username}]
        })
        
        if existing_user:
            field = "email" if existing_user.get('email') == email else "username"
            return jsonify(create_response(
                success=False,
                error={"code": "USER_EXISTS", "message": f"User with this {field} already exists"}
            )), 409
        
        # Create new user
        hashed_password = generate_password_hash(password)
        verification_token = generate_verification_token()
        
        user_doc = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "firstName": first_name,
            "lastName": last_name,
            "role": "user",  # Default role
            "avatar": "",
            "isActive": True,
            "isEmailVerified": False,
            "emailVerificationToken": verification_token,
            "wallet": {
                "balance": 100,  # Welcome bonus
                "transactions": [{
                    "type": "credit",
                    "amount": 100,
                    "description": "Welcome bonus",
                    "timestamp": datetime.utcnow(),
                    "transactionId": str(ObjectId())
                }]
            },
            "preferences": {
                "language": "en",
                "notifications": True
            },
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "lastLogin": None
        }
        
        result = mongo_db.db.users.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        
        # Create access and refresh tokens
        access_token = create_access_token(
            identity=str(result.inserted_id),
            additional_claims={"role": "user"}
        )
        refresh_token = create_refresh_token(identity=str(result.inserted_id))
        
        # Remove sensitive data from response
        user_data = serialize_doc(user_doc)
        del user_data['password']
        del user_data['emailVerificationToken']
        
        return jsonify(create_response(
            success=True,
            data={
                "user": user_data,
                "accessToken": access_token,
                "refreshToken": refresh_token
            },
            message="User registered successfully"
        )), 201
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "REGISTRATION_ERROR", "message": str(e)}
        )), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_CREDENTIALS", "message": "Email and password are required"}
            )), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Find user by email
        user = mongo_db.db.users.find_one({"email": email})
        
        if not user or not check_password_hash(user['password'], password):
            return jsonify(create_response(
                success=False,
                error={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}
            )), 401
        
        if not user.get('isActive', True):
            return jsonify(create_response(
                success=False,
                error={"code": "ACCOUNT_DISABLED", "message": "Account is disabled"}
            )), 403
        
        # Update last login
        mongo_db.db.users.update_one(
            {"_id": user['_id']},
            {"$set": {"lastLogin": datetime.utcnow()}}
        )
        
        # Create access and refresh tokens
        access_token = create_access_token(
            identity=str(user['_id']),
            additional_claims={"role": user['role']}
        )
        refresh_token = create_refresh_token(identity=str(user['_id']))
        
        # Remove sensitive data from response
        user_data = serialize_doc(user)
        del user_data['password']
        if 'emailVerificationToken' in user_data:
            del user_data['emailVerificationToken']
        
        return jsonify(create_response(
            success=True,
            data={
                "user": user_data,
                "accessToken": access_token,
                "refreshToken": refresh_token
            },
            message="Login successful"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "LOGIN_ERROR", "message": str(e)}
        )), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        
        # Get user from database
        user = mongo_db.db.users.find_one({"_id": ObjectId(current_user_id)})
        
        if not user or not user.get('isActive', True):
            return jsonify(create_response(
                success=False,
                error={"code": "USER_NOT_FOUND", "message": "User not found or inactive"}
            )), 404
        
        # Create new access token
        access_token = create_access_token(
            identity=current_user_id,
            additional_claims={"role": user['role']}
        )
        
        return jsonify(create_response(
            success=True,
            data={"accessToken": access_token},
            message="Token refreshed successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "REFRESH_ERROR", "message": str(e)}
        )), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        # In a production environment, you would add the token to a blacklist
        # For now, we'll just return a success response
        return jsonify(create_response(
            success=True,
            message="Logout successful"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "LOGOUT_ERROR", "message": str(e)}
        )), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_EMAIL", "message": "Email is required"}
            )), 400
        
        email = data['email'].strip().lower()
        
        # Find user by email
        user = mongo_db.db.users.find_one({"email": email})
        
        if user:
            # Generate reset token
            reset_token = generate_verification_token()
            reset_expires = datetime.utcnow() + timedelta(hours=1)
            
            # Update user with reset token
            mongo_db.db.users.update_one(
                {"_id": user['_id']},
                {
                    "$set": {
                        "passwordResetToken": reset_token,
                        "passwordResetExpires": reset_expires
                    }
                }
            )
            
            # In a real application, you would send an email here
            # For now, we'll just return the token (remove this in production)
            
        # Always return success to prevent email enumeration
        return jsonify(create_response(
            success=True,
            message="If an account with that email exists, a password reset link has been sent"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "FORGOT_PASSWORD_ERROR", "message": str(e)}
        )), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        
        required_fields = ['token', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify(create_response(
                    success=False,
                    error={"code": "MISSING_FIELD", "message": f"{field} is required"}
                )), 400
        
        token = data['token']
        password = data['password']
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify(create_response(
                success=False,
                error={"code": "WEAK_PASSWORD", "message": message}
            )), 400
        
        # Find user with valid reset token
        user = mongo_db.db.users.find_one({
            "passwordResetToken": token,
            "passwordResetExpires": {"$gt": datetime.utcnow()}
        })
        
        if not user:
            return jsonify(create_response(
                success=False,
                error={"code": "INVALID_TOKEN", "message": "Invalid or expired reset token"}
            )), 400
        
        # Update password and remove reset token
        hashed_password = generate_password_hash(password)
        mongo_db.db.users.update_one(
            {"_id": user['_id']},
            {
                "$set": {
                    "password": hashed_password,
                    "updatedAt": datetime.utcnow()
                },
                "$unset": {
                    "passwordResetToken": "",
                    "passwordResetExpires": ""
                }
            }
        )
        
        return jsonify(create_response(
            success=True,
            message="Password reset successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "RESET_PASSWORD_ERROR", "message": str(e)}
        )), 500

@auth_bp.route('/verify-email', methods=['GET'])
def verify_email():
    try:
        token = request.args.get('token')
        
        if not token:
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_TOKEN", "message": "Verification token is required"}
            )), 400
        
        # Find user with verification token
        user = mongo_db.db.users.find_one({"emailVerificationToken": token})
        
        if not user:
            return jsonify(create_response(
                success=False,
                error={"code": "INVALID_TOKEN", "message": "Invalid verification token"}
            )), 400
        
        if user.get('isEmailVerified', False):
            return jsonify(create_response(
                success=True,
                message="Email already verified"
            )), 200
        
        # Update user as verified
        mongo_db.db.users.update_one(
            {"_id": user['_id']},
            {
                "$set": {
                    "isEmailVerified": True,
                    "updatedAt": datetime.utcnow()
                },
                "$unset": {"emailVerificationToken": ""}
            }
        )
        
        return jsonify(create_response(
            success=True,
            message="Email verified successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "VERIFICATION_ERROR", "message": str(e)}
        )), 500

