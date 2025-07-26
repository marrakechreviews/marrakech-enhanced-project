from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

from src.models.database import mongo_db, create_response, serialize_doc, serialize_docs

search_bp = Blueprint('search', __name__)

@search_bp.route('', methods=['GET'])
def global_search():
    """Global search (articles, reviews, locations)"""
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', 'all')  # 'articles', 'reviews', 'locations', 'all'
        limit = int(request.args.get('limit', 20))
        
        if not query:
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_QUERY", "message": "Search query is required"}
            )), 400
        
        results = {
            "articles": [],
            "reviews": [],
            "locations": [],
            "total": 0
        }
        
        # Search articles
        if category in ['articles', 'all']:
            article_query = {
                "status": "published",
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"content": {"$regex": query, "$options": "i"}},
                    {"category": {"$regex": query, "$options": "i"}},
                    {"tags": {"$regex": query, "$options": "i"}}
                ]
            }
            
            articles = list(mongo_db.db.articles.find(
                article_query,
                {
                    "title": 1,
                    "excerpt": 1,
                    "featuredImage": 1,
                    "author": 1,
                    "category": 1,
                    "publishedAt": 1,
                    "views": 1,
                    "likes": 1,
                    "slug": 1
                }
            ).limit(limit))
            
            # Populate author information
            for article in articles:
                if article.get('author'):
                    author = mongo_db.db.users.find_one(
                        {"_id": ObjectId(article['author'])},
                        {"firstName": 1, "lastName": 1, "username": 1}
                    )
                    if author:
                        article['authorInfo'] = serialize_doc(author)
                article['type'] = 'article'
            
            results['articles'] = serialize_docs(articles)
        
        # Search reviews
        if category in ['reviews', 'all']:
            review_query = {
                "status": "approved",
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"content": {"$regex": query, "$options": "i"}},
                    {"location.name": {"$regex": query, "$options": "i"}}
                ]
            }
            
            reviews = list(mongo_db.db.reviews.find(
                review_query,
                {
                    "title": 1,
                    "content": 1,
                    "rating": 1,
                    "author": 1,
                    "location": 1,
                    "createdAt": 1,
                    "helpfulVotes": 1,
                    "images": 1
                }
            ).limit(limit))
            
            # Populate author information
            for review in reviews:
                if review.get('author'):
                    author = mongo_db.db.users.find_one(
                        {"_id": ObjectId(review['author'])},
                        {"firstName": 1, "lastName": 1, "username": 1}
                    )
                    if author:
                        review['authorInfo'] = serialize_doc(author)
                review['type'] = 'review'
            
            results['reviews'] = serialize_docs(reviews)
        
        # Search locations (from reviews)
        if category in ['locations', 'all']:
            location_pipeline = [
                {
                    "$match": {
                        "status": "approved",
                        "location.name": {"$regex": query, "$options": "i"}
                    }
                },
                {
                    "$group": {
                        "_id": "$location.name",
                        "reviewCount": {"$sum": 1},
                        "avgRating": {"$avg": "$rating"},
                        "location": {"$first": "$location"}
                    }
                },
                {"$sort": {"reviewCount": -1}},
                {"$limit": limit}
            ]
            
            locations = list(mongo_db.db.reviews.aggregate(location_pipeline))
            
            for location in locations:
                location['name'] = location['_id']
                location['type'] = 'location'
                del location['_id']
            
            results['locations'] = locations
        
        # Calculate total results
        results['total'] = len(results['articles']) + len(results['reviews']) + len(results['locations'])
        
        # If searching all categories, combine and sort by relevance
        if category == 'all':
            all_results = []
            all_results.extend(results['articles'])
            all_results.extend(results['reviews'])
            all_results.extend(results['locations'])
            
            # Simple relevance scoring (can be improved)
            for result in all_results:
                score = 0
                if result['type'] == 'article':
                    score += result.get('views', 0) * 0.1
                    score += result.get('likes', 0) * 0.2
                elif result['type'] == 'review':
                    score += result.get('helpfulVotes', 0) * 0.3
                    score += result.get('rating', 0) * 0.2
                elif result['type'] == 'location':
                    score += result.get('reviewCount', 0) * 0.5
                    score += result.get('avgRating', 0) * 0.3
                
                result['relevanceScore'] = score
            
            # Sort by relevance score
            all_results.sort(key=lambda x: x.get('relevanceScore', 0), reverse=True)
            results['combined'] = all_results[:limit]
        
        return jsonify(create_response(
            success=True,
            data=results,
            message=f"Found {results['total']} results for '{query}'"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GLOBAL_SEARCH_ERROR", "message": str(e)}
        )), 500

@search_bp.route('/articles', methods=['GET'])
def search_articles():
    """Search articles only"""
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category')
        author = request.args.get('author')
        limit = int(request.args.get('limit', 20))
        sort_by = request.args.get('sort', 'relevance')  # 'relevance', 'date', 'views', 'likes'
        
        if not query:
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_QUERY", "message": "Search query is required"}
            )), 400
        
        # Build search query
        search_query = {
            "status": "published",
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"content": {"$regex": query, "$options": "i"}},
                {"tags": {"$regex": query, "$options": "i"}}
            ]
        }
        
        if category:
            search_query["category"] = category
        
        if author:
            search_query["author"] = ObjectId(author)
        
        # Determine sort order
        sort_field = "publishedAt"
        sort_order = -1
        
        if sort_by == 'views':
            sort_field = "views"
        elif sort_by == 'likes':
            sort_field = "likes"
        elif sort_by == 'date':
            sort_field = "publishedAt"
        
        # Execute search
        articles = list(mongo_db.db.articles.find(
            search_query,
            {
                "title": 1,
                "excerpt": 1,
                "featuredImage": 1,
                "author": 1,
                "category": 1,
                "tags": 1,
                "publishedAt": 1,
                "views": 1,
                "likes": 1,
                "slug": 1
            }
        ).sort(sort_field, sort_order).limit(limit))
        
        # Populate author information
        for article in articles:
            if article.get('author'):
                author_info = mongo_db.db.users.find_one(
                    {"_id": ObjectId(article['author'])},
                    {"firstName": 1, "lastName": 1, "username": 1}
                )
                if author_info:
                    article['authorInfo'] = serialize_doc(author_info)
        
        return jsonify(create_response(
            success=True,
            data=serialize_docs(articles),
            message=f"Found {len(articles)} articles for '{query}'"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "SEARCH_ARTICLES_ERROR", "message": str(e)}
        )), 500

@search_bp.route('/reviews', methods=['GET'])
def search_reviews():
    """Search reviews only"""
    try:
        query = request.args.get('q', '').strip()
        location = request.args.get('location')
        rating = request.args.get('rating')
        limit = int(request.args.get('limit', 20))
        sort_by = request.args.get('sort', 'date')  # 'date', 'rating', 'helpful'
        
        if not query:
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_QUERY", "message": "Search query is required"}
            )), 400
        
        # Build search query
        search_query = {
            "status": "approved",
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"content": {"$regex": query, "$options": "i"}}
            ]
        }
        
        if location:
            search_query["location.name"] = {"$regex": location, "$options": "i"}
        
        if rating:
            search_query["rating"] = int(rating)
        
        # Determine sort order
        sort_field = "createdAt"
        sort_order = -1
        
        if sort_by == 'rating':
            sort_field = "rating"
        elif sort_by == 'helpful':
            sort_field = "helpfulVotes"
        
        # Execute search
        reviews = list(mongo_db.db.reviews.find(
            search_query,
            {
                "title": 1,
                "content": 1,
                "rating": 1,
                "author": 1,
                "location": 1,
                "createdAt": 1,
                "helpfulVotes": 1,
                "images": 1
            }
        ).sort(sort_field, sort_order).limit(limit))
        
        # Populate author information
        for review in reviews:
            if review.get('author'):
                author_info = mongo_db.db.users.find_one(
                    {"_id": ObjectId(review['author'])},
                    {"firstName": 1, "lastName": 1, "username": 1}
                )
                if author_info:
                    review['authorInfo'] = serialize_doc(author_info)
        
        return jsonify(create_response(
            success=True,
            data=serialize_docs(reviews),
            message=f"Found {len(reviews)} reviews for '{query}'"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "SEARCH_REVIEWS_ERROR", "message": str(e)}
        )), 500

@search_bp.route('/suggestions', methods=['GET'])
def get_search_suggestions():
    """Get search suggestions"""
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 10))
        
        if not query or len(query) < 2:
            return jsonify(create_response(
                success=True,
                data=[],
                message="Query too short for suggestions"
            )), 200
        
        suggestions = []
        
        # Get article title suggestions
        article_titles = mongo_db.db.articles.find(
            {
                "status": "published",
                "title": {"$regex": query, "$options": "i"}
            },
            {"title": 1}
        ).limit(limit // 2)
        
        for article in article_titles:
            suggestions.append({
                "text": article['title'],
                "type": "article",
                "id": str(article['_id'])
            })
        
        # Get location suggestions
        location_pipeline = [
            {
                "$match": {
                    "status": "approved",
                    "location.name": {"$regex": query, "$options": "i"}
                }
            },
            {
                "$group": {
                    "_id": "$location.name",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": limit // 2}
        ]
        
        locations = mongo_db.db.reviews.aggregate(location_pipeline)
        
        for location in locations:
            suggestions.append({
                "text": location['_id'],
                "type": "location",
                "count": location['count']
            })
        
        # Get category suggestions
        categories = mongo_db.db.categories.find(
            {
                "name": {"$regex": query, "$options": "i"},
                "isActive": True
            },
            {"name": 1}
        ).limit(5)
        
        for category in categories:
            suggestions.append({
                "text": category['name'],
                "type": "category",
                "id": str(category['_id'])
            })
        
        # Remove duplicates and limit results
        unique_suggestions = []
        seen_texts = set()
        
        for suggestion in suggestions:
            if suggestion['text'] not in seen_texts:
                unique_suggestions.append(suggestion)
                seen_texts.add(suggestion['text'])
                
                if len(unique_suggestions) >= limit:
                    break
        
        return jsonify(create_response(
            success=True,
            data=unique_suggestions,
            message="Search suggestions retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_SUGGESTIONS_ERROR", "message": str(e)}
        )), 500

@search_bp.route('/trending', methods=['GET'])
def get_trending_searches():
    """Get trending search terms"""
    try:
        # This would typically be based on search logs
        # For now, return popular categories and locations
        
        # Popular categories (based on article count)
        popular_categories = list(mongo_db.db.articles.aggregate([
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
            {"$limit": 5}
        ]))
        
        # Popular locations (based on review count)
        popular_locations = list(mongo_db.db.reviews.aggregate([
            {
                "$match": {
                    "status": "approved",
                    "location.name": {"$ne": ""}
                }
            },
            {
                "$group": {
                    "_id": "$location.name",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]))
        
        trending_data = {
            "categories": [cat['_id'] for cat in popular_categories if cat['_id']],
            "locations": [loc['_id'] for loc in popular_locations if loc['_id']],
            "keywords": ["marrakech", "medina", "atlas mountains", "desert", "riads"]  # Static for demo
        }
        
        return jsonify(create_response(
            success=True,
            data=trending_data,
            message="Trending searches retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_TRENDING_ERROR", "message": str(e)}
        )), 500

