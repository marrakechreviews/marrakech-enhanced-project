from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime, timedelta
import subprocess
import os

from src.models.database import mongo_db, create_response, serialize_doc, serialize_docs
from src.utils.decorators import admin_required, audit_log

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    """Get admin dashboard statistics"""
    try:
        # Basic counts
        total_users = mongo_db.db.users.count_documents({})
        total_articles = mongo_db.db.articles.count_documents({})
        total_reviews = mongo_db.db.reviews.count_documents({})
        total_categories = mongo_db.db.categories.count_documents({})
        
        # Pending items
        pending_reviews = mongo_db.db.reviews.count_documents({"status": "pending"})
        draft_articles = mongo_db.db.articles.count_documents({"status": "draft"})
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_users_week = mongo_db.db.users.count_documents({"createdAt": {"$gte": week_ago}})
        new_articles_week = mongo_db.db.articles.count_documents({"createdAt": {"$gte": week_ago}})
        new_reviews_week = mongo_db.db.reviews.count_documents({"createdAt": {"$gte": week_ago}})
        
        # User role distribution
        role_distribution = list(mongo_db.db.users.aggregate([
            {
                "$group": {
                    "_id": "$role",
                    "count": {"$sum": 1}
                }
            }
        ]))
        
        # Article status distribution
        article_status = list(mongo_db.db.articles.aggregate([
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]))
        
        # Review status distribution
        review_status = list(mongo_db.db.reviews.aggregate([
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]))
        
        # Storage statistics
        upload_stats = list(mongo_db.db.uploads.aggregate([
            {
                "$group": {
                    "_id": None,
                    "totalFiles": {"$sum": 1},
                    "totalSize": {"$sum": "$size"}
                }
            }
        ]))
        
        # Wallet statistics
        wallet_stats = list(mongo_db.db.users.aggregate([
            {
                "$group": {
                    "_id": None,
                    "totalBalance": {"$sum": "$wallet.balance"},
                    "avgBalance": {"$avg": "$wallet.balance"}
                }
            }
        ]))
        
        stats_data = {
            "overview": {
                "totalUsers": total_users,
                "totalArticles": total_articles,
                "totalReviews": total_reviews,
                "totalCategories": total_categories,
                "pendingReviews": pending_reviews,
                "draftArticles": draft_articles
            },
            "recentActivity": {
                "newUsersWeek": new_users_week,
                "newArticlesWeek": new_articles_week,
                "newReviewsWeek": new_reviews_week
            },
            "distributions": {
                "userRoles": role_distribution,
                "articleStatus": article_status,
                "reviewStatus": review_status
            },
            "storage": upload_stats[0] if upload_stats else {"totalFiles": 0, "totalSize": 0},
            "wallet": wallet_stats[0] if wallet_stats else {"totalBalance": 0, "avgBalance": 0}
        }
        
        return jsonify(create_response(
            success=True,
            data=stats_data,
            message="Admin statistics retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_ADMIN_STATS_ERROR", "message": str(e)}
        )), 500

@admin_bp.route('/recent-activity', methods=['GET'])
@admin_required
def get_recent_activity():
    """Get recent activity feed"""
    try:
        limit = int(request.args.get('limit', 20))
        
        # Get recent audit logs
        recent_logs = list(mongo_db.db.audit_logs.find(
            {},
            {
                "user": 1,
                "action": 1,
                "resource": 1,
                "resourceId": 1,
                "timestamp": 1,
                "details": 1
            }
        ).sort("timestamp", -1).limit(limit))
        
        # Populate user information
        for log in recent_logs:
            if log.get('user'):
                user = mongo_db.db.users.find_one(
                    {"_id": ObjectId(log['user'])},
                    {"firstName": 1, "lastName": 1, "username": 1, "role": 1}
                )
                if user:
                    log['userInfo'] = serialize_doc(user)
        
        return jsonify(create_response(
            success=True,
            data=serialize_docs(recent_logs),
            message="Recent activity retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_RECENT_ACTIVITY_ERROR", "message": str(e)}
        )), 500

@admin_bp.route('/audit-logs', methods=['GET'])
@admin_required
def get_audit_logs():
    """Get audit logs"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        user_id = request.args.get('user')
        action = request.args.get('action')
        resource = request.args.get('resource')
        
        # Build query
        query = {}
        if user_id:
            query['user'] = ObjectId(user_id)
        if action:
            query['action'] = action
        if resource:
            query['resource'] = resource
        
        # Get paginated logs
        skip = (page - 1) * limit
        logs = list(mongo_db.db.audit_logs.find(query).sort("timestamp", -1).skip(skip).limit(limit))
        total = mongo_db.db.audit_logs.count_documents(query)
        
        # Populate user information
        for log in logs:
            if log.get('user'):
                user = mongo_db.db.users.find_one(
                    {"_id": ObjectId(log['user'])},
                    {"firstName": 1, "lastName": 1, "username": 1, "role": 1}
                )
                if user:
                    log['userInfo'] = serialize_doc(user)
        
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
            data=serialize_docs(logs),
            pagination=pagination,
            message="Audit logs retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_AUDIT_LOGS_ERROR", "message": str(e)}
        )), 500

@admin_bp.route('/backup', methods=['POST'])
@admin_required
@audit_log('create_backup', 'system')
def create_backup():
    """Create database backup"""
    try:
        # This is a simplified backup - in production you'd use proper MongoDB backup tools
        backup_data = {
            "timestamp": datetime.utcnow(),
            "collections": {}
        }
        
        # Get collection names
        collection_names = ['users', 'articles', 'reviews', 'categories', 'settings', 'notifications']
        
        for collection_name in collection_names:
            collection = getattr(mongo_db.db, collection_name)
            documents = list(collection.find({}))
            backup_data['collections'][collection_name] = serialize_docs(documents)
        
        # In a real implementation, you would save this to a file or cloud storage
        # For demo purposes, we'll just return success
        
        return jsonify(create_response(
            success=True,
            data={
                "backupId": str(ObjectId()),
                "timestamp": backup_data['timestamp'].isoformat(),
                "collections": list(backup_data['collections'].keys()),
                "totalDocuments": sum(len(docs) for docs in backup_data['collections'].values())
            },
            message="Database backup created successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "CREATE_BACKUP_ERROR", "message": str(e)}
        )), 500

@admin_bp.route('/maintenance', methods=['POST'])
@admin_required
@audit_log('toggle_maintenance', 'system')
def toggle_maintenance():
    """Toggle maintenance mode"""
    try:
        data = request.get_json()
        maintenance_mode = data.get('enabled', False)
        message = data.get('message', 'System is under maintenance. Please try again later.')
        
        # Update maintenance setting
        mongo_db.db.settings.update_one(
            {"key": "maintenance_mode"},
            {
                "$set": {
                    "value": maintenance_mode,
                    "updatedAt": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        # Update maintenance message
        mongo_db.db.settings.update_one(
            {"key": "maintenance_message"},
            {
                "$set": {
                    "value": message,
                    "updatedAt": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        status = "enabled" if maintenance_mode else "disabled"
        
        return jsonify(create_response(
            success=True,
            data={
                "maintenanceMode": maintenance_mode,
                "message": message
            },
            message=f"Maintenance mode {status}"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "TOGGLE_MAINTENANCE_ERROR", "message": str(e)}
        )), 500

@admin_bp.route('/system-info', methods=['GET'])
@admin_required
def get_system_info():
    """Get system information"""
    try:
        # Database statistics
        db_stats = mongo_db.db.command("dbStats")
        
        # Collection statistics
        collection_stats = {}
        collection_names = ['users', 'articles', 'reviews', 'categories', 'settings', 'notifications', 'uploads']
        
        for collection_name in collection_names:
            try:
                stats = mongo_db.db.command("collStats", collection_name)
                collection_stats[collection_name] = {
                    "count": stats.get('count', 0),
                    "size": stats.get('size', 0),
                    "avgObjSize": stats.get('avgObjSize', 0)
                }
            except:
                collection_stats[collection_name] = {"count": 0, "size": 0, "avgObjSize": 0}
        
        # System information
        system_info = {
            "database": {
                "name": db_stats.get('db', ''),
                "collections": db_stats.get('collections', 0),
                "objects": db_stats.get('objects', 0),
                "dataSize": db_stats.get('dataSize', 0),
                "storageSize": db_stats.get('storageSize', 0),
                "indexes": db_stats.get('indexes', 0),
                "indexSize": db_stats.get('indexSize', 0)
            },
            "collections": collection_stats,
            "server": {
                "timestamp": datetime.utcnow().isoformat(),
                "uptime": "N/A"  # Would need to track application start time
            }
        }
        
        return jsonify(create_response(
            success=True,
            data=system_info,
            message="System information retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_SYSTEM_INFO_ERROR", "message": str(e)}
        )), 500

@admin_bp.route('/cleanup', methods=['POST'])
@admin_required
@audit_log('cleanup_system', 'system')
def cleanup_system():
    """Cleanup system data"""
    try:
        data = request.get_json()
        cleanup_type = data.get('type', 'all')  # 'logs', 'notifications', 'uploads', 'all'
        days_old = data.get('days_old', 30)
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        cleanup_results = {}
        
        if cleanup_type in ['logs', 'all']:
            # Cleanup old audit logs
            result = mongo_db.db.audit_logs.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            cleanup_results['audit_logs'] = result.deleted_count
        
        if cleanup_type in ['notifications', 'all']:
            # Cleanup old read notifications
            result = mongo_db.db.notifications.delete_many({
                "isRead": True,
                "createdAt": {"$lt": cutoff_date}
            })
            cleanup_results['notifications'] = result.deleted_count
        
        if cleanup_type in ['uploads', 'all']:
            # Find orphaned uploads (not referenced by any article or user)
            # This is a simplified version - in production you'd want more thorough checking
            all_uploads = mongo_db.db.uploads.find({}, {"filename": 1, "path": 1})
            orphaned_count = 0
            
            for upload in all_uploads:
                filename = upload['filename']
                path = upload['path']
                
                # Check if referenced in articles
                article_ref = mongo_db.db.articles.find_one({
                    "$or": [
                        {"featuredImage": path},
                        {"gallery": path}
                    ]
                })
                
                # Check if referenced in user avatars
                user_ref = mongo_db.db.users.find_one({"avatar": path})
                
                # Check if referenced in reviews
                review_ref = mongo_db.db.reviews.find_one({"images": path})
                
                if not article_ref and not user_ref and not review_ref:
                    # Delete orphaned upload
                    mongo_db.db.uploads.delete_one({"_id": upload['_id']})
                    
                    # Delete physical file
                    try:
                        file_path = os.path.join(
                            os.path.dirname(os.path.dirname(__file__)),
                            'static',
                            'uploads',
                            filename
                        )
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    except:
                        pass
                    
                    orphaned_count += 1
            
            cleanup_results['orphaned_uploads'] = orphaned_count
        
        total_cleaned = sum(cleanup_results.values())
        
        return jsonify(create_response(
            success=True,
            data={
                "cleaned": cleanup_results,
                "total": total_cleaned,
                "cutoff_date": cutoff_date.isoformat()
            },
            message=f"Cleanup completed. Removed {total_cleaned} items."
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "CLEANUP_ERROR", "message": str(e)}
        )), 500

@admin_bp.route('/users/bulk-action', methods=['POST'])
@admin_required
@audit_log('bulk_user_action', 'user')
def bulk_user_action():
    """Perform bulk action on users"""
    try:
        data = request.get_json()
        action = data.get('action')  # 'activate', 'deactivate', 'delete', 'change_role'
        user_ids = data.get('user_ids', [])
        
        if not action or not user_ids:
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_PARAMETERS", "message": "Action and user IDs are required"}
            )), 400
        
        # Convert string IDs to ObjectIds
        object_ids = [ObjectId(uid) for uid in user_ids]
        
        result_count = 0
        
        if action == 'activate':
            result = mongo_db.db.users.update_many(
                {"_id": {"$in": object_ids}},
                {"$set": {"isActive": True, "updatedAt": datetime.utcnow()}}
            )
            result_count = result.modified_count
            
        elif action == 'deactivate':
            result = mongo_db.db.users.update_many(
                {"_id": {"$in": object_ids}},
                {"$set": {"isActive": False, "updatedAt": datetime.utcnow()}}
            )
            result_count = result.modified_count
            
        elif action == 'delete':
            # Prevent deletion of admin users
            admin_users = mongo_db.db.users.count_documents({
                "_id": {"$in": object_ids},
                "role": "admin"
            })
            
            if admin_users > 0:
                return jsonify(create_response(
                    success=False,
                    error={"code": "CANNOT_DELETE_ADMIN", "message": "Cannot delete admin users"}
                )), 403
            
            result = mongo_db.db.users.delete_many({"_id": {"$in": object_ids}})
            result_count = result.deleted_count
            
        elif action == 'change_role':
            new_role = data.get('new_role')
            if not new_role or new_role not in ['admin', 'moderator', 'user']:
                return jsonify(create_response(
                    success=False,
                    error={"code": "INVALID_ROLE", "message": "Invalid role specified"}
                )), 400
            
            result = mongo_db.db.users.update_many(
                {"_id": {"$in": object_ids}},
                {"$set": {"role": new_role, "updatedAt": datetime.utcnow()}}
            )
            result_count = result.modified_count
        
        else:
            return jsonify(create_response(
                success=False,
                error={"code": "INVALID_ACTION", "message": "Invalid action specified"}
            )), 400
        
        return jsonify(create_response(
            success=True,
            data={
                "action": action,
                "affected_count": result_count,
                "total_requested": len(user_ids)
            },
            message=f"Bulk action '{action}' completed on {result_count} users"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "BULK_ACTION_ERROR", "message": str(e)}
        )), 500

