from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from bson import ObjectId

from src.models.database import mongo_db, create_response

def role_required(*allowed_roles):
    """Decorator to require specific roles for access"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                claims = get_jwt()
                user_role = claims.get('role', 'user')
                
                # Check if user role is in allowed roles
                if user_role not in allowed_roles:
                    return jsonify(create_response(
                        success=False,
                        error={
                            "code": "INSUFFICIENT_PERMISSIONS",
                            "message": f"Access denied. Required roles: {', '.join(allowed_roles)}"
                        }
                    )), 403
                
                # Verify user still exists and is active
                user = mongo_db.db.users.find_one({
                    "_id": ObjectId(current_user_id),
                    "isActive": True
                })
                
                if not user:
                    return jsonify(create_response(
                        success=False,
                        error={
                            "code": "USER_NOT_FOUND",
                            "message": "User not found or inactive"
                        }
                    )), 404
                
                # Verify role hasn't changed
                if user['role'] != user_role:
                    return jsonify(create_response(
                        success=False,
                        error={
                            "code": "ROLE_CHANGED",
                            "message": "User role has changed. Please login again"
                        }
                    )), 401
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify(create_response(
                    success=False,
                    error={"code": "AUTHORIZATION_ERROR", "message": str(e)}
                )), 500
        
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin role"""
    return role_required('admin')(f)

def moderator_required(f):
    """Decorator to require admin or moderator role"""
    return role_required('admin', 'moderator')(f)

def user_required(f):
    """Decorator to require any authenticated user"""
    return role_required('admin', 'moderator', 'user')(f)

def owner_or_admin_required(resource_field='author'):
    """Decorator to require resource owner or admin access"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                claims = get_jwt()
                user_role = claims.get('role', 'user')
                
                # Admin has access to everything
                if user_role == 'admin':
                    return f(*args, **kwargs)
                
                # Get resource ID from URL parameters
                resource_id = kwargs.get('id') or kwargs.get('resource_id')
                if not resource_id:
                    return jsonify(create_response(
                        success=False,
                        error={"code": "MISSING_RESOURCE_ID", "message": "Resource ID is required"}
                    )), 400
                
                # Determine collection based on endpoint
                collection_name = None
                if 'articles' in str(f):
                    collection_name = 'articles'
                elif 'reviews' in str(f):
                    collection_name = 'reviews'
                elif 'users' in str(f):
                    collection_name = 'users'
                    resource_field = '_id'  # For user resources, check _id instead of author
                
                if not collection_name:
                    return jsonify(create_response(
                        success=False,
                        error={"code": "UNKNOWN_RESOURCE", "message": "Cannot determine resource type"}
                    )), 400
                
                # Find the resource
                collection = getattr(mongo_db.db, collection_name)
                resource = collection.find_one({"_id": ObjectId(resource_id)})
                
                if not resource:
                    return jsonify(create_response(
                        success=False,
                        error={"code": "RESOURCE_NOT_FOUND", "message": "Resource not found"}
                    )), 404
                
                # Check ownership
                resource_owner_id = str(resource.get(resource_field, ''))
                if resource_owner_id != current_user_id:
                    return jsonify(create_response(
                        success=False,
                        error={
                            "code": "ACCESS_DENIED",
                            "message": "You can only access your own resources"
                        }
                    )), 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify(create_response(
                    success=False,
                    error={"code": "OWNERSHIP_CHECK_ERROR", "message": str(e)}
                )), 500
        
        return decorated_function
    return decorator

def get_current_user():
    """Get current user from JWT token"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return None
        
        user = mongo_db.db.users.find_one({
            "_id": ObjectId(current_user_id),
            "isActive": True
        })
        
        return user
    except:
        return None

def log_user_action(action, resource=None, resource_id=None, details=None):
    """Log user action for audit trail"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return
        
        from flask import request
        
        log_entry = {
            "user": ObjectId(current_user_id),
            "action": action,
            "resource": resource,
            "resourceId": ObjectId(resource_id) if resource_id else None,
            "details": details or {},
            "ipAddress": request.remote_addr,
            "userAgent": request.headers.get('User-Agent', ''),
            "timestamp": datetime.utcnow()
        }
        
        mongo_db.db.audit_logs.insert_one(log_entry)
        
    except Exception as e:
        # Don't fail the main operation if logging fails
        print(f"Audit log error: {e}")

def audit_log(action, resource=None):
    """Decorator to automatically log user actions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Execute the function first
                result = f(*args, **kwargs)
                
                # Log the action if successful
                resource_id = kwargs.get('id') or kwargs.get('resource_id')
                log_user_action(action, resource, resource_id)
                
                return result
                
            except Exception as e:
                # Re-raise the exception
                raise e
        
        return decorated_function
    return decorator

