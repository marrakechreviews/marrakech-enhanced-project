from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import ObjectId
from datetime import datetime

from src.models.database import mongo_db, create_response, serialize_doc, serialize_docs
from src.utils.decorators import admin_required, audit_log

settings_bp = Blueprint('settings', __name__)

# Default settings
DEFAULT_SETTINGS = [
    {
        "key": "site_title",
        "value": "Marrakech Reviews",
        "description": "Website title",
        "category": "general",
        "isPublic": True
    },
    {
        "key": "site_description",
        "value": "Discover the best of Marrakech through authentic reviews and experiences",
        "description": "Website description for SEO",
        "category": "general",
        "isPublic": True
    },
    {
        "key": "contact_email",
        "value": "contact@marrakechreviews.com",
        "description": "Contact email address",
        "category": "general",
        "isPublic": True
    },
    {
        "key": "reviews_require_approval",
        "value": True,
        "description": "Whether reviews require admin approval before being published",
        "category": "moderation",
        "isPublic": False
    },
    {
        "key": "articles_auto_publish",
        "value": False,
        "description": "Whether articles are automatically published or require approval",
        "category": "moderation",
        "isPublic": False
    },
    {
        "key": "wallet_welcome_bonus",
        "value": 100,
        "description": "Welcome bonus coins for new users",
        "category": "wallet",
        "isPublic": False
    },
    {
        "key": "wallet_review_reward",
        "value": 10,
        "description": "Coins rewarded for approved reviews",
        "category": "wallet",
        "isPublic": False
    },
    {
        "key": "wallet_article_reward",
        "value": 25,
        "description": "Coins rewarded for published articles",
        "category": "wallet",
        "isPublic": False
    },
    {
        "key": "seo_keywords",
        "value": ["marrakech", "morocco", "travel", "reviews", "tourism"],
        "description": "Default SEO keywords",
        "category": "seo",
        "isPublic": True
    },
    {
        "key": "social_facebook",
        "value": "",
        "description": "Facebook page URL",
        "category": "social",
        "isPublic": True
    },
    {
        "key": "social_instagram",
        "value": "",
        "description": "Instagram profile URL",
        "category": "social",
        "isPublic": True
    },
    {
        "key": "social_twitter",
        "value": "",
        "description": "Twitter profile URL",
        "category": "social",
        "isPublic": True
    }
]

def initialize_default_settings():
    """Initialize default settings if they don't exist"""
    try:
        for setting in DEFAULT_SETTINGS:
            existing = mongo_db.db.settings.find_one({"key": setting["key"]})
            if not existing:
                setting_doc = setting.copy()
                setting_doc["createdAt"] = datetime.utcnow()
                setting_doc["updatedAt"] = datetime.utcnow()
                mongo_db.db.settings.insert_one(setting_doc)
    except Exception as e:
        print(f"Error initializing settings: {e}")

@settings_bp.route('', methods=['GET'])
def get_public_settings():
    """Get public settings"""
    try:
        # Initialize default settings if needed
        initialize_default_settings()
        
        # Get public settings only
        settings = list(mongo_db.db.settings.find(
            {"isPublic": True},
            {"_id": 0, "key": 1, "value": 1, "description": 1, "category": 1}
        ))
        
        # Convert to key-value format
        settings_dict = {}
        for setting in settings:
            settings_dict[setting["key"]] = setting["value"]
        
        return jsonify(create_response(
            success=True,
            data=settings_dict,
            message="Public settings retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_SETTINGS_ERROR", "message": str(e)}
        )), 500

@settings_bp.route('/admin', methods=['GET'])
@admin_required
def get_all_settings():
    """Get all settings (admin only)"""
    try:
        # Initialize default settings if needed
        initialize_default_settings()
        
        category = request.args.get('category')
        
        # Build query
        query = {}
        if category:
            query['category'] = category
        
        # Get all settings
        settings = list(mongo_db.db.settings.find(query).sort("category", 1).sort("key", 1))
        
        # Group by category
        settings_by_category = {}
        for setting in settings:
            cat = setting.get('category', 'general')
            if cat not in settings_by_category:
                settings_by_category[cat] = []
            
            setting_data = serialize_doc(setting)
            settings_by_category[cat].append(setting_data)
        
        return jsonify(create_response(
            success=True,
            data=settings_by_category,
            message="All settings retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_ALL_SETTINGS_ERROR", "message": str(e)}
        )), 500

@settings_bp.route('/<key>', methods=['PUT'])
@admin_required
@audit_log('update_setting', 'setting')
def update_setting(key):
    """Update setting (admin only)"""
    try:
        data = request.get_json()
        
        if 'value' not in data:
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_VALUE", "message": "Setting value is required"}
            )), 400
        
        # Find existing setting
        existing = mongo_db.db.settings.find_one({"key": key})
        if not existing:
            return jsonify(create_response(
                success=False,
                error={"code": "SETTING_NOT_FOUND", "message": "Setting not found"}
            )), 404
        
        # Update setting
        update_data = {
            "value": data["value"],
            "updatedAt": datetime.utcnow()
        }
        
        # Update description if provided
        if 'description' in data:
            update_data['description'] = data['description']
        
        # Update isPublic if provided
        if 'isPublic' in data:
            update_data['isPublic'] = bool(data['isPublic'])
        
        mongo_db.db.settings.update_one(
            {"key": key},
            {"$set": update_data}
        )
        
        # Get updated setting
        updated_setting = mongo_db.db.settings.find_one({"key": key})
        
        return jsonify(create_response(
            success=True,
            data=serialize_doc(updated_setting),
            message="Setting updated successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "UPDATE_SETTING_ERROR", "message": str(e)}
        )), 500

@settings_bp.route('', methods=['POST'])
@admin_required
@audit_log('create_setting', 'setting')
def create_setting():
    """Create new setting (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['key', 'value', 'description', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify(create_response(
                    success=False,
                    error={"code": "MISSING_FIELD", "message": f"{field} is required"}
                )), 400
        
        key = data['key']
        
        # Check if setting already exists
        existing = mongo_db.db.settings.find_one({"key": key})
        if existing:
            return jsonify(create_response(
                success=False,
                error={"code": "SETTING_EXISTS", "message": "Setting with this key already exists"}
            )), 409
        
        # Create setting document
        setting_doc = {
            "key": key,
            "value": data['value'],
            "description": data['description'],
            "category": data['category'],
            "isPublic": data.get('isPublic', False),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = mongo_db.db.settings.insert_one(setting_doc)
        setting_doc['_id'] = result.inserted_id
        
        return jsonify(create_response(
            success=True,
            data=serialize_doc(setting_doc),
            message="Setting created successfully"
        )), 201
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "CREATE_SETTING_ERROR", "message": str(e)}
        )), 500

@settings_bp.route('/<key>', methods=['DELETE'])
@admin_required
@audit_log('delete_setting', 'setting')
def delete_setting(key):
    """Delete setting (admin only)"""
    try:
        # Find setting
        setting = mongo_db.db.settings.find_one({"key": key})
        if not setting:
            return jsonify(create_response(
                success=False,
                error={"code": "SETTING_NOT_FOUND", "message": "Setting not found"}
            )), 404
        
        # Prevent deletion of critical settings
        critical_settings = ['site_title', 'site_description', 'contact_email']
        if key in critical_settings:
            return jsonify(create_response(
                success=False,
                error={"code": "CANNOT_DELETE_CRITICAL", "message": "Cannot delete critical system settings"}
            )), 403
        
        # Delete setting
        mongo_db.db.settings.delete_one({"key": key})
        
        return jsonify(create_response(
            success=True,
            message="Setting deleted successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "DELETE_SETTING_ERROR", "message": str(e)}
        )), 500

@settings_bp.route('/categories', methods=['GET'])
@admin_required
def get_setting_categories():
    """Get all setting categories (admin only)"""
    try:
        # Get distinct categories
        categories = mongo_db.db.settings.distinct("category")
        
        # Count settings per category
        category_counts = {}
        for category in categories:
            count = mongo_db.db.settings.count_documents({"category": category})
            category_counts[category] = count
        
        return jsonify(create_response(
            success=True,
            data={
                "categories": categories,
                "counts": category_counts
            },
            message="Setting categories retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_CATEGORIES_ERROR", "message": str(e)}
        )), 500

@settings_bp.route('/export', methods=['GET'])
@admin_required
def export_settings():
    """Export all settings (admin only)"""
    try:
        # Get all settings
        settings = list(mongo_db.db.settings.find({}, {"_id": 0}))
        
        return jsonify(create_response(
            success=True,
            data=settings,
            message="Settings exported successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "EXPORT_SETTINGS_ERROR", "message": str(e)}
        )), 500

@settings_bp.route('/import', methods=['POST'])
@admin_required
@audit_log('import_settings', 'setting')
def import_settings():
    """Import settings (admin only)"""
    try:
        data = request.get_json()
        
        if not data.get('settings'):
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_SETTINGS", "message": "Settings data is required"}
            )), 400
        
        settings = data['settings']
        overwrite = data.get('overwrite', False)
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for setting in settings:
            try:
                if not setting.get('key'):
                    errors.append({"setting": str(setting), "error": "Missing key"})
                    continue
                
                key = setting['key']
                existing = mongo_db.db.settings.find_one({"key": key})
                
                if existing and not overwrite:
                    skipped_count += 1
                    continue
                
                # Prepare setting document
                setting_doc = {
                    "key": key,
                    "value": setting.get('value', ''),
                    "description": setting.get('description', ''),
                    "category": setting.get('category', 'general'),
                    "isPublic": setting.get('isPublic', False),
                    "updatedAt": datetime.utcnow()
                }
                
                if existing:
                    # Update existing
                    mongo_db.db.settings.update_one(
                        {"key": key},
                        {"$set": setting_doc}
                    )
                else:
                    # Create new
                    setting_doc["createdAt"] = datetime.utcnow()
                    mongo_db.db.settings.insert_one(setting_doc)
                
                imported_count += 1
                
            except Exception as e:
                errors.append({"setting": setting.get('key', 'unknown'), "error": str(e)})
        
        return jsonify(create_response(
            success=True,
            data={
                "imported": imported_count,
                "skipped": skipped_count,
                "errors": errors,
                "total": len(settings)
            },
            message=f"Imported {imported_count} settings successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "IMPORT_SETTINGS_ERROR", "message": str(e)}
        )), 500

