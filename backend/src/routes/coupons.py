from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from src.models.database import mongo_db, create_response
from src.models.coupon import Coupon
from src.utils.decorators import admin_required, moderator_required, user_required

coupons_bp = Blueprint('coupons', __name__)

@coupons_bp.route('', methods=['GET'])
@user_required
def get_user_coupons():
    """Get available coupons for current user"""
    try:
        current_user_id = get_jwt_identity()
        coupons = Coupon.find_user_coupons(current_user_id)
        
        return jsonify(create_response(
            success=True,
            data=coupons,
            message="User coupons retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_USER_COUPONS_ERROR", "message": str(e)}
        )), 500

@coupons_bp.route('/weekly', methods=['POST'])
@user_required
def claim_weekly_coupon():
    """Claim weekly coupon for current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user already claimed this week
        week_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = week_start - timedelta(days=week_start.weekday())
        week_end = week_start + timedelta(days=7)
        
        existing_coupon = mongo_db.db.coupons.find_one({
            "applicableUsers": {"$in": [current_user_id]},
            "createdAt": {"$gte": week_start, "$lt": week_end},
            "type": "weekly_reward"
        })
        
        if existing_coupon:
            return jsonify(create_response(
                success=False,
                error={"code": "ALREADY_CLAIMED", "message": "You have already claimed your weekly coupon"}
            )), 409
        
        coupon = Coupon.create_weekly_coupon_for_user(current_user_id)
        
        return jsonify(create_response(
            success=True,
            data=coupon,
            message="Weekly coupon claimed successfully"
        )), 201
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "CLAIM_WEEKLY_COUPON_ERROR", "message": str(e)}
        )), 500

@coupons_bp.route('/validate', methods=['POST'])
@user_required
def validate_coupon():
    """Validate a coupon code"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        code = data.get('code', '').strip().upper()
        order_amount = data.get('orderAmount', 0)
        
        if not code:
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_CODE", "message": "Coupon code is required"}
            )), 400
        
        validation_result = Coupon.validate_coupon(code, current_user_id, order_amount)
        
        return jsonify(create_response(
            success=validation_result['valid'],
            data=validation_result.get('coupon'),
            error={"code": "INVALID_COUPON", "message": validation_result.get('error')} if not validation_result['valid'] else None,
            message="Coupon validated successfully" if validation_result['valid'] else validation_result.get('error')
        )), 200 if validation_result['valid'] else 400
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "VALIDATE_COUPON_ERROR", "message": str(e)}
        )), 500

@coupons_bp.route('/use', methods=['POST'])
@user_required
def use_coupon():
    """Use a coupon"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        code = data.get('code', '').strip().upper()
        order_amount = data.get('orderAmount', 0)
        
        if not code:
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_CODE", "message": "Coupon code is required"}
            )), 400
        
        # First validate the coupon
        validation_result = Coupon.validate_coupon(code, current_user_id, order_amount)
        
        if not validation_result['valid']:
            return jsonify(create_response(
                success=False,
                error={"code": "INVALID_COUPON", "message": validation_result['error']}
            )), 400
        
        # Use the coupon
        coupon = validation_result['coupon']
        usage_result = Coupon.use_coupon(coupon['_id'], current_user_id, order_amount)
        
        if not usage_result:
            return jsonify(create_response(
                success=False,
                error={"code": "USE_COUPON_ERROR", "message": "Failed to use coupon"}
            )), 500
        
        return jsonify(create_response(
            success=True,
            data={
                "coupon": coupon,
                "discount": usage_result['discount'],
                "usage": usage_result['usage']
            },
            message="Coupon used successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "USE_COUPON_ERROR", "message": str(e)}
        )), 500

@coupons_bp.route('/my-usage', methods=['GET'])
@user_required
def get_my_coupon_usage():
    """Get current user's coupon usage statistics"""
    try:
        current_user_id = get_jwt_identity()
        stats = Coupon.get_user_usage_stats(current_user_id)
        
        return jsonify(create_response(
            success=True,
            data=stats,
            message="Coupon usage statistics retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_COUPON_USAGE_ERROR", "message": str(e)}
        )), 500

# Admin routes
@coupons_bp.route('/admin', methods=['GET'])
@moderator_required
def get_all_coupons():
    """Get all coupons (admin/moderator)"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        status = request.args.get('status')  # active, inactive, expired
        
        query = {}
        if status == 'active':
            query = {
                "isActive": True,
                "validFrom": {"$lte": datetime.utcnow()},
                "validUntil": {"$gte": datetime.utcnow()}
            }
        elif status == 'inactive':
            query = {"isActive": False}
        elif status == 'expired':
            query = {"validUntil": {"$lt": datetime.utcnow()}}
        
        coupons, pagination = Coupon.find_all(query, page, limit)
        
        return jsonify(create_response(
            success=True,
            data=coupons,
            pagination=pagination,
            message="Coupons retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_ALL_COUPONS_ERROR", "message": str(e)}
        )), 500

@coupons_bp.route('/admin', methods=['POST'])
@admin_required
def create_coupon():
    """Create a new coupon (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'value']
        for field in required_fields:
            if not data.get(field):
                return jsonify(create_response(
                    success=False,
                    error={"code": "MISSING_FIELD", "message": f"{field} is required"}
                )), 400
        
        data['createdBy'] = current_user_id
        coupon = Coupon.create(data)
        
        return jsonify(create_response(
            success=True,
            data=coupon,
            message="Coupon created successfully"
        )), 201
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "CREATE_COUPON_ERROR", "message": str(e)}
        )), 500

@coupons_bp.route('/admin/<coupon_id>', methods=['PUT'])
@admin_required
def update_coupon(coupon_id):
    """Update a coupon (admin only)"""
    try:
        data = request.get_json()
        
        # Remove fields that shouldn't be updated
        data.pop('_id', None)
        data.pop('createdBy', None)
        data.pop('createdAt', None)
        data.pop('usageCount', None)
        
        coupon = Coupon.update(coupon_id, data)
        
        if not coupon:
            return jsonify(create_response(
                success=False,
                error={"code": "COUPON_NOT_FOUND", "message": "Coupon not found"}
            )), 404
        
        return jsonify(create_response(
            success=True,
            data=coupon,
            message="Coupon updated successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "UPDATE_COUPON_ERROR", "message": str(e)}
        )), 500

@coupons_bp.route('/admin/<coupon_id>', methods=['DELETE'])
@admin_required
def delete_coupon(coupon_id):
    """Delete a coupon (admin only)"""
    try:
        success = Coupon.delete(coupon_id)
        
        if not success:
            return jsonify(create_response(
                success=False,
                error={"code": "COUPON_NOT_FOUND", "message": "Coupon not found"}
            )), 404
        
        return jsonify(create_response(
            success=True,
            message="Coupon deleted successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "DELETE_COUPON_ERROR", "message": str(e)}
        )), 500

@coupons_bp.route('/admin/stats', methods=['GET'])
@moderator_required
def get_coupon_stats():
    """Get coupon statistics (admin/moderator)"""
    try:
        stats = Coupon.get_stats()
        
        return jsonify(create_response(
            success=True,
            data=stats,
            message="Coupon statistics retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_COUPON_STATS_ERROR", "message": str(e)}
        )), 500

@coupons_bp.route('/admin/<coupon_id>/usage', methods=['GET'])
@moderator_required
def get_coupon_usage(coupon_id):
    """Get usage details for a specific coupon"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        skip = (page - 1) * limit
        
        # Get usage records
        usage_records = list(mongo_db.db.coupon_usage.find(
            {"couponId": coupon_id}
        ).sort("usedAt", -1).skip(skip).limit(limit))
        
        # Get total count
        total = mongo_db.db.coupon_usage.count_documents({"couponId": coupon_id})
        
        # Populate user information
        for record in usage_records:
            user = mongo_db.db.users.find_one(
                {"_id": record['userId']},
                {"firstName": 1, "lastName": 1, "email": 1}
            )
            if user:
                record['user'] = user
        
        # Calculate pagination
        total_pages = (total + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        pagination = {
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": total_pages,
            "hasNext": has_next,
            "hasPrev": has_prev
        }
        
        return jsonify(create_response(
            success=True,
            data=usage_records,
            pagination=pagination,
            message="Coupon usage retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_COUPON_USAGE_ERROR", "message": str(e)}
        )), 500

