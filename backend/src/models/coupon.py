from datetime import datetime, timedelta
from bson import ObjectId
from src.models.database import mongo_db, serialize_doc, serialize_docs
import random
import string

class Coupon:
    """Coupon model for user rewards and promotions"""
    
    @staticmethod
    def generate_code(length=8):
        """Generate a random coupon code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    @staticmethod
    def create(data):
        """Create a new coupon"""
        coupon_doc = {
            "code": data.get('code', Coupon.generate_code()),
            "title": data['title'],
            "description": data.get('description', ''),
            "type": data.get('type', 'discount'),  # discount, free_shipping, etc.
            "value": data['value'],  # percentage or fixed amount
            "valueType": data.get('valueType', 'percentage'),  # percentage or fixed
            "minOrderAmount": data.get('minOrderAmount', 0),
            "maxDiscount": data.get('maxDiscount', None),
            "usageLimit": data.get('usageLimit', 1),  # how many times can be used
            "usageCount": 0,
            "userLimit": data.get('userLimit', 1),  # how many times per user
            "validFrom": data.get('validFrom', datetime.utcnow()),
            "validUntil": data.get('validUntil', datetime.utcnow() + timedelta(days=30)),
            "isActive": data.get('isActive', True),
            "categories": data.get('categories', []),  # applicable categories
            "excludedCategories": data.get('excludedCategories', []),
            "applicableUsers": data.get('applicableUsers', []),  # specific users (empty = all)
            "createdBy": ObjectId(data['createdBy']),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = mongo_db.db.coupons.insert_one(coupon_doc)
        coupon_doc['_id'] = result.inserted_id
        return serialize_doc(coupon_doc)
    
    @staticmethod
    def find_by_id(coupon_id):
        """Find coupon by ID"""
        coupon = mongo_db.db.coupons.find_one({"_id": ObjectId(coupon_id)})
        return serialize_doc(coupon) if coupon else None
    
    @staticmethod
    def find_by_code(code):
        """Find coupon by code"""
        coupon = mongo_db.db.coupons.find_one({"code": code.upper()})
        return serialize_doc(coupon) if coupon else None
    
    @staticmethod
    def update(coupon_id, data):
        """Update coupon"""
        update_data = data.copy()
        update_data['updatedAt'] = datetime.utcnow()
        
        result = mongo_db.db.coupons.update_one(
            {"_id": ObjectId(coupon_id)},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return Coupon.find_by_id(coupon_id)
        return None
    
    @staticmethod
    def delete(coupon_id):
        """Delete coupon"""
        result = mongo_db.db.coupons.delete_one({"_id": ObjectId(coupon_id)})
        return result.deleted_count > 0
    
    @staticmethod
    def find_all(query=None, page=1, limit=20, sort_field="createdAt", sort_order=-1):
        """Find coupons with pagination"""
        if query is None:
            query = {}
        
        skip = (page - 1) * limit
        total = mongo_db.db.coupons.count_documents(query)
        
        cursor = mongo_db.db.coupons.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)
        coupons = list(cursor)
        
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
        
        return serialize_docs(coupons), pagination
    
    @staticmethod
    def find_active():
        """Find all active coupons"""
        query = {
            "isActive": True,
            "validFrom": {"$lte": datetime.utcnow()},
            "validUntil": {"$gte": datetime.utcnow()}
        }
        
        coupons = list(mongo_db.db.coupons.find(query))
        return serialize_docs(coupons)
    
    @staticmethod
    def find_user_coupons(user_id):
        """Find coupons available for a specific user"""
        query = {
            "isActive": True,
            "validFrom": {"$lte": datetime.utcnow()},
            "validUntil": {"$gte": datetime.utcnow()},
            "$or": [
                {"applicableUsers": []},  # Available to all users
                {"applicableUsers": ObjectId(user_id)}  # Specific to this user
            ]
        }
        
        coupons = list(mongo_db.db.coupons.find(query))
        return serialize_docs(coupons)
    
    @staticmethod
    def validate_coupon(code, user_id, order_amount=0):
        """Validate if a coupon can be used"""
        coupon = Coupon.find_by_code(code)
        
        if not coupon:
            return {"valid": False, "error": "Coupon not found"}
        
        # Check if active
        if not coupon['isActive']:
            return {"valid": False, "error": "Coupon is not active"}
        
        # Check validity dates
        now = datetime.utcnow()
        valid_from = datetime.fromisoformat(coupon['validFrom'].replace('Z', '+00:00')) if isinstance(coupon['validFrom'], str) else coupon['validFrom']
        valid_until = datetime.fromisoformat(coupon['validUntil'].replace('Z', '+00:00')) if isinstance(coupon['validUntil'], str) else coupon['validUntil']
        
        if now < valid_from:
            return {"valid": False, "error": "Coupon is not yet valid"}
        
        if now > valid_until:
            return {"valid": False, "error": "Coupon has expired"}
        
        # Check usage limit
        if coupon['usageLimit'] > 0 and coupon['usageCount'] >= coupon['usageLimit']:
            return {"valid": False, "error": "Coupon usage limit exceeded"}
        
        # Check minimum order amount
        if order_amount < coupon['minOrderAmount']:
            return {"valid": False, "error": f"Minimum order amount is ${coupon['minOrderAmount']}"}
        
        # Check user-specific restrictions
        if coupon['applicableUsers'] and ObjectId(user_id) not in [ObjectId(uid) for uid in coupon['applicableUsers']]:
            return {"valid": False, "error": "Coupon not applicable for this user"}
        
        # Check user usage limit
        user_usage = mongo_db.db.coupon_usage.count_documents({
            "couponId": ObjectId(coupon['_id']),
            "userId": ObjectId(user_id)
        })
        
        if user_usage >= coupon['userLimit']:
            return {"valid": False, "error": "You have already used this coupon"}
        
        return {"valid": True, "coupon": coupon}
    
    @staticmethod
    def use_coupon(coupon_id, user_id, order_amount=0):
        """Mark coupon as used"""
        coupon = Coupon.find_by_id(coupon_id)
        if not coupon:
            return False
        
        # Calculate discount
        discount = 0
        if coupon['valueType'] == 'percentage':
            discount = (order_amount * coupon['value']) / 100
            if coupon['maxDiscount'] and discount > coupon['maxDiscount']:
                discount = coupon['maxDiscount']
        else:
            discount = coupon['value']
        
        # Record usage
        usage_doc = {
            "couponId": ObjectId(coupon_id),
            "userId": ObjectId(user_id),
            "orderAmount": order_amount,
            "discountAmount": discount,
            "usedAt": datetime.utcnow()
        }
        
        mongo_db.db.coupon_usage.insert_one(usage_doc)
        
        # Increment usage count
        mongo_db.db.coupons.update_one(
            {"_id": ObjectId(coupon_id)},
            {"$inc": {"usageCount": 1}}
        )
        
        return {"discount": discount, "usage": serialize_doc(usage_doc)}
    
    @staticmethod
    def create_weekly_coupon_for_user(user_id):
        """Create a weekly coupon for a user"""
        # Check if user already has a coupon for this week
        week_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = week_start - timedelta(days=week_start.weekday())
        week_end = week_start + timedelta(days=7)
        
        existing_coupon = mongo_db.db.coupons.find_one({
            "applicableUsers": ObjectId(user_id),
            "createdAt": {"$gte": week_start, "$lt": week_end},
            "type": "weekly_reward"
        })
        
        if existing_coupon:
            return serialize_doc(existing_coupon)
        
        # Create new weekly coupon
        coupon_data = {
            "title": "Weekly Reward",
            "description": "Your weekly 10% discount coupon",
            "type": "weekly_reward",
            "value": 10,
            "valueType": "percentage",
            "maxDiscount": 50,
            "usageLimit": 1,
            "userLimit": 1,
            "validFrom": datetime.utcnow(),
            "validUntil": datetime.utcnow() + timedelta(days=7),
            "applicableUsers": [ObjectId(user_id)],
            "createdBy": ObjectId(user_id)
        }
        
        return Coupon.create(coupon_data)
    
    @staticmethod
    def get_user_usage_stats(user_id):
        """Get coupon usage statistics for a user"""
        pipeline = [
            {"$match": {"userId": ObjectId(user_id)}},
            {
                "$group": {
                    "_id": None,
                    "totalUsed": {"$sum": 1},
                    "totalSaved": {"$sum": "$discountAmount"},
                    "lastUsed": {"$max": "$usedAt"}
                }
            }
        ]
        
        result = list(mongo_db.db.coupon_usage.aggregate(pipeline))
        
        if result:
            stats = result[0]
            stats.pop('_id')
            return stats
        
        return {
            "totalUsed": 0,
            "totalSaved": 0,
            "lastUsed": None
        }
    
    @staticmethod
    def get_stats():
        """Get coupon statistics"""
        total_coupons = mongo_db.db.coupons.count_documents({})
        active_coupons = mongo_db.db.coupons.count_documents({"isActive": True})
        
        # Usage stats
        usage_stats = list(mongo_db.db.coupon_usage.aggregate([
            {
                "$group": {
                    "_id": None,
                    "totalUsage": {"$sum": 1},
                    "totalSavings": {"$sum": "$discountAmount"}
                }
            }
        ]))
        
        # Popular coupons
        popular_coupons = list(mongo_db.db.coupons.aggregate([
            {"$sort": {"usageCount": -1}},
            {"$limit": 5},
            {"$project": {"title": 1, "code": 1, "usageCount": 1}}
        ]))
        
        return {
            "totalCoupons": total_coupons,
            "activeCoupons": active_coupons,
            "totalUsage": usage_stats[0]['totalUsage'] if usage_stats else 0,
            "totalSavings": usage_stats[0]['totalSavings'] if usage_stats else 0,
            "popularCoupons": serialize_docs(popular_coupons)
        }

