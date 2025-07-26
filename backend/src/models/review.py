from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client.marrakech_reviews
reviews_collection = db.reviews

class Review:
    @staticmethod
    def create(review_data):
        """Create a new review"""
        result = reviews_collection.insert_one(review_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_id(review_id):
        """Find review by ID"""
        try:
            review = reviews_collection.find_one({'_id': ObjectId(review_id)})
            if review:
                review['_id'] = str(review['_id'])
            return review
        except:
            return None
    
    @staticmethod
    def find_all():
        """Find all reviews"""
        reviews = list(reviews_collection.find({'status': 'published'}).sort('created_at', -1))
        for review in reviews:
            review['_id'] = str(review['_id'])
        return reviews
    
    @staticmethod
    def find_paginated(filters=None, page=1, limit=10):
        """Find reviews with pagination"""
        if filters is None:
            filters = {}
        
        skip = (page - 1) * limit
        reviews = list(reviews_collection.find(filters)
                      .sort('created_at', -1)
                      .skip(skip)
                      .limit(limit))
        
        for review in reviews:
            review['_id'] = str(review['_id'])
        
        return reviews
    
    @staticmethod
    def find_by_author(author_id, page=1, limit=10):
        """Find reviews by author"""
        skip = (page - 1) * limit
        reviews = list(reviews_collection.find({'author_id': author_id})
                      .sort('created_at', -1)
                      .skip(skip)
                      .limit(limit))
        
        for review in reviews:
            review['_id'] = str(review['_id'])
        
        return reviews
    
    @staticmethod
    def find_by_category(category, page=1, limit=10):
        """Find reviews by category"""
        skip = (page - 1) * limit
        reviews = list(reviews_collection.find({
            'category': category,
            'status': 'published'
        }).sort('created_at', -1).skip(skip).limit(limit))
        
        for review in reviews:
            review['_id'] = str(review['_id'])
        
        return reviews
    
    @staticmethod
    def find_by_location(location, page=1, limit=10):
        """Find reviews by location"""
        skip = (page - 1) * limit
        reviews = list(reviews_collection.find({
            'location': {'$regex': location, '$options': 'i'},
            'status': 'published'
        }).sort('created_at', -1).skip(skip).limit(limit))
        
        for review in reviews:
            review['_id'] = str(review['_id'])
        
        return reviews
    
    @staticmethod
    def find_recent(limit=5):
        """Find recent reviews"""
        reviews = list(reviews_collection.find({'status': 'published'})
                      .sort('created_at', -1)
                      .limit(limit))
        
        for review in reviews:
            review['_id'] = str(review['_id'])
        
        return reviews
    
    @staticmethod
    def find_popular(limit=5):
        """Find popular reviews (by views and likes)"""
        reviews = list(reviews_collection.find({'status': 'published'})
                      .sort([('views', -1), ('likes', -1)])
                      .limit(limit))
        
        for review in reviews:
            review['_id'] = str(review['_id'])
        
        return reviews
    
    @staticmethod
    def search(query, page=1, limit=10):
        """Search reviews by text"""
        skip = (page - 1) * limit
        
        search_filter = {
            '$and': [
                {'status': 'published'},
                {
                    '$or': [
                        {'title': {'$regex': query, '$options': 'i'}},
                        {'content': {'$regex': query, '$options': 'i'}},
                        {'location': {'$regex': query, '$options': 'i'}},
                        {'tags': {'$in': [query]}}
                    ]
                }
            ]
        }
        
        reviews = list(reviews_collection.find(search_filter)
                      .sort('created_at', -1)
                      .skip(skip)
                      .limit(limit))
        
        for review in reviews:
            review['_id'] = str(review['_id'])
        
        return reviews
    
    @staticmethod
    def update_by_id(review_id, update_data):
        """Update review by ID"""
        try:
            result = reviews_collection.update_one(
                {'_id': ObjectId(review_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    @staticmethod
    def delete_by_id(review_id):
        """Delete review by ID"""
        try:
            result = reviews_collection.delete_one({'_id': ObjectId(review_id)})
            return result.deleted_count > 0
        except:
            return False
    
    @staticmethod
    def count_documents(filters=None):
        """Count documents matching filters"""
        if filters is None:
            filters = {}
        return reviews_collection.count_documents(filters)
    
    @staticmethod
    def increment_views(review_id):
        """Increment view count"""
        try:
            reviews_collection.update_one(
                {'_id': ObjectId(review_id)},
                {'$inc': {'views': 1}}
            )
            return True
        except:
            return False
    
    @staticmethod
    def increment_likes(review_id):
        """Increment like count"""
        try:
            reviews_collection.update_one(
                {'_id': ObjectId(review_id)},
                {'$inc': {'likes': 1}}
            )
            return True
        except:
            return False
    
    @staticmethod
    def decrement_likes(review_id):
        """Decrement like count"""
        try:
            reviews_collection.update_one(
                {'_id': ObjectId(review_id)},
                {'$inc': {'likes': -1}}
            )
            return True
        except:
            return False
    
    @staticmethod
    def increment_helpful_votes(review_id):
        """Increment helpful votes"""
        try:
            reviews_collection.update_one(
                {'_id': ObjectId(review_id)},
                {'$inc': {'helpful_votes': 1}}
            )
            return True
        except:
            return False
    
    @staticmethod
    def get_average_rating():
        """Get average rating across all reviews"""
        pipeline = [
            {'$match': {'status': 'published'}},
            {'$group': {'_id': None, 'avg_rating': {'$avg': '$rating'}}}
        ]
        
        result = list(reviews_collection.aggregate(pipeline))
        if result:
            return round(result[0]['avg_rating'], 2)
        return 0
    
    @staticmethod
    def get_categories_count():
        """Get count of reviews by category"""
        pipeline = [
            {'$match': {'status': 'published'}},
            {'$group': {'_id': '$category', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        
        result = list(reviews_collection.aggregate(pipeline))
        return {item['_id']: item['count'] for item in result}
    
    @staticmethod
    def get_rating_distribution():
        """Get distribution of ratings"""
        pipeline = [
            {'$match': {'status': 'published'}},
            {'$group': {'_id': '$rating', 'count': {'$sum': 1}}},
            {'$sort': {'_id': 1}}
        ]
        
        result = list(reviews_collection.aggregate(pipeline))
        return {item['_id']: item['count'] for item in result}
    
    @staticmethod
    def get_monthly_stats():
        """Get monthly review statistics"""
        pipeline = [
            {'$match': {'status': 'published'}},
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$created_at'},
                        'month': {'$month': '$created_at'}
                    },
                    'count': {'$sum': 1},
                    'avg_rating': {'$avg': '$rating'}
                }
            },
            {'$sort': {'_id.year': -1, '_id.month': -1}},
            {'$limit': 12}
        ]
        
        result = list(reviews_collection.aggregate(pipeline))
        return result
    
    @staticmethod
    def get_top_locations(limit=10):
        """Get top reviewed locations"""
        pipeline = [
            {'$match': {'status': 'published'}},
            {'$group': {
                '_id': '$location',
                'count': {'$sum': 1},
                'avg_rating': {'$avg': '$rating'}
            }},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]
        
        result = list(reviews_collection.aggregate(pipeline))
        return result
    
    @staticmethod
    def get_user_stats(user_id):
        """Get user's review statistics"""
        pipeline = [
            {'$match': {'author_id': user_id}},
            {
                '$group': {
                    '_id': None,
                    'total_reviews': {'$sum': 1},
                    'avg_rating_given': {'$avg': '$rating'},
                    'total_views': {'$sum': '$views'},
                    'total_likes': {'$sum': '$likes'},
                    'total_helpful_votes': {'$sum': '$helpful_votes'}
                }
            }
        ]
        
        result = list(reviews_collection.aggregate(pipeline))
        if result:
            stats = result[0]
            del stats['_id']
            return stats
        
        return {
            'total_reviews': 0,
            'avg_rating_given': 0,
            'total_views': 0,
            'total_likes': 0,
            'total_helpful_votes': 0
        }

