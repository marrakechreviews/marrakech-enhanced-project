from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime

from src.models.database import mongo_db, create_response, serialize_doc, paginate_query
from src.utils.decorators import user_required, admin_required, audit_log

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('', methods=['GET'])
@user_required
def get_notifications():
    """Get user notifications"""
    try:
        current_user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        # Build query
        query = {"recipient": ObjectId(current_user_id)}
        if unread_only:
            query['isRead'] = False
        
        # Get paginated notifications
        notifications, pagination = paginate_query(
            mongo_db.db.notifications,
            query,
            page,
            limit,
            'createdAt',
            -1
        )
        
        return jsonify(create_response(
            success=True,
            data=notifications,
            pagination=pagination,
            message="Notifications retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_NOTIFICATIONS_ERROR", "message": str(e)}
        )), 500

@notifications_bp.route('/<id>/read', methods=['PUT'])
@user_required
@audit_log('mark_notification_read', 'notification')
def mark_notification_read(id):
    """Mark notification as read"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find notification
        notification = mongo_db.db.notifications.find_one({
            "_id": ObjectId(id),
            "recipient": ObjectId(current_user_id)
        })
        
        if not notification:
            return jsonify(create_response(
                success=False,
                error={"code": "NOTIFICATION_NOT_FOUND", "message": "Notification not found"}
            )), 404
        
        # Mark as read
        mongo_db.db.notifications.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"isRead": True}}
        )
        
        return jsonify(create_response(
            success=True,
            message="Notification marked as read"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "MARK_READ_ERROR", "message": str(e)}
        )), 500

@notifications_bp.route('/read-all', methods=['PUT'])
@user_required
@audit_log('mark_all_notifications_read', 'notification')
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        current_user_id = get_jwt_identity()
        
        # Mark all user's notifications as read
        result = mongo_db.db.notifications.update_many(
            {
                "recipient": ObjectId(current_user_id),
                "isRead": False
            },
            {"$set": {"isRead": True}}
        )
        
        return jsonify(create_response(
            success=True,
            data={"updated_count": result.modified_count},
            message=f"Marked {result.modified_count} notifications as read"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "MARK_ALL_READ_ERROR", "message": str(e)}
        )), 500

@notifications_bp.route('/<id>', methods=['DELETE'])
@user_required
@audit_log('delete_notification', 'notification')
def delete_notification(id):
    """Delete notification"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find notification
        notification = mongo_db.db.notifications.find_one({
            "_id": ObjectId(id),
            "recipient": ObjectId(current_user_id)
        })
        
        if not notification:
            return jsonify(create_response(
                success=False,
                error={"code": "NOTIFICATION_NOT_FOUND", "message": "Notification not found"}
            )), 404
        
        # Delete notification
        mongo_db.db.notifications.delete_one({"_id": ObjectId(id)})
        
        return jsonify(create_response(
            success=True,
            message="Notification deleted successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "DELETE_NOTIFICATION_ERROR", "message": str(e)}
        )), 500

@notifications_bp.route('/unread-count', methods=['GET'])
@user_required
def get_unread_count():
    """Get unread notifications count"""
    try:
        current_user_id = get_jwt_identity()
        
        # Count unread notifications
        count = mongo_db.db.notifications.count_documents({
            "recipient": ObjectId(current_user_id),
            "isRead": False
        })
        
        return jsonify(create_response(
            success=True,
            data={"count": count},
            message="Unread count retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_UNREAD_COUNT_ERROR", "message": str(e)}
        )), 500

@notifications_bp.route('/admin/send', methods=['POST'])
@admin_required
@audit_log('send_notification', 'notification')
def send_notification():
    """Send notification to user(s) (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify(create_response(
                    success=False,
                    error={"code": "MISSING_FIELD", "message": f"{field} is required"}
                )), 400
        
        title = data['title']
        message = data['message']
        notification_type = data.get('type', 'system')
        notification_data = data.get('data', {})
        
        # Determine recipients
        recipients = []
        if data.get('recipient_id'):
            # Single recipient
            recipients = [ObjectId(data['recipient_id'])]
        elif data.get('recipient_role'):
            # All users with specific role
            users = mongo_db.db.users.find({"role": data['recipient_role']}, {"_id": 1})
            recipients = [user['_id'] for user in users]
        elif data.get('all_users'):
            # All users
            users = mongo_db.db.users.find({}, {"_id": 1})
            recipients = [user['_id'] for user in users]
        else:
            return jsonify(create_response(
                success=False,
                error={"code": "NO_RECIPIENTS", "message": "No recipients specified"}
            )), 400
        
        # Create notifications
        notifications = []
        for recipient_id in recipients:
            notification_doc = {
                "recipient": recipient_id,
                "type": notification_type,
                "title": title,
                "message": message,
                "data": notification_data,
                "isRead": False,
                "createdAt": datetime.utcnow()
            }
            notifications.append(notification_doc)
        
        # Insert notifications
        if notifications:
            mongo_db.db.notifications.insert_many(notifications)
        
        return jsonify(create_response(
            success=True,
            data={"sent_count": len(notifications)},
            message=f"Notification sent to {len(notifications)} users"
        )), 201
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "SEND_NOTIFICATION_ERROR", "message": str(e)}
        )), 500

@notifications_bp.route('/admin/stats', methods=['GET'])
@admin_required
def get_notification_stats():
    """Get notification statistics (admin only)"""
    try:
        # Get notification statistics
        total_notifications = mongo_db.db.notifications.count_documents({})
        unread_notifications = mongo_db.db.notifications.count_documents({"isRead": False})
        
        # Get notifications by type
        type_stats = list(mongo_db.db.notifications.aggregate([
            {
                "$group": {
                    "_id": "$type",
                    "count": {"$sum": 1},
                    "unread": {
                        "$sum": {
                            "$cond": [{"$eq": ["$isRead", False]}, 1, 0]
                        }
                    }
                }
            }
        ]))
        
        # Get recent activity
        recent_notifications = list(mongo_db.db.notifications.find(
            {},
            {"title": 1, "type": 1, "createdAt": 1, "isRead": 1}
        ).sort("createdAt", -1).limit(10))
        
        stats_data = {
            "total": total_notifications,
            "unread": unread_notifications,
            "read": total_notifications - unread_notifications,
            "by_type": type_stats,
            "recent": serialize_doc(recent_notifications)
        }
        
        return jsonify(create_response(
            success=True,
            data=stats_data,
            message="Notification statistics retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_NOTIFICATION_STATS_ERROR", "message": str(e)}
        )), 500

@notifications_bp.route('/admin/cleanup', methods=['POST'])
@admin_required
@audit_log('cleanup_notifications', 'notification')
def cleanup_notifications():
    """Cleanup old notifications (admin only)"""
    try:
        data = request.get_json()
        days_old = data.get('days_old', 30)  # Default to 30 days
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Delete old read notifications
        result = mongo_db.db.notifications.delete_many({
            "isRead": True,
            "createdAt": {"$lt": cutoff_date}
        })
        
        return jsonify(create_response(
            success=True,
            data={"deleted_count": result.deleted_count},
            message=f"Cleaned up {result.deleted_count} old notifications"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "CLEANUP_NOTIFICATIONS_ERROR", "message": str(e)}
        )), 500

@notifications_bp.route('/preferences', methods=['GET'])
@user_required
def get_notification_preferences():
    """Get user notification preferences"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get user preferences
        user = mongo_db.db.users.find_one(
            {"_id": ObjectId(current_user_id)},
            {"preferences.notifications": 1}
        )
        
        if not user:
            return jsonify(create_response(
                success=False,
                error={"code": "USER_NOT_FOUND", "message": "User not found"}
            )), 404
        
        preferences = user.get('preferences', {}).get('notifications', {
            "email": True,
            "push": True,
            "review_approved": True,
            "article_published": True,
            "wallet_transactions": True,
            "system_updates": True
        })
        
        return jsonify(create_response(
            success=True,
            data=preferences,
            message="Notification preferences retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_PREFERENCES_ERROR", "message": str(e)}
        )), 500

@notifications_bp.route('/preferences', methods=['PUT'])
@user_required
@audit_log('update_notification_preferences', 'notification')
def update_notification_preferences():
    """Update user notification preferences"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Update user preferences
        mongo_db.db.users.update_one(
            {"_id": ObjectId(current_user_id)},
            {
                "$set": {
                    "preferences.notifications": data,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        return jsonify(create_response(
            success=True,
            data=data,
            message="Notification preferences updated successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "UPDATE_PREFERENCES_ERROR", "message": str(e)}
        )), 500

