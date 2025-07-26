from datetime import datetime
from bson import ObjectId
from src.models.database import mongo_db, serialize_doc, serialize_docs

class Article:
    """Article model for MongoDB operations"""
    
    @staticmethod
    def create(data):
        """Create a new article"""
        article_doc = {
            "title": data['title'],
            "slug": data['slug'],
            "content": data['content'],
            "excerpt": data.get('excerpt', ''),
            "featuredImage": data.get('featuredImage', ''),
            "gallery": data.get('gallery', []),
            "author": ObjectId(data['author']),
            "category": data.get('category', ''),
            "tags": data.get('tags', []),
            "seo": {
                "metaTitle": data.get('seo', {}).get('metaTitle', data['title']),
                "metaDescription": data.get('seo', {}).get('metaDescription', ''),
                "keywords": data.get('seo', {}).get('keywords', []),
                "canonicalUrl": data.get('seo', {}).get('canonicalUrl', ''),
                "ogTitle": data.get('seo', {}).get('ogTitle', data['title']),
                "ogDescription": data.get('seo', {}).get('ogDescription', ''),
                "ogImage": data.get('seo', {}).get('ogImage', ''),
                "twitterTitle": data.get('seo', {}).get('twitterTitle', data['title']),
                "twitterDescription": data.get('seo', {}).get('twitterDescription', ''),
                "twitterImage": data.get('seo', {}).get('twitterImage', ''),
                "structuredData": data.get('seo', {}).get('structuredData', {})
            },
            "status": data.get('status', 'draft'),
            "publishedAt": data.get('publishedAt'),
            "views": 0,
            "likes": 0,
            "readingTime": data.get('readingTime', 0),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = mongo_db.db.articles.insert_one(article_doc)
        article_doc['_id'] = result.inserted_id
        return serialize_doc(article_doc)
    
    @staticmethod
    def find_by_id(article_id):
        """Find article by ID"""
        article = mongo_db.db.articles.find_one({"_id": ObjectId(article_id)})
        return serialize_doc(article) if article else None
    
    @staticmethod
    def find_by_slug(slug):
        """Find article by slug"""
        article = mongo_db.db.articles.find_one({"slug": slug})
        return serialize_doc(article) if article else None
    
    @staticmethod
    def update(article_id, data):
        """Update article"""
        update_data = data.copy()
        update_data['updatedAt'] = datetime.utcnow()
        
        result = mongo_db.db.articles.update_one(
            {"_id": ObjectId(article_id)},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return Article.find_by_id(article_id)
        return None
    
    @staticmethod
    def delete(article_id):
        """Delete article"""
        result = mongo_db.db.articles.delete_one({"_id": ObjectId(article_id)})
        return result.deleted_count > 0
    
    @staticmethod
    def find_all(query=None, page=1, limit=20, sort_field="createdAt", sort_order=-1):
        """Find articles with pagination"""
        if query is None:
            query = {}
        
        skip = (page - 1) * limit
        total = mongo_db.db.articles.count_documents(query)
        
        cursor = mongo_db.db.articles.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)
        articles = list(cursor)
        
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
        
        return serialize_docs(articles), pagination
    
    @staticmethod
    def find_published(page=1, limit=20, category=None, author=None, search=None):
        """Find published articles"""
        query = {"status": "published"}
        
        if category:
            query['category'] = category
        if author:
            query['author'] = ObjectId(author)
        if search:
            query['$text'] = {'$search': search}
        
        return Article.find_all(query, page, limit, 'publishedAt', -1)
    
    @staticmethod
    def find_by_author(author_id, page=1, limit=20, status=None):
        """Find articles by author"""
        query = {"author": ObjectId(author_id)}
        if status:
            query['status'] = status
        
        return Article.find_all(query, page, limit)
    
    @staticmethod
    def increment_views(article_id):
        """Increment article view count"""
        mongo_db.db.articles.update_one(
            {"_id": ObjectId(article_id)},
            {"$inc": {"views": 1}}
        )
    
    @staticmethod
    def increment_likes(article_id):
        """Increment article like count"""
        mongo_db.db.articles.update_one(
            {"_id": ObjectId(article_id)},
            {"$inc": {"likes": 1}}
        )
    
    @staticmethod
    def publish(article_id):
        """Publish article"""
        return Article.update(article_id, {
            "status": "published",
            "publishedAt": datetime.utcnow()
        })
    
    @staticmethod
    def archive(article_id):
        """Archive article"""
        return Article.update(article_id, {"status": "archived"})
    
    @staticmethod
    def get_stats():
        """Get article statistics"""
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        status_stats = list(mongo_db.db.articles.aggregate(pipeline))
        
        total_articles = mongo_db.db.articles.count_documents({})
        total_views = list(mongo_db.db.articles.aggregate([
            {"$group": {"_id": None, "totalViews": {"$sum": "$views"}}}
        ]))
        
        return {
            "total": total_articles,
            "totalViews": total_views[0]['totalViews'] if total_views else 0,
            "statusDistribution": status_stats
        }

