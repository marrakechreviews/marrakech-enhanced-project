from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
import requests
import os
from datetime import datetime, timedelta

from src.models.database import mongo_db, create_response, serialize_doc, serialize_docs
from src.utils.decorators import admin_required, audit_log

tripadvisor_bp = Blueprint('tripadvisor', __name__)

# Mock TripAdvisor data for demonstration (replace with real API calls)
MOCK_ATTRACTIONS = [
    {
        "id": "1",
        "name": "Jemaa el-Fnaa",
        "description": "The main square and marketplace in Marrakech's medina quarter",
        "image": "https://images.unsplash.com/photo-1539650116574-75c0c6d73f6e?w=800",
        "rating": 4.5,
        "reviews": 15420,
        "category": "Cultural Sites",
        "location": {
            "lat": 31.6259,
            "lng": -7.9891
        },
        "price_range": "Free",
        "opening_hours": "24 hours"
    },
    {
        "id": "2", 
        "name": "Majorelle Garden",
        "description": "Botanical garden and artist's landscape garden in Marrakech",
        "image": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800",
        "rating": 4.3,
        "reviews": 8932,
        "category": "Gardens",
        "location": {
            "lat": 31.6416,
            "lng": -8.0033
        },
        "price_range": "70 MAD",
        "opening_hours": "8:00 AM - 6:00 PM"
    },
    {
        "id": "3",
        "name": "Bahia Palace",
        "description": "19th-century palace with beautiful gardens and intricate architecture",
        "image": "https://images.unsplash.com/photo-1570939274717-7eda259b50ed?w=800",
        "rating": 4.2,
        "reviews": 6754,
        "category": "Historic Sites",
        "location": {
            "lat": 31.6214,
            "lng": -7.9844
        },
        "price_range": "70 MAD",
        "opening_hours": "9:00 AM - 5:00 PM"
    },
    {
        "id": "4",
        "name": "Koutoubia Mosque",
        "description": "The largest mosque in Marrakech with a famous minaret",
        "image": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800",
        "rating": 4.4,
        "reviews": 4521,
        "category": "Religious Sites",
        "location": {
            "lat": 31.6242,
            "lng": -7.9929
        },
        "price_range": "Free (exterior only)",
        "opening_hours": "Exterior viewable 24/7"
    },
    {
        "id": "5",
        "name": "Saadian Tombs",
        "description": "Historic royal necropolis dating from the 16th century",
        "image": "https://images.unsplash.com/photo-1570939274717-7eda259b50ed?w=800",
        "rating": 4.1,
        "reviews": 3892,
        "category": "Historic Sites",
        "location": {
            "lat": 31.6186,
            "lng": -7.9836
        },
        "price_range": "70 MAD",
        "opening_hours": "9:00 AM - 5:00 PM"
    }
]

MOCK_HOTELS = [
    {
        "id": "h1",
        "name": "La Mamounia",
        "description": "Luxury palace hotel in the heart of Marrakech",
        "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
        "rating": 4.8,
        "reviews": 2341,
        "price_range": "$$$$$",
        "amenities": ["Spa", "Pool", "Restaurant", "Garden"],
        "location": {
            "lat": 31.6295,
            "lng": -7.9811
        }
    },
    {
        "id": "h2",
        "name": "Royal Mansour Marrakech",
        "description": "Ultra-luxury resort with private riads",
        "image": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800",
        "rating": 4.9,
        "reviews": 1876,
        "price_range": "$$$$$",
        "amenities": ["Spa", "Multiple Pools", "Fine Dining", "Private Gardens"],
        "location": {
            "lat": 31.6311,
            "lng": -7.9897
        }
    },
    {
        "id": "h3",
        "name": "Riad Yasmine",
        "description": "Traditional riad with modern amenities",
        "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800",
        "rating": 4.3,
        "reviews": 892,
        "price_range": "$$$",
        "amenities": ["Rooftop Terrace", "Traditional Hammam", "Restaurant"],
        "location": {
            "lat": 31.6298,
            "lng": -7.9876
        }
    }
]

MOCK_RESTAURANTS = [
    {
        "id": "r1",
        "name": "Nomad",
        "description": "Modern Moroccan cuisine with rooftop terrace",
        "image": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800",
        "rating": 4.6,
        "reviews": 3421,
        "cuisine": "Moroccan",
        "price_range": "$$$",
        "location": {
            "lat": 31.6289,
            "lng": -7.9889
        }
    },
    {
        "id": "r2",
        "name": "Le Jardin",
        "description": "Restaurant in a beautiful garden setting",
        "image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800",
        "rating": 4.4,
        "reviews": 2156,
        "cuisine": "Mediterranean",
        "price_range": "$$",
        "location": {
            "lat": 31.6301,
            "lng": -7.9823
        }
    },
    {
        "id": "r3",
        "name": "Dar Yacout",
        "description": "Traditional Moroccan palace restaurant",
        "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800",
        "rating": 4.5,
        "reviews": 1789,
        "cuisine": "Traditional Moroccan",
        "price_range": "$$$$",
        "location": {
            "lat": 31.6334,
            "lng": -7.9912
        }
    }
]

def get_cached_data(cache_key, expiry_hours=24):
    """Get cached data from database"""
    try:
        cached = mongo_db.db.cache.find_one({"key": cache_key})
        if cached:
            # Check if cache is still valid
            if datetime.utcnow() < cached['expires_at']:
                return cached['data']
            else:
                # Remove expired cache
                mongo_db.db.cache.delete_one({"key": cache_key})
        return None
    except:
        return None

def set_cached_data(cache_key, data, expiry_hours=24):
    """Set cached data in database"""
    try:
        expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
        mongo_db.db.cache.replace_one(
            {"key": cache_key},
            {
                "key": cache_key,
                "data": data,
                "expires_at": expires_at,
                "created_at": datetime.utcnow()
            },
            upsert=True
        )
    except:
        pass

@tripadvisor_bp.route('/attractions', methods=['GET'])
def get_attractions():
    """Get attractions for carousel"""
    try:
        # Check cache first
        cached_data = get_cached_data('tripadvisor_attractions')
        if cached_data:
            return jsonify(create_response(
                success=True,
                data=cached_data,
                message="Attractions retrieved from cache"
            )), 200
        
        # For demo purposes, use mock data
        # In production, replace with actual TripAdvisor API calls
        attractions_data = MOCK_ATTRACTIONS
        
        # Cache the data
        set_cached_data('tripadvisor_attractions', attractions_data)
        
        return jsonify(create_response(
            success=True,
            data=attractions_data,
            message="Attractions retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_ATTRACTIONS_ERROR", "message": str(e)}
        )), 500

@tripadvisor_bp.route('/hotels', methods=['GET'])
def get_hotels():
    """Get hotels data"""
    try:
        # Check cache first
        cached_data = get_cached_data('tripadvisor_hotels')
        if cached_data:
            return jsonify(create_response(
                success=True,
                data=cached_data,
                message="Hotels retrieved from cache"
            )), 200
        
        # For demo purposes, use mock data
        hotels_data = MOCK_HOTELS
        
        # Cache the data
        set_cached_data('tripadvisor_hotels', hotels_data)
        
        return jsonify(create_response(
            success=True,
            data=hotels_data,
            message="Hotels retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_HOTELS_ERROR", "message": str(e)}
        )), 500

@tripadvisor_bp.route('/restaurants', methods=['GET'])
def get_restaurants():
    """Get restaurants data"""
    try:
        # Check cache first
        cached_data = get_cached_data('tripadvisor_restaurants')
        if cached_data:
            return jsonify(create_response(
                success=True,
                data=cached_data,
                message="Restaurants retrieved from cache"
            )), 200
        
        # For demo purposes, use mock data
        restaurants_data = MOCK_RESTAURANTS
        
        # Cache the data
        set_cached_data('tripadvisor_restaurants', restaurants_data)
        
        return jsonify(create_response(
            success=True,
            data=restaurants_data,
            message="Restaurants retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_RESTAURANTS_ERROR", "message": str(e)}
        )), 500

@tripadvisor_bp.route('/sync', methods=['POST'])
@admin_required
@audit_log('sync_tripadvisor', 'tripadvisor')
def sync_tripadvisor_data():
    """Sync data from TripAdvisor (admin only)"""
    try:
        # Clear existing cache
        mongo_db.db.cache.delete_many({"key": {"$regex": "^tripadvisor_"}})
        
        # In a real implementation, this would:
        # 1. Call TripAdvisor API endpoints
        # 2. Process and validate the data
        # 3. Store in cache with appropriate expiry
        
        # For demo, we'll just refresh the cache with mock data
        set_cached_data('tripadvisor_attractions', MOCK_ATTRACTIONS, 24)
        set_cached_data('tripadvisor_hotels', MOCK_HOTELS, 24)
        set_cached_data('tripadvisor_restaurants', MOCK_RESTAURANTS, 24)
        
        return jsonify(create_response(
            success=True,
            message="TripAdvisor data synced successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "SYNC_ERROR", "message": str(e)}
        )), 500

@tripadvisor_bp.route('/search', methods=['GET'])
def search_tripadvisor():
    """Search TripAdvisor data"""
    try:
        query = request.args.get('q', '').lower()
        category = request.args.get('category', 'all')  # 'attractions', 'hotels', 'restaurants', 'all'
        
        if not query:
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_QUERY", "message": "Search query is required"}
            )), 400
        
        results = []
        
        # Search attractions
        if category in ['attractions', 'all']:
            for attraction in MOCK_ATTRACTIONS:
                if (query in attraction['name'].lower() or 
                    query in attraction['description'].lower() or
                    query in attraction['category'].lower()):
                    attraction_result = attraction.copy()
                    attraction_result['type'] = 'attraction'
                    results.append(attraction_result)
        
        # Search hotels
        if category in ['hotels', 'all']:
            for hotel in MOCK_HOTELS:
                if (query in hotel['name'].lower() or 
                    query in hotel['description'].lower()):
                    hotel_result = hotel.copy()
                    hotel_result['type'] = 'hotel'
                    results.append(hotel_result)
        
        # Search restaurants
        if category in ['restaurants', 'all']:
            for restaurant in MOCK_RESTAURANTS:
                if (query in restaurant['name'].lower() or 
                    query in restaurant['description'].lower() or
                    query in restaurant['cuisine'].lower()):
                    restaurant_result = restaurant.copy()
                    restaurant_result['type'] = 'restaurant'
                    results.append(restaurant_result)
        
        # Sort by rating (highest first)
        results.sort(key=lambda x: x.get('rating', 0), reverse=True)
        
        return jsonify(create_response(
            success=True,
            data=results,
            message=f"Found {len(results)} results for '{query}'"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "SEARCH_ERROR", "message": str(e)}
        )), 500

@tripadvisor_bp.route('/featured', methods=['GET'])
def get_featured_content():
    """Get featured content for homepage carousel"""
    try:
        # Get top-rated items from each category
        featured = {
            "attractions": sorted(MOCK_ATTRACTIONS, key=lambda x: x['rating'], reverse=True)[:3],
            "hotels": sorted(MOCK_HOTELS, key=lambda x: x['rating'], reverse=True)[:2],
            "restaurants": sorted(MOCK_RESTAURANTS, key=lambda x: x['rating'], reverse=True)[:2]
        }
        
        # Add type field to each item
        for attraction in featured['attractions']:
            attraction['type'] = 'attraction'
        for hotel in featured['hotels']:
            hotel['type'] = 'hotel'
        for restaurant in featured['restaurants']:
            restaurant['type'] = 'restaurant'
        
        return jsonify(create_response(
            success=True,
            data=featured,
            message="Featured content retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_FEATURED_ERROR", "message": str(e)}
        )), 500

@tripadvisor_bp.route('/stats', methods=['GET'])
@admin_required
def get_tripadvisor_stats():
    """Get TripAdvisor integration statistics (admin only)"""
    try:
        stats = {
            "attractions_count": len(MOCK_ATTRACTIONS),
            "hotels_count": len(MOCK_HOTELS),
            "restaurants_count": len(MOCK_RESTAURANTS),
            "last_sync": None,
            "cache_status": {}
        }
        
        # Check cache status
        cache_keys = ['tripadvisor_attractions', 'tripadvisor_hotels', 'tripadvisor_restaurants']
        for key in cache_keys:
            cached = mongo_db.db.cache.find_one({"key": key})
            if cached:
                stats['cache_status'][key] = {
                    "cached": True,
                    "expires_at": cached['expires_at'].isoformat(),
                    "created_at": cached['created_at'].isoformat()
                }
                if not stats['last_sync'] or cached['created_at'] > datetime.fromisoformat(stats['last_sync']):
                    stats['last_sync'] = cached['created_at'].isoformat()
            else:
                stats['cache_status'][key] = {"cached": False}
        
        return jsonify(create_response(
            success=True,
            data=stats,
            message="TripAdvisor statistics retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_STATS_ERROR", "message": str(e)}
        )), 500

