from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime, timedelta
import jwt
from functools import wraps
from src.models.database import mongo_db
import os

reviews_bp = Blueprint('reviews', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, os.getenv('JWT_SECRET_KEY', 'your-secret-key'), algorithms=['HS256'])
            current_user = mongo_db.db.users.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.get('role') != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@reviews_bp.route('', methods=['GET'])
def get_reviews():
    """Get all reviews with pagination and filtering"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        category = request.args.get('category')
        location = request.args.get('location')
        rating = request.args.get('rating')
        search = request.args.get('search')
        
        filters = {"status": "approved"}  # Only show approved reviews
        if category:
            filters['category'] = category
        if location:
            filters['location.name'] = {'$regex': location, '$options': 'i'}
        if rating:
            filters['rating'] = {'$gte': int(rating)}
        if search:
            filters['$or'] = [
                {'title': {'$regex': search, '$options': 'i'}},
                {'content': {'$regex': search, '$options': 'i'}},
                {'location.name': {'$regex': search, '$options': 'i'}}
            ]
        
        skip = (page - 1) * limit
        reviews = list(mongo_db.db.reviews.find(filters)
                      .sort('createdAt', -1)
                      .skip(skip)
                      .limit(limit))
        
        total_count = mongo_db.db.reviews.count_documents(filters)
        
        # Convert ObjectId to string for JSON serialization
        for review in reviews:
            review['_id'] = str(review['_id'])
            if 'author' in review:
                review['author'] = str(review['author'])
        
        return jsonify({
            'success': True,
            'data': reviews,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'totalPages': (total_count + limit - 1) // limit,
                'hasNext': page * limit < total_count,
                'hasPrev': page > 1
            },
            'message': 'Reviews retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@reviews_bp.route('/reviews/<review_id>', methods=['GET'])
def get_review(review_id):
    """Get a specific review by ID"""
    try:
        review = Review.find_by_id(review_id)
        if not review:
            return jsonify({'success': False, 'message': 'Review not found'}), 404
        
        # Increment view count
        Review.increment_views(review_id)
        
        return jsonify({'success': True, 'review': review}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@reviews_bp.route('/reviews', methods=['POST'])
@token_required
def create_review(current_user):
    """Create a new review"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'content', 'rating', 'location', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        # Validate rating
        if not isinstance(data['rating'], int) or data['rating'] < 1 or data['rating'] > 5:
            return jsonify({'success': False, 'message': 'Rating must be between 1 and 5'}), 400
        
        review_data = {
            'title': data['title'],
            'content': data['content'],
            'rating': data['rating'],
            'location': data['location'],
            'category': data['category'],
            'author_id': str(current_user['_id']),
            'author_name': f"{current_user.get('firstName', '')} {current_user.get('lastName', '')}".strip(),
            'images': data.get('images', []),
            'tags': data.get('tags', []),
            'visit_date': data.get('visit_date'),
            'pros': data.get('pros', []),
            'cons': data.get('cons', []),
            'tips': data.get('tips', ''),
            'price_range': data.get('price_range'),
            'status': 'published',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'views': 0,
            'likes': 0,
            'helpful_votes': 0
        }
        
        review_id = Review.create(review_data)
        
        # Update user stats
        User.increment_reviews_count(str(current_user['_id']))
        
        return jsonify({
            'success': True,
            'message': 'Review created successfully',
            'review_id': str(review_id)
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@reviews_bp.route('/reviews/<review_id>', methods=['PUT'])
@token_required
def update_review(current_user, review_id):
    """Update a review"""
    try:
        review = Review.find_by_id(review_id)
        if not review:
            return jsonify({'success': False, 'message': 'Review not found'}), 404
        
        # Check if user owns the review or is admin
        if str(review['author_id']) != str(current_user['_id']) and current_user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Update allowed fields
        update_data = {}
        allowed_fields = ['title', 'content', 'rating', 'location', 'category', 'images', 'tags', 'visit_date', 'pros', 'cons', 'tips', 'price_range']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            Review.update_by_id(review_id, update_data)
        
        return jsonify({'success': True, 'message': 'Review updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@reviews_bp.route('/reviews/<review_id>', methods=['DELETE'])
@token_required
def delete_review(current_user, review_id):
    """Delete a review"""
    try:
        review = Review.find_by_id(review_id)
        if not review:
            return jsonify({'success': False, 'message': 'Review not found'}), 404
        
        # Check if user owns the review or is admin
        if str(review['author_id']) != str(current_user['_id']) and current_user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        Review.delete_by_id(review_id)
        
        # Update user stats
        User.decrement_reviews_count(str(current_user['_id']))
        
        return jsonify({'success': True, 'message': 'Review deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@reviews_bp.route('/reviews/<review_id>/like', methods=['POST'])
@token_required
def like_review(current_user, review_id):
    """Like/unlike a review"""
    try:
        review = Review.find_by_id(review_id)
        if not review:
            return jsonify({'success': False, 'message': 'Review not found'}), 404
        
        user_id = str(current_user['_id'])
        liked_reviews = current_user.get('liked_reviews', [])
        
        if review_id in liked_reviews:
            # Unlike
            User.remove_liked_review(user_id, review_id)
            Review.decrement_likes(review_id)
            message = 'Review unliked'
        else:
            # Like
            User.add_liked_review(user_id, review_id)
            Review.increment_likes(review_id)
            message = 'Review liked'
        
        return jsonify({'success': True, 'message': message}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@reviews_bp.route('/reviews/<review_id>/helpful', methods=['POST'])
@token_required
def mark_helpful(current_user, review_id):
    """Mark a review as helpful"""
    try:
        review = Review.find_by_id(review_id)
        if not review:
            return jsonify({'success': False, 'message': 'Review not found'}), 404
        
        Review.increment_helpful_votes(review_id)
        
        return jsonify({'success': True, 'message': 'Review marked as helpful'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@reviews_bp.route('/user/reviews', methods=['GET'])
@token_required
def get_user_reviews(current_user):
    """Get reviews by current user"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        filters = {'author_id': str(current_user['_id'])}
        reviews = Review.find_paginated(filters, page, limit)
        total_count = Review.count_documents(filters)
        
        return jsonify({
            'success': True,
            'reviews': reviews,
            'pagination': {
                'current_page': page,
                'total_pages': (total_count + limit - 1) // limit,
                'total_count': total_count,
                'has_next': page * limit < total_count,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@reviews_bp.route('/user/coupons/claim', methods=['POST'])
@token_required
def claim_weekly_coupon(current_user):
    """Claim weekly coupon for user"""
    try:
        user_id = str(current_user['_id'])
        
        # Check if user already claimed this week
        week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        existing_coupon = Coupon.find_user_coupon_this_week(user_id, week_start)
        if existing_coupon:
            return jsonify({
                'success': False, 
                'message': 'You have already claimed your coupon this week'
            }), 400
        
        # Generate new coupon
        coupon_code = f"WEEK{datetime.utcnow().strftime('%Y%W')}{user_id[-4:].upper()}"
        
        coupon_data = {
            'code': coupon_code,
            'user_id': user_id,
            'discount_percentage': 10,  # 10% discount
            'valid_from': datetime.utcnow(),
            'valid_until': week_start + timedelta(days=7),
            'is_used': False,
            'created_at': datetime.utcnow()
        }
        
        coupon_id = Coupon.create(coupon_data)
        
        # Update user's coupon count
        User.increment_coupons_count(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Weekly coupon claimed successfully',
            'coupon': {
                'code': coupon_code,
                'discount': '10%',
                'valid_until': coupon_data['valid_until'].isoformat()
            }
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@reviews_bp.route('/user/coupons', methods=['GET'])
@token_required
def get_user_coupons(current_user):
    """Get user's coupons"""
    try:
        user_id = str(current_user['_id'])
        coupons = Coupon.find_by_user_id(user_id)
        
        return jsonify({
            'success': True,
            'coupons': coupons
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@reviews_bp.route('/admin/reviews', methods=['GET'])
@token_required
@admin_required
def admin_get_reviews(current_user):
    """Admin: Get all reviews with advanced filtering"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        status = request.args.get('status')
        author = request.args.get('author')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        filters = {}
        if status:
            filters['status'] = status
        if author:
            filters['author_name'] = {'$regex': author, '$options': 'i'}
        if date_from:
            filters['created_at'] = {'$gte': datetime.fromisoformat(date_from)}
        if date_to:
            if 'created_at' not in filters:
                filters['created_at'] = {}
            filters['created_at']['$lte'] = datetime.fromisoformat(date_to)
        
        reviews = Review.find_paginated(filters, page, limit)
        total_count = Review.count_documents(filters)
        
        # Get statistics
        stats = {
            'total_reviews': Review.count_documents({}),
            'published_reviews': Review.count_documents({'status': 'published'}),
            'pending_reviews': Review.count_documents({'status': 'pending'}),
            'average_rating': Review.get_average_rating()
        }
        
        return jsonify({
            'success': True,
            'reviews': reviews,
            'stats': stats,
            'pagination': {
                'current_page': page,
                'total_pages': (total_count + limit - 1) // limit,
                'total_count': total_count,
                'has_next': page * limit < total_count,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@reviews_bp.route('/admin/reviews/<review_id>/status', methods=['PUT'])
@token_required
@admin_required
def admin_update_review_status(current_user, review_id):
    """Admin: Update review status"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if status not in ['published', 'pending', 'rejected']:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
        review = Review.find_by_id(review_id)
        if not review:
            return jsonify({'success': False, 'message': 'Review not found'}), 404
        
        Review.update_by_id(review_id, {
            'status': status,
            'updated_at': datetime.utcnow()
        })
        
        return jsonify({'success': True, 'message': 'Review status updated'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@reviews_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all review categories"""
    categories = [
        'restaurants',
        'hotels',
        'attractions',
        'shopping',
        'nightlife',
        'tours',
        'transportation',
        'services',
        'gardens',
        'palaces',
        'markets',
        'museums'
    ]
    
    return jsonify({
        'success': True,
        'categories': categories
    }), 200

@reviews_bp.route('/stats', methods=['GET'])
def get_review_stats():
    """Get public review statistics"""
    try:
        stats = {
            'total_reviews': Review.count_documents({'status': 'published'}),
            'average_rating': Review.get_average_rating(),
            'categories_count': Review.get_categories_count(),
            'recent_reviews': Review.find_recent(5)
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

