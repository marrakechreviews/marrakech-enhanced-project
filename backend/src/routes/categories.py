from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import ObjectId
from datetime import datetime
import re

from src.models.database import mongo_db, create_response, serialize_doc, serialize_docs
from src.utils.decorators import admin_required, audit_log

categories_bp = Blueprint('categories', __name__)

def generate_slug(name):
    """Generate URL-friendly slug from category name"""
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def ensure_unique_slug(name, category_id=None):
    """Ensure slug is unique by appending number if necessary"""
    base_slug = generate_slug(name)
    slug = base_slug
    counter = 1
    
    while True:
        query = {"slug": slug}
        if category_id:
            query["_id"] = {"$ne": ObjectId(category_id)}
        
        existing = mongo_db.db.categories.find_one(query)
        if not existing:
            return slug
        
        slug = f"{base_slug}-{counter}"
        counter += 1

@categories_bp.route('', methods=['GET'])
def get_categories():
    """Get all categories (public)"""
    try:
        # Get all active categories
        categories = list(mongo_db.db.categories.find(
            {"isActive": True},
            sort=[("name", 1)]
        ))
        
        # Build hierarchical structure
        category_map = {}
        root_categories = []
        
        for category in categories:
            category_data = serialize_doc(category)
            category_data['children'] = []
            category_map[str(category['_id'])] = category_data
            
            if not category.get('parentCategory'):
                root_categories.append(category_data)
        
        # Add children to their parents
        for category in categories:
            if category.get('parentCategory'):
                parent_id = str(category['parentCategory'])
                if parent_id in category_map:
                    category_map[parent_id]['children'].append(category_map[str(category['_id'])])
        
        return jsonify(create_response(
            success=True,
            data=root_categories,
            message="Categories retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_CATEGORIES_ERROR", "message": str(e)}
        )), 500

@categories_bp.route('/<slug>', methods=['GET'])
def get_category_by_slug(slug):
    """Get category by slug"""
    try:
        category = mongo_db.db.categories.find_one({"slug": slug, "isActive": True})
        
        if not category:
            return jsonify(create_response(
                success=False,
                error={"code": "CATEGORY_NOT_FOUND", "message": "Category not found"}
            )), 404
        
        # Get subcategories
        subcategories = list(mongo_db.db.categories.find(
            {"parentCategory": category['_id'], "isActive": True},
            sort=[("name", 1)]
        ))
        
        category_data = serialize_doc(category)
        category_data['subcategories'] = serialize_docs(subcategories)
        
        # Get article count for this category
        article_count = mongo_db.db.articles.count_documents({
            "category": category['name'],
            "status": "published"
        })
        category_data['articleCount'] = article_count
        
        return jsonify(create_response(
            success=True,
            data=category_data,
            message="Category retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_CATEGORY_ERROR", "message": str(e)}
        )), 500

@categories_bp.route('', methods=['POST'])
@admin_required
@audit_log('create_category', 'category')
def create_category():
    """Create category (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_NAME", "message": "Category name is required"}
            )), 400
        
        name = data['name'].strip()
        description = data.get('description', '').strip()
        parent_category_id = data.get('parentCategory')
        
        # Check if category name already exists
        existing = mongo_db.db.categories.find_one({"name": name})
        if existing:
            return jsonify(create_response(
                success=False,
                error={"code": "CATEGORY_EXISTS", "message": "Category with this name already exists"}
            )), 409
        
        # Validate parent category if provided
        parent_category = None
        if parent_category_id:
            parent_category = mongo_db.db.categories.find_one({"_id": ObjectId(parent_category_id)})
            if not parent_category:
                return jsonify(create_response(
                    success=False,
                    error={"code": "PARENT_NOT_FOUND", "message": "Parent category not found"}
                )), 404
        
        # Generate unique slug
        slug = ensure_unique_slug(name)
        
        # Create category document
        category_doc = {
            "name": name,
            "slug": slug,
            "description": description,
            "parentCategory": ObjectId(parent_category_id) if parent_category_id else None,
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = mongo_db.db.categories.insert_one(category_doc)
        category_doc['_id'] = result.inserted_id
        
        return jsonify(create_response(
            success=True,
            data=serialize_doc(category_doc),
            message="Category created successfully"
        )), 201
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "CREATE_CATEGORY_ERROR", "message": str(e)}
        )), 500

@categories_bp.route('/<id>', methods=['PUT'])
@admin_required
@audit_log('update_category', 'category')
def update_category(id):
    """Update category (admin only)"""
    try:
        data = request.get_json()
        
        # Find category
        category = mongo_db.db.categories.find_one({"_id": ObjectId(id)})
        if not category:
            return jsonify(create_response(
                success=False,
                error={"code": "CATEGORY_NOT_FOUND", "message": "Category not found"}
            )), 404
        
        # Build update data
        update_data = {}
        
        if 'name' in data:
            name = data['name'].strip()
            if name != category['name']:
                # Check if new name already exists
                existing = mongo_db.db.categories.find_one({
                    "name": name,
                    "_id": {"$ne": ObjectId(id)}
                })
                if existing:
                    return jsonify(create_response(
                        success=False,
                        error={"code": "CATEGORY_EXISTS", "message": "Category with this name already exists"}
                    )), 409
                
                update_data['name'] = name
                update_data['slug'] = ensure_unique_slug(name, id)
        
        if 'description' in data:
            update_data['description'] = data['description'].strip()
        
        if 'parentCategory' in data:
            parent_category_id = data['parentCategory']
            if parent_category_id:
                # Validate parent category
                parent_category = mongo_db.db.categories.find_one({"_id": ObjectId(parent_category_id)})
                if not parent_category:
                    return jsonify(create_response(
                        success=False,
                        error={"code": "PARENT_NOT_FOUND", "message": "Parent category not found"}
                    )), 404
                
                # Prevent circular reference
                if parent_category_id == id:
                    return jsonify(create_response(
                        success=False,
                        error={"code": "CIRCULAR_REFERENCE", "message": "Category cannot be its own parent"}
                    )), 400
                
                update_data['parentCategory'] = ObjectId(parent_category_id)
            else:
                update_data['parentCategory'] = None
        
        if 'isActive' in data:
            update_data['isActive'] = bool(data['isActive'])
        
        if not update_data:
            return jsonify(create_response(
                success=False,
                error={"code": "NO_UPDATE_DATA", "message": "No valid fields to update"}
            )), 400
        
        update_data['updatedAt'] = datetime.utcnow()
        
        # Update category
        mongo_db.db.categories.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )
        
        # Get updated category
        updated_category = mongo_db.db.categories.find_one({"_id": ObjectId(id)})
        
        return jsonify(create_response(
            success=True,
            data=serialize_doc(updated_category),
            message="Category updated successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "UPDATE_CATEGORY_ERROR", "message": str(e)}
        )), 500

@categories_bp.route('/<id>', methods=['DELETE'])
@admin_required
@audit_log('delete_category', 'category')
def delete_category(id):
    """Delete category (admin only)"""
    try:
        # Find category
        category = mongo_db.db.categories.find_one({"_id": ObjectId(id)})
        if not category:
            return jsonify(create_response(
                success=False,
                error={"code": "CATEGORY_NOT_FOUND", "message": "Category not found"}
            )), 404
        
        # Check if category has subcategories
        subcategories = mongo_db.db.categories.find_one({"parentCategory": ObjectId(id)})
        if subcategories:
            return jsonify(create_response(
                success=False,
                error={"code": "HAS_SUBCATEGORIES", "message": "Cannot delete category with subcategories"}
            )), 400
        
        # Check if category is used by articles
        articles_count = mongo_db.db.articles.count_documents({"category": category['name']})
        if articles_count > 0:
            return jsonify(create_response(
                success=False,
                error={"code": "CATEGORY_IN_USE", "message": f"Cannot delete category. {articles_count} articles are using this category"}
            )), 400
        
        # Delete category
        mongo_db.db.categories.delete_one({"_id": ObjectId(id)})
        
        return jsonify(create_response(
            success=True,
            message="Category deleted successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "DELETE_CATEGORY_ERROR", "message": str(e)}
        )), 500

@categories_bp.route('/admin', methods=['GET'])
@admin_required
def get_all_categories_admin():
    """Get all categories including inactive ones (admin only)"""
    try:
        # Get all categories
        categories = list(mongo_db.db.categories.find({}, sort=[("name", 1)]))
        
        # Add article counts
        for category in categories:
            article_count = mongo_db.db.articles.count_documents({
                "category": category['name']
            })
            category['articleCount'] = article_count
        
        return jsonify(create_response(
            success=True,
            data=serialize_docs(categories),
            message="All categories retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_ALL_CATEGORIES_ERROR", "message": str(e)}
        )), 500

