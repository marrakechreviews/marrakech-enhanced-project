from flask import current_app
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import json

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
    
    def init_app(self, app):
        self.client = MongoClient(app.config['MONGO_URI'])
        self.db = self.client.get_default_database()
        
        # Create indexes
        self.create_indexes()
    
    def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Users collection indexes
            self.db.users.create_index("email", unique=True)
            self.db.users.create_index("username", unique=True)
            self.db.users.create_index("role")
            self.db.users.create_index([("createdAt", -1)])
            
            # Articles collection indexes
            self.db.articles.create_index("slug", unique=True)
            self.db.articles.create_index("author")
            self.db.articles.create_index([("status", 1), ("publishedAt", -1)])
            self.db.articles.create_index([("category", 1), ("status", 1)])
            self.db.articles.create_index("tags")
            self.db.articles.create_index([("title", "text"), ("content", "text")])
            
            # Reviews collection indexes
            self.db.reviews.create_index("author")
            self.db.reviews.create_index("article")
            self.db.reviews.create_index([("status", 1), ("createdAt", -1)])
            self.db.reviews.create_index("location.name")
            self.db.reviews.create_index("rating")
            
            # Categories collection indexes
            self.db.categories.create_index("slug", unique=True)
            self.db.categories.create_index("parentCategory")
            
            # Settings collection indexes
            self.db.settings.create_index("key", unique=True)
            self.db.settings.create_index("category")
            
            # Notifications collection indexes
            self.db.notifications.create_index([("recipient", 1), ("isRead", 1), ("createdAt", -1)])
            
            # Audit logs collection indexes
            self.db.audit_logs.create_index([("user", 1), ("timestamp", -1)])
            self.db.audit_logs.create_index([("resource", 1), ("resourceId", 1)])
            self.db.audit_logs.create_index([("timestamp", -1)])
            
        except Exception as e:
            print(f"Error creating indexes: {e}")

# Global MongoDB instance
mongo_db = MongoDB()

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for MongoDB ObjectId and datetime"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def serialize_doc(doc):
    """Serialize MongoDB document to JSON-serializable format"""
    if doc is None:
        return None
    return json.loads(json.dumps(doc, cls=JSONEncoder))

def serialize_docs(docs):
    """Serialize list of MongoDB documents"""
    return [serialize_doc(doc) for doc in docs]

def create_response(success=True, data=None, message="", error=None, pagination=None):
    """Create standardized API response"""
    response = {
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if success:
        response["data"] = data
        response["message"] = message
        if pagination:
            response["pagination"] = pagination
    else:
        response["error"] = error or {"code": "UNKNOWN_ERROR", "message": "An unknown error occurred"}
    
    return response

def paginate_query(collection, query, page=1, limit=20, sort_field="createdAt", sort_order=-1):
    """Paginate MongoDB query results"""
    skip = (page - 1) * limit
    
    # Get total count
    total = collection.count_documents(query)
    
    # Get paginated results
    cursor = collection.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)
    results = list(cursor)
    
    # Calculate pagination info
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
    
    return serialize_docs(results), pagination

