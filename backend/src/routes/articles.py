from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
import re

from src.models.database import mongo_db, create_response, serialize_doc, serialize_docs, paginate_query
from src.utils.decorators import admin_required, moderator_required, user_required, owner_or_admin_required, get_current_user, audit_log

articles_bp = Blueprint('articles', __name__)

def generate_slug(title):
    """Generate URL-friendly slug from title"""
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def ensure_unique_slug(title, article_id=None):
    """Ensure slug is unique by appending number if necessary"""
    base_slug = generate_slug(title)
    slug = base_slug
    counter = 1
    
    while True:
        query = {"slug": slug}
        if article_id:
            query["_id"] = {"$ne": ObjectId(article_id)}
        
        existing = mongo_db.db.articles.find_one(query)
        if not existing:
            return slug
        
        slug = f"{base_slug}-{counter}"
        counter += 1

@articles_bp.route('', methods=['GET'])
def get_articles():
    """Get published articles (public)"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        category = request.args.get('category')
        author = request.args.get('author')
        search = request.args.get('search')
        
        # Build query for published articles only
        query = {"status": "published"}
        
        if category:
            query['category'] = category
        if author:
            query['author'] = ObjectId(author)
        if search:
            query['$text'] = {'$search': search}
        
        # Get paginated results
        articles, pagination = paginate_query(
            mongo_db.db.articles, 
            query, 
            page, 
            limit, 
            'publishedAt', 
            -1
        )
        
        # Populate author information
        for article in articles:
            if article.get('author'):
                author_data = mongo_db.db.users.find_one(
                    {"_id": ObjectId(article['author'])},
                    {"firstName": 1, "lastName": 1, "username": 1, "avatar": 1}
                )
                if author_data:
                    article['authorInfo'] = serialize_doc(author_data)
        
        return jsonify(create_response(
            success=True,
            data=articles,
            pagination=pagination,
            message="Articles retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_ARTICLES_ERROR", "message": str(e)}
        )), 500

@articles_bp.route('/search', methods=['GET'])
def search_articles():
    """Search articles"""
    try:
        query_text = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        if not query_text:
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_QUERY", "message": "Search query is required"}
            )), 400
        
        # Build search query
        query = {
            "status": "published",
            "$text": {"$search": query_text}
        }
        
        # Get paginated results with text score
        articles, pagination = paginate_query(
            mongo_db.db.articles, 
            query, 
            page, 
            limit, 
            'score', 
            -1
        )
        
        return jsonify(create_response(
            success=True,
            data=articles,
            pagination=pagination,
            message="Search completed successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "SEARCH_ERROR", "message": str(e)}
        )), 500

@articles_bp.route('/category/<slug>', methods=['GET'])
def get_articles_by_category(slug):
    """Get articles by category"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Find category
        category = mongo_db.db.categories.find_one({"slug": slug})
        if not category:
            return jsonify(create_response(
                success=False,
                error={"code": "CATEGORY_NOT_FOUND", "message": "Category not found"}
            )), 404
        
        # Get articles in this category
        query = {
            "status": "published",
            "category": category['name']
        }
        
        articles, pagination = paginate_query(
            mongo_db.db.articles, 
            query, 
            page, 
            limit, 
            'publishedAt', 
            -1
        )
        
        return jsonify(create_response(
            success=True,
            data={
                "category": serialize_doc(category),
                "articles": articles
            },
            pagination=pagination,
            message="Articles retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_CATEGORY_ARTICLES_ERROR", "message": str(e)}
        )), 500

@articles_bp.route('/<slug>', methods=['GET'])
def get_article_by_slug(slug):
    """Get article by slug (public)"""
    try:
        article = mongo_db.db.articles.find_one({"slug": slug, "status": "published"})
        
        if not article:
            return jsonify(create_response(
                success=False,
                error={"code": "ARTICLE_NOT_FOUND", "message": "Article not found"}
            )), 404
        
        # Increment view count
        mongo_db.db.articles.update_one(
            {"_id": article['_id']},
            {"$inc": {"views": 1}}
        )
        
        # Populate author information
        if article.get('author'):
            author_data = mongo_db.db.users.find_one(
                {"_id": ObjectId(article['author'])},
                {"firstName": 1, "lastName": 1, "username": 1, "avatar": 1}
            )
            if author_data:
                article['authorInfo'] = serialize_doc(author_data)
        
        article_data = serialize_doc(article)
        article_data['views'] = article_data.get('views', 0) + 1
        
        return jsonify(create_response(
            success=True,
            data=article_data,
            message="Article retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_ARTICLE_ERROR", "message": str(e)}
        )), 500

@articles_bp.route('', methods=['POST'])
@user_required
@audit_log('create_article', 'article')
def create_article():
    """Create article (authenticated users)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify(create_response(
                    success=False,
                    error={"code": "MISSING_FIELD", "message": f"{field} is required"}
                )), 400
        
        title = data['title'].strip()
        content = data['content']
        
        # Generate unique slug
        slug = ensure_unique_slug(title)
        
        # Create article document
        article_doc = {
            "title": title,
            "slug": slug,
            "content": content,
            "excerpt": data.get('excerpt', ''),
            "featuredImage": data.get('featuredImage', ''),
            "gallery": data.get('gallery', []),
            "author": ObjectId(current_user_id),
            "category": data.get('category', ''),
            "tags": data.get('tags', []),
            "seo": {
                "metaTitle": data.get('seo', {}).get('metaTitle', title),
                "metaDescription": data.get('seo', {}).get('metaDescription', ''),
                "keywords": data.get('seo', {}).get('keywords', []),
                "canonicalUrl": data.get('seo', {}).get('canonicalUrl', '')
            },
            "status": "draft",  # Default to draft
            "publishedAt": None,
            "views": 0,
            "likes": 0,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = mongo_db.db.articles.insert_one(article_doc)
        article_doc['_id'] = result.inserted_id
        
        return jsonify(create_response(
            success=True,
            data=serialize_doc(article_doc),
            message="Article created successfully"
        )), 201
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "CREATE_ARTICLE_ERROR", "message": str(e)}
        )), 500

@articles_bp.route('/<id>', methods=['PUT'])
@jwt_required()
@audit_log('update_article', 'article')
def update_article(id):
    """Update article (author/admin/moderator)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = get_current_user()
        data = request.get_json()
        
        # Find article
        article = mongo_db.db.articles.find_one({"_id": ObjectId(id)})
        if not article:
            return jsonify(create_response(
                success=False,
                error={"code": "ARTICLE_NOT_FOUND", "message": "Article not found"}
            )), 404
        
        # Check permissions
        is_author = str(article['author']) == current_user_id
        is_admin_or_moderator = current_user['role'] in ['admin', 'moderator']
        
        if not (is_author or is_admin_or_moderator):
            return jsonify(create_response(
                success=False,
                error={"code": "ACCESS_DENIED", "message": "You can only edit your own articles"}
            )), 403
        
        # Build update data
        update_data = {}
        updatable_fields = ['title', 'content', 'excerpt', 'featuredImage', 'gallery', 'category', 'tags', 'seo']
        
        for field in updatable_fields:
            if field in data:
                update_data[field] = data[field]
        
        # Update slug if title changed
        if 'title' in data and data['title'] != article['title']:
            update_data['slug'] = ensure_unique_slug(data['title'], id)
        
        if not update_data:
            return jsonify(create_response(
                success=False,
                error={"code": "NO_UPDATE_DATA", "message": "No valid fields to update"}
            )), 400
        
        update_data['updatedAt'] = datetime.utcnow()
        
        # Update article
        mongo_db.db.articles.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )
        
        # Get updated article
        updated_article = mongo_db.db.articles.find_one({"_id": ObjectId(id)})
        
        return jsonify(create_response(
            success=True,
            data=serialize_doc(updated_article),
            message="Article updated successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "UPDATE_ARTICLE_ERROR", "message": str(e)}
        )), 500

@articles_bp.route('/<id>', methods=['DELETE'])
@jwt_required()
@audit_log('delete_article', 'article')
def delete_article(id):
    """Delete article (author/admin)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = get_current_user()
        
        # Find article
        article = mongo_db.db.articles.find_one({"_id": ObjectId(id)})
        if not article:
            return jsonify(create_response(
                success=False,
                error={"code": "ARTICLE_NOT_FOUND", "message": "Article not found"}
            )), 404
        
        # Check permissions (only author or admin can delete)
        is_author = str(article['author']) == current_user_id
        is_admin = current_user['role'] == 'admin'
        
        if not (is_author or is_admin):
            return jsonify(create_response(
                success=False,
                error={"code": "ACCESS_DENIED", "message": "You can only delete your own articles"}
            )), 403
        
        # Delete article
        mongo_db.db.articles.delete_one({"_id": ObjectId(id)})
        
        return jsonify(create_response(
            success=True,
            message="Article deleted successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "DELETE_ARTICLE_ERROR", "message": str(e)}
        )), 500

@articles_bp.route('/<id>/publish', methods=['PUT'])
@moderator_required
@audit_log('publish_article', 'article')
def publish_article(id):
    """Publish article (admin/moderator)"""
    try:
        # Find article
        article = mongo_db.db.articles.find_one({"_id": ObjectId(id)})
        if not article:
            return jsonify(create_response(
                success=False,
                error={"code": "ARTICLE_NOT_FOUND", "message": "Article not found"}
            )), 404
        
        # Update article status
        mongo_db.db.articles.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "status": "published",
                    "publishedAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        return jsonify(create_response(
            success=True,
            message="Article published successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "PUBLISH_ARTICLE_ERROR", "message": str(e)}
        )), 500

@articles_bp.route('/<id>/archive', methods=['PUT'])
@moderator_required
@audit_log('archive_article', 'article')
def archive_article(id):
    """Archive article (admin/moderator)"""
    try:
        # Find article
        article = mongo_db.db.articles.find_one({"_id": ObjectId(id)})
        if not article:
            return jsonify(create_response(
                success=False,
                error={"code": "ARTICLE_NOT_FOUND", "message": "Article not found"}
            )), 404
        
        # Update article status
        mongo_db.db.articles.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "status": "archived",
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        return jsonify(create_response(
            success=True,
            message="Article archived successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "ARCHIVE_ARTICLE_ERROR", "message": str(e)}
        )), 500

@articles_bp.route('/<id>/like', methods=['POST'])
@user_required
def like_article(id):
    """Like article (authenticated users)"""
    try:
        # Find article
        article = mongo_db.db.articles.find_one({"_id": ObjectId(id), "status": "published"})
        if not article:
            return jsonify(create_response(
                success=False,
                error={"code": "ARTICLE_NOT_FOUND", "message": "Article not found"}
            )), 404
        
        # Increment likes
        mongo_db.db.articles.update_one(
            {"_id": ObjectId(id)},
            {"$inc": {"likes": 1}}
        )
        
        return jsonify(create_response(
            success=True,
            message="Article liked successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "LIKE_ARTICLE_ERROR", "message": str(e)}
        )), 500

@articles_bp.route('/my', methods=['GET'])
@user_required
def get_my_articles():
    """Get current user's articles"""
    try:
        current_user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        status = request.args.get('status')
        
        # Build query
        query = {"author": ObjectId(current_user_id)}
        if status:
            query['status'] = status
        
        # Get paginated results
        articles, pagination = paginate_query(
            mongo_db.db.articles, 
            query, 
            page, 
            limit, 
            'createdAt', 
            -1
        )
        
        return jsonify(create_response(
            success=True,
            data=articles,
            pagination=pagination,
            message="Articles retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_MY_ARTICLES_ERROR", "message": str(e)}
        )), 500

