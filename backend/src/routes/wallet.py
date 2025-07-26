from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
import uuid

from src.models.database import mongo_db, create_response, serialize_doc, paginate_query
from src.utils.decorators import admin_required, user_required, get_current_user, audit_log

wallet_bp = Blueprint('wallet', __name__)

@wallet_bp.route('', methods=['GET'])
@user_required
def get_wallet():
    """Get current user's wallet"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify(create_response(
                success=False,
                error={"code": "USER_NOT_FOUND", "message": "User not found"}
            )), 404
        
        wallet_data = current_user.get('wallet', {
            "balance": 0,
            "transactions": []
        })
        
        return jsonify(create_response(
            success=True,
            data=wallet_data,
            message="Wallet retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_WALLET_ERROR", "message": str(e)}
        )), 500

@wallet_bp.route('/transactions', methods=['GET'])
@user_required
def get_wallet_transactions():
    """Get wallet transaction history"""
    try:
        current_user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        transaction_type = request.args.get('type')  # 'credit' or 'debit'
        
        # Get user's wallet
        user = mongo_db.db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            return jsonify(create_response(
                success=False,
                error={"code": "USER_NOT_FOUND", "message": "User not found"}
            )), 404
        
        transactions = user.get('wallet', {}).get('transactions', [])
        
        # Filter by type if specified
        if transaction_type:
            transactions = [t for t in transactions if t.get('type') == transaction_type]
        
        # Sort by timestamp (newest first)
        transactions.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
        
        # Manual pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_transactions = transactions[start_idx:end_idx]
        
        # Calculate pagination info
        total = len(transactions)
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
            data=paginated_transactions,
            pagination=pagination,
            message="Transaction history retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_TRANSACTIONS_ERROR", "message": str(e)}
        )), 500

@wallet_bp.route('/balance', methods=['GET'])
@user_required
def get_wallet_balance():
    """Get wallet balance"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify(create_response(
                success=False,
                error={"code": "USER_NOT_FOUND", "message": "User not found"}
            )), 404
        
        balance = current_user.get('wallet', {}).get('balance', 0)
        
        return jsonify(create_response(
            success=True,
            data={"balance": balance},
            message="Balance retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_BALANCE_ERROR", "message": str(e)}
        )), 500

@wallet_bp.route('/add-coins', methods=['POST'])
@admin_required
@audit_log('add_coins', 'wallet')
def add_coins():
    """Add coins to user wallet (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['userId', 'amount', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify(create_response(
                    success=False,
                    error={"code": "MISSING_FIELD", "message": f"{field} is required"}
                )), 400
        
        user_id = data['userId']
        amount = float(data['amount'])
        description = data['description']
        
        if amount <= 0:
            return jsonify(create_response(
                success=False,
                error={"code": "INVALID_AMOUNT", "message": "Amount must be positive"}
            )), 400
        
        # Find user
        user = mongo_db.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify(create_response(
                success=False,
                error={"code": "USER_NOT_FOUND", "message": "User not found"}
            )), 404
        
        # Create transaction
        transaction = {
            "type": "credit",
            "amount": amount,
            "description": description,
            "timestamp": datetime.utcnow(),
            "transactionId": str(uuid.uuid4())
        }
        
        # Update user wallet
        current_balance = user.get('wallet', {}).get('balance', 0)
        new_balance = current_balance + amount
        
        mongo_db.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "wallet.balance": new_balance,
                    "updatedAt": datetime.utcnow()
                },
                "$push": {
                    "wallet.transactions": transaction
                }
            }
        )
        
        # Create notification for user
        notification_doc = {
            "recipient": ObjectId(user_id),
            "type": "wallet_transaction",
            "title": "Coins Added",
            "message": f"{amount} coins have been added to your wallet. {description}",
            "data": {"transactionId": transaction["transactionId"], "amount": amount},
            "isRead": False,
            "createdAt": datetime.utcnow()
        }
        mongo_db.db.notifications.insert_one(notification_doc)
        
        return jsonify(create_response(
            success=True,
            data={
                "transaction": transaction,
                "newBalance": new_balance
            },
            message="Coins added successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "ADD_COINS_ERROR", "message": str(e)}
        )), 500

@wallet_bp.route('/spend', methods=['POST'])
@user_required
@audit_log('spend_coins', 'wallet')
def spend_coins():
    """Spend coins from wallet"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify(create_response(
                    success=False,
                    error={"code": "MISSING_FIELD", "message": f"{field} is required"}
                )), 400
        
        amount = float(data['amount'])
        description = data['description']
        
        if amount <= 0:
            return jsonify(create_response(
                success=False,
                error={"code": "INVALID_AMOUNT", "message": "Amount must be positive"}
            )), 400
        
        # Get user
        user = mongo_db.db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            return jsonify(create_response(
                success=False,
                error={"code": "USER_NOT_FOUND", "message": "User not found"}
            )), 404
        
        # Check balance
        current_balance = user.get('wallet', {}).get('balance', 0)
        if current_balance < amount:
            return jsonify(create_response(
                success=False,
                error={"code": "INSUFFICIENT_BALANCE", "message": "Insufficient wallet balance"}
            )), 400
        
        # Create transaction
        transaction = {
            "type": "debit",
            "amount": amount,
            "description": description,
            "timestamp": datetime.utcnow(),
            "transactionId": str(uuid.uuid4())
        }
        
        # Update user wallet
        new_balance = current_balance - amount
        
        mongo_db.db.users.update_one(
            {"_id": ObjectId(current_user_id)},
            {
                "$set": {
                    "wallet.balance": new_balance,
                    "updatedAt": datetime.utcnow()
                },
                "$push": {
                    "wallet.transactions": transaction
                }
            }
        )
        
        return jsonify(create_response(
            success=True,
            data={
                "transaction": transaction,
                "newBalance": new_balance
            },
            message="Coins spent successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "SPEND_COINS_ERROR", "message": str(e)}
        )), 500

@wallet_bp.route('/reward', methods=['POST'])
@user_required
def reward_coins():
    """Reward coins for user actions (like writing reviews, articles)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        action = data.get('action')  # 'review_approved', 'article_published', etc.
        
        # Define reward amounts for different actions
        reward_amounts = {
            'review_approved': 10,
            'article_published': 25,
            'helpful_review': 5,
            'daily_login': 2
        }
        
        if action not in reward_amounts:
            return jsonify(create_response(
                success=False,
                error={"code": "INVALID_ACTION", "message": "Invalid reward action"}
            )), 400
        
        amount = reward_amounts[action]
        description = f"Reward for {action.replace('_', ' ')}"
        
        # Create transaction
        transaction = {
            "type": "credit",
            "amount": amount,
            "description": description,
            "timestamp": datetime.utcnow(),
            "transactionId": str(uuid.uuid4())
        }
        
        # Update user wallet
        user = mongo_db.db.users.find_one({"_id": ObjectId(current_user_id)})
        current_balance = user.get('wallet', {}).get('balance', 0)
        new_balance = current_balance + amount
        
        mongo_db.db.users.update_one(
            {"_id": ObjectId(current_user_id)},
            {
                "$set": {
                    "wallet.balance": new_balance,
                    "updatedAt": datetime.utcnow()
                },
                "$push": {
                    "wallet.transactions": transaction
                }
            }
        )
        
        # Create notification
        notification_doc = {
            "recipient": ObjectId(current_user_id),
            "type": "wallet_transaction",
            "title": "Coins Earned",
            "message": f"You earned {amount} coins for {action.replace('_', ' ')}!",
            "data": {"transactionId": transaction["transactionId"], "amount": amount},
            "isRead": False,
            "createdAt": datetime.utcnow()
        }
        mongo_db.db.notifications.insert_one(notification_doc)
        
        return jsonify(create_response(
            success=True,
            data={
                "transaction": transaction,
                "newBalance": new_balance
            },
            message=f"Earned {amount} coins for {action.replace('_', ' ')}"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "REWARD_COINS_ERROR", "message": str(e)}
        )), 500

@wallet_bp.route('/admin/stats', methods=['GET'])
@admin_required
def get_wallet_stats():
    """Get wallet statistics (admin only)"""
    try:
        # Aggregate wallet statistics
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "totalUsers": {"$sum": 1},
                    "totalBalance": {"$sum": "$wallet.balance"},
                    "avgBalance": {"$avg": "$wallet.balance"}
                }
            }
        ]
        
        stats = list(mongo_db.db.users.aggregate(pipeline))
        
        if not stats:
            stats_data = {
                "totalUsers": 0,
                "totalBalance": 0,
                "avgBalance": 0
            }
        else:
            stats_data = stats[0]
            del stats_data['_id']
        
        # Get transaction statistics
        transaction_pipeline = [
            {"$unwind": "$wallet.transactions"},
            {
                "$group": {
                    "_id": "$wallet.transactions.type",
                    "count": {"$sum": 1},
                    "totalAmount": {"$sum": "$wallet.transactions.amount"}
                }
            }
        ]
        
        transaction_stats = list(mongo_db.db.users.aggregate(transaction_pipeline))
        
        stats_data['transactionStats'] = transaction_stats
        
        return jsonify(create_response(
            success=True,
            data=stats_data,
            message="Wallet statistics retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_WALLET_STATS_ERROR", "message": str(e)}
        )), 500

