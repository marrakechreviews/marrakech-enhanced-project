from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from bson import ObjectId
from datetime import datetime

from src.models.database import mongo_db, create_response, serialize_doc, serialize_docs, paginate_query
from src.utils.decorators import admin_required, user_required, owner_or_admin_required, get_current_user, audit_log

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users (admin only)"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        role = request.args.get('role')
        search = request.args.get('search')
        
        # Build query
        query = {}
        if role:
            query['role'] = role
        if search:
            query['$or'] = [
                {'username': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}},
                {'firstName': {'$regex': search, '$options': 'i'}},
                {'lastName': {'$regex': search, '$options': 'i'}}
            ]
        
        # Get paginated results
        users, pagination = paginate_query(
            mongo_db.db.users, 
            query, 
            page, 
            limit, 
            'createdAt', 
            -1
        )
        
        # Remove sensitive data
        for user in users:
            if 'password' in user:
                del user['password']
            if 'emailVerificationToken' in user:
                del user['emailVerificationToken']
            if 'passwordResetToken' in user:
                del user['passwordResetToken']
        
        return jsonify(create_response(
            success=True,
            data=users,
            pagination=pagination,
            message="Users retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_USERS_ERROR", "message": str(e)}
        )), 500

@users_bp.route('/profile', methods=['GET'])
@user_required
def get_profile():
    """Get current user profile"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify(create_response(
                success=False,
                error={"code": "USER_NOT_FOUND", "message": "User not found"}
            )), 404
        
        # Remove sensitive data
        user_data = serialize_doc(current_user)
        if 'password' in user_data:
            del user_data['password']
        if 'emailVerificationToken' in user_data:
            del user_data['emailVerificationToken']
        if 'passwordResetToken' in user_data:
            del user_data['passwordResetToken']
        
        return jsonify(create_response(
            success=True,
            data=user_data,
            message="Profile retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_PROFILE_ERROR", "message": str(e)}
        )), 500

@users_bp.route('/profile', methods=['PUT'])
@user_required
@audit_log('update_profile', 'user')
def update_profile():
    """Update current user profile"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Fields that can be updated by user
        allowed_fields = ['firstName', 'lastName', 'avatar', 'preferences']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify(create_response(
                success=False,
                error={"code": "NO_UPDATE_DATA", "message": "No valid fields to update"}
            )), 400
        
        update_data['updatedAt'] = datetime.utcnow()
        
        # Update user
        result = mongo_db.db.users.update_one(
            {"_id": ObjectId(current_user_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return jsonify(create_response(
                success=False,
                error={"code": "USER_NOT_FOUND", "message": "User not found"}
            )), 404
        
        # Get updated user
        updated_user = mongo_db.db.users.find_one({"_id": ObjectId(current_user_id)})
        user_data = serialize_doc(updated_user)
        
        # Remove sensitive data
        if 'password' in user_data:
            del user_data['password']
        if 'emailVerificationToken' in user_data:
            del user_data['emailVerificationToken']
        if 'passwordResetToken' in user_data:
            del user_data['passwordResetToken']
        
        return jsonify(create_response(
            success=True,
            data=user_data,
            message="Profile updated successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "UPDATE_PROFILE_ERROR", "message": str(e)}
        )), 500

@users_bp.route('/<id>', methods=['GET'])
@admin_required
def get_user_by_id(id):
    """Get user by ID (admin only)"""
    try:
        user = mongo_db.db.users.find_one({"_id": ObjectId(id)})
        
        if not user:
            return jsonify(create_response(
                success=False,
                error={"code": "USER_NOT_FOUND", "message": "User not found"}
            )), 404
        
        # Remove sensitive data
        user_data = serialize_doc(user)
        if 'password' in user_data:
            del user_data['password']
        if 'emailVerificationToken' in user_data:
            del user_data['emailVerificationToken']
        if 'passwordResetToken' in user_data:
            del user_data['passwordResetToken']
        
        return jsonify(create_response(
            success=True,
            data=user_data,
            message="User retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_USER_ERROR", "message": str(e)}
        )), 500

@users_bp.route('/<id>', methods=['PUT'])
@admin_required
@audit_log('update_user', 'user')
def update_user(id):
    """Update user (admin only)"""
    try:
        data = request.get_json()
        
        # Fields that can be updated by admin
        allowed_fields = ['firstName', 'lastName', 'avatar', 'preferences', 'isActive']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        # Handle password update separately
        if 'password' in data and data['password']:
            update_data['password'] = generate_password_hash(data['password'])
        
        if not update_data:
            return jsonify(create_response(
                success=False,
                error={"code": "NO_UPDATE_DATA", "message": "No valid fields to update"}
            )), 400
        
        update_data['updatedAt'] = datetime.utcnow()
        
        # Update user
        result = mongo_db.db.users.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return jsonify(create_response(
                success=False,
                error={"code": "USER_NOT_FOUND", "message": "User not found"}
            )), 404
        
        # Get updated user
        updated_user = mongo_db.db.users.find_one({"_id": ObjectId(id)})
        user_data = serialize_doc(updated_user)
        
        # Remove sensitive data
        if 'password' in user_data:
            del user_data['password']
        if 'emailVerificationToken' in user_data:
            del user_data['emailVerificationToken']
        if 'passwordResetToken' in user_data:
            del user_data['passwordResetToken']
        
        return jsonify(create_response(
            success=True,
            data=user_data,
            message="User updated successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "UPDATE_USER_ERROR", "message": str(e)}
        )), 500

@users_bp.route('/<id>', methods=['DELETE'])
@admin_required
@audit_log('delete_user', 'user')
def delete_user(id):
    """Delete user (admin only)"""
    try:
        # Check if user exists
        user = mongo_db.db.users.find_one({"_id": ObjectId(id)})
        if not user:
            return jsonify(create_response(
                success=False,
                error={"code": "USER_NOT_FOUND", "message": "User not found"}
            )), 404
        
        # Prevent deleting admin users (optional safety check)
        if user.get('role') == 'admin':
            return jsonify(create_response(
                success=False,
                error={"code": "CANNOT_DELETE_ADMIN", "message": "Cannot delete admin users"}
            )), 403
        
        # Delete user
        mongo_db.db.users.delete_one({"_id": ObjectId(id)})
        
        return jsonify(create_response(
            success=True,
            message="User deleted successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "DELETE_USER_ERROR", "message": str(e)}
        )), 500

@users_bp.route('/<id>/role', methods=['PUT'])
@admin_required
@audit_log('update_user_role', 'user')
def update_user_role(id):
    """Update user role (admin only)"""
    try:
        data = request.get_json()
        
        if 'role' not in data:
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_ROLE", "message": "Role is required"}
            )), 400
        
        role = data['role']
        valid_roles = ['admin', 'moderator', 'user']
        
        if role not in valid_roles:
            return jsonify(create_response(
                success=False,
                error={"code": "INVALID_ROLE", "message": f"Role must be one of: {', '.join(valid_roles)}"}
            )), 400
        
        # Update user role
        result = mongo_db.db.users.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "role": role,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            return jsonify(create_response(
                success=False,
                error={"code": "USER_NOT_FOUND", "message": "User not found"}
            )), 404
        
        return jsonify(create_response(
            success=True,
            message=f"User role updated to {role}"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "UPDATE_ROLE_ERROR", "message": str(e)}
        )), 500

@users_bp.route('/<id>/status', methods=['PUT'])
@admin_required
@audit_log('update_user_status', 'user')
def update_user_status(id):
    """Activate/deactivate user (admin only)"""
    try:
        data = request.get_json()
        
        if 'isActive' not in data:
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_STATUS", "message": "isActive status is required"}
            )), 400
        
        is_active = bool(data['isActive'])
        
        # Update user status
        result = mongo_db.db.users.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "isActive": is_active,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            return jsonify(create_response(
                success=False,
                error={"code": "USER_NOT_FOUND", "message": "User not found"}
            )), 404
        
        status_text = "activated" if is_active else "deactivated"
        return jsonify(create_response(
            success=True,
            message=f"User {status_text} successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "UPDATE_STATUS_ERROR", "message": str(e)}
        )), 500

