from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import ObjectId
from datetime import datetime, timedelta

from src.models.database import mongo_db, create_response, serialize_doc
from src.utils.decorators import admin_required, moderator_required

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
@moderator_required
def get_dashboard_analytics():
    """Get dashboard analytics (admin/moderator)"""
    try:
        # Get date range
        days = int(request.args.get('days', 30))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Basic counts
        total_users = mongo_db.db.users.count_documents({})
        total_articles = mongo_db.db.articles.count_documents({})
        total_reviews = mongo_db.db.reviews.count_documents({})
        pending_reviews = mongo_db.db.reviews.count_documents({"status": "pending"})
        
        # Recent activity
        new_users = mongo_db.db.users.count_documents({
            "createdAt": {"$gte": start_date}
        })
        new_articles = mongo_db.db.articles.count_documents({
            "createdAt": {"$gte": start_date}
        })
        new_reviews = mongo_db.db.reviews.count_documents({
            "createdAt": {"$gte": start_date}
        })
        
        # User growth over time
        user_growth = list(mongo_db.db.users.aggregate([
            {
                "$match": {
                    "createdAt": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$createdAt"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]))
        
        # Article views and likes
        article_stats = list(mongo_db.db.articles.aggregate([
            {
                "$group": {
                    "_id": None,
                    "totalViews": {"$sum": "$views"},
                    "totalLikes": {"$sum": "$likes"},
                    "avgViews": {"$avg": "$views"},
                    "avgLikes": {"$avg": "$likes"}
                }
            }
        ]))
        
        # Review ratings distribution
        rating_distribution = list(mongo_db.db.reviews.aggregate([
            {
                "$match": {"status": "approved"}
            },
            {
                "$group": {
                    "_id": "$rating",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]))
        
        # Top categories
        top_categories = list(mongo_db.db.articles.aggregate([
            {
                "$match": {"status": "published"}
            },
            {
                "$group": {
                    "_id": "$category",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]))
        
        # Wallet statistics
        wallet_stats = list(mongo_db.db.users.aggregate([
            {
                "$group": {
                    "_id": None,
                    "totalBalance": {"$sum": "$wallet.balance"},
                    "avgBalance": {"$avg": "$wallet.balance"},
                    "usersWithWallet": {
                        "$sum": {
                            "$cond": [{"$gt": ["$wallet.balance", 0]}, 1, 0]
                        }
                    }
                }
            }
        ]))
        
        analytics_data = {
            "overview": {
                "totalUsers": total_users,
                "totalArticles": total_articles,
                "totalReviews": total_reviews,
                "pendingReviews": pending_reviews,
                "newUsers": new_users,
                "newArticles": new_articles,
                "newReviews": new_reviews
            },
            "userGrowth": user_growth,
            "articleStats": article_stats[0] if article_stats else {
                "totalViews": 0,
                "totalLikes": 0,
                "avgViews": 0,
                "avgLikes": 0
            },
            "ratingDistribution": rating_distribution,
            "topCategories": top_categories,
            "walletStats": wallet_stats[0] if wallet_stats else {
                "totalBalance": 0,
                "avgBalance": 0,
                "usersWithWallet": 0
            }
        }
        
        return jsonify(create_response(
            success=True,
            data=analytics_data,
            message="Dashboard analytics retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_DASHBOARD_ANALYTICS_ERROR", "message": str(e)}
        )), 500

@analytics_bp.route('/articles', methods=['GET'])
@moderator_required
def get_article_analytics():
    """Get article analytics"""
    try:
        # Most viewed articles
        most_viewed = list(mongo_db.db.articles.find(
            {"status": "published"},
            {"title": 1, "views": 1, "likes": 1, "author": 1, "publishedAt": 1}
        ).sort("views", -1).limit(10))
        
        # Most liked articles
        most_liked = list(mongo_db.db.articles.find(
            {"status": "published"},
            {"title": 1, "views": 1, "likes": 1, "author": 1, "publishedAt": 1}
        ).sort("likes", -1).limit(10))
        
        # Articles by status
        status_distribution = list(mongo_db.db.articles.aggregate([
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]))
        
        # Articles by author
        author_stats = list(mongo_db.db.articles.aggregate([
            {
                "$group": {
                    "_id": "$author",
                    "count": {"$sum": 1},
                    "totalViews": {"$sum": "$views"},
                    "totalLikes": {"$sum": "$likes"}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]))
        
        # Populate author information
        for stat in author_stats:
            if stat['_id']:
                author = mongo_db.db.users.find_one(
                    {"_id": ObjectId(stat['_id'])},
                    {"firstName": 1, "lastName": 1, "username": 1}
                )
                if author:
                    stat['authorInfo'] = serialize_doc(author)
        
        analytics_data = {
            "mostViewed": serialize_doc(most_viewed),
            "mostLiked": serialize_doc(most_liked),
            "statusDistribution": status_distribution,
            "authorStats": author_stats
        }
        
        return jsonify(create_response(
            success=True,
            data=analytics_data,
            message="Article analytics retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_ARTICLE_ANALYTICS_ERROR", "message": str(e)}
        )), 500

@analytics_bp.route('/reviews', methods=['GET'])
@moderator_required
def get_review_analytics():
    """Get review analytics"""
    try:
        # Reviews by status
        status_distribution = list(mongo_db.db.reviews.aggregate([
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]))
        
        # Average rating over time
        rating_trends = list(mongo_db.db.reviews.aggregate([
            {
                "$match": {"status": "approved"}
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m",
                            "date": "$createdAt"
                        }
                    },
                    "avgRating": {"$avg": "$rating"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]))
        
        # Most helpful reviews
        most_helpful = list(mongo_db.db.reviews.find(
            {"status": "approved"},
            {"title": 1, "rating": 1, "helpfulVotes": 1, "author": 1, "createdAt": 1}
        ).sort("helpfulVotes", -1).limit(10))
        
        # Reviews by location
        location_stats = list(mongo_db.db.reviews.aggregate([
            {
                "$match": {
                    "status": "approved",
                    "location.name": {"$ne": ""}
                }
            },
            {
                "$group": {
                    "_id": "$location.name",
                    "count": {"$sum": 1},
                    "avgRating": {"$avg": "$rating"}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]))
        
        # Moderation statistics
        moderation_stats = list(mongo_db.db.reviews.aggregate([
            {
                "$match": {"moderatedBy": {"$ne": None}}
            },
            {
                "$group": {
                    "_id": "$moderatedBy",
                    "approved": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "approved"]}, 1, 0]
                        }
                    },
                    "rejected": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "rejected"]}, 1, 0]
                        }
                    },
                    "hidden": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "hidden"]}, 1, 0]
                        }
                    }
                }
            }
        ]))
        
        # Populate moderator information
        for stat in moderation_stats:
            if stat['_id']:
                moderator = mongo_db.db.users.find_one(
                    {"_id": ObjectId(stat['_id'])},
                    {"firstName": 1, "lastName": 1, "username": 1}
                )
                if moderator:
                    stat['moderatorInfo'] = serialize_doc(moderator)
        
        analytics_data = {
            "statusDistribution": status_distribution,
            "ratingTrends": rating_trends,
            "mostHelpful": serialize_doc(most_helpful),
            "locationStats": location_stats,
            "moderationStats": moderation_stats
        }
        
        return jsonify(create_response(
            success=True,
            data=analytics_data,
            message="Review analytics retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_REVIEW_ANALYTICS_ERROR", "message": str(e)}
        )), 500

@analytics_bp.route('/users', methods=['GET'])
@admin_required
def get_user_analytics():
    """Get user analytics (admin only)"""
    try:
        # User registration trends
        registration_trends = list(mongo_db.db.users.aggregate([
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m",
                            "date": "$createdAt"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]))
        
        # Users by role
        role_distribution = list(mongo_db.db.users.aggregate([
            {
                "$group": {
                    "_id": "$role",
                    "count": {"$sum": 1}
                }
            }
        ]))
        
        # Active vs inactive users
        activity_stats = list(mongo_db.db.users.aggregate([
            {
                "$group": {
                    "_id": "$isActive",
                    "count": {"$sum": 1}
                }
            }
        ]))
        
        # Most active users (by articles and reviews)
        user_activity = list(mongo_db.db.users.aggregate([
            {
                "$lookup": {
                    "from": "articles",
                    "localField": "_id",
                    "foreignField": "author",
                    "as": "articles"
                }
            },
            {
                "$lookup": {
                    "from": "reviews",
                    "localField": "_id",
                    "foreignField": "author",
                    "as": "reviews"
                }
            },
            {
                "$project": {
                    "firstName": 1,
                    "lastName": 1,
                    "username": 1,
                    "role": 1,
                    "articleCount": {"$size": "$articles"},
                    "reviewCount": {"$size": "$reviews"},
                    "totalActivity": {
                        "$add": [
                            {"$size": "$articles"},
                            {"$size": "$reviews"}
                        ]
                    }
                }
            },
            {"$sort": {"totalActivity": -1}},
            {"$limit": 10}
        ]))
        
        # Login activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_logins = mongo_db.db.users.count_documents({
            "lastLogin": {"$gte": thirty_days_ago}
        })
        
        analytics_data = {
            "registrationTrends": registration_trends,
            "roleDistribution": role_distribution,
            "activityStats": activity_stats,
            "mostActiveUsers": serialize_doc(user_activity),
            "recentLogins": recent_logins,
            "totalUsers": mongo_db.db.users.count_documents({})
        }
        
        return jsonify(create_response(
            success=True,
            data=analytics_data,
            message="User analytics retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_USER_ANALYTICS_ERROR", "message": str(e)}
        )), 500

@analytics_bp.route('/export', methods=['GET'])
@admin_required
def export_analytics():
    """Export analytics data (admin only)"""
    try:
        export_type = request.args.get('type', 'dashboard')
        format_type = request.args.get('format', 'json')
        
        if export_type == 'dashboard':
            # Get dashboard analytics
            analytics_data = get_dashboard_analytics()
        elif export_type == 'articles':
            analytics_data = get_article_analytics()
        elif export_type == 'reviews':
            analytics_data = get_review_analytics()
        elif export_type == 'users':
            analytics_data = get_user_analytics()
        else:
            return jsonify(create_response(
                success=False,
                error={"code": "INVALID_EXPORT_TYPE", "message": "Invalid export type"}
            )), 400
        
        # Add export metadata
        export_data = {
            "exportType": export_type,
            "exportedAt": datetime.utcnow().isoformat(),
            "data": analytics_data
        }
        
        return jsonify(create_response(
            success=True,
            data=export_data,
            message="Analytics data exported successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "EXPORT_ANALYTICS_ERROR", "message": str(e)}
        )), 500

