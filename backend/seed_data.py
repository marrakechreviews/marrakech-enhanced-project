import os
import sys
from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash
import pymongo

# Connect to MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['marrakech_reviews']

# Clear existing data
print("Clearing existing data...")
db.users.delete_many({})
db.articles.delete_many({})
db.reviews.delete_many({})
db.categories.delete_many({})

# Create admin user
print("Creating admin user...")
admin_user = {
    "_id": ObjectId(),
    "username": "admin",
    "email": "admin@marrakechreviews.com", 
    "password": generate_password_hash("SecureAdmin123!"),
    "role": "admin",
    "firstName": "Admin",
    "lastName": "User",
    "isActive": True,
    "isVerified": True,
    "createdAt": datetime.utcnow(),
    "updatedAt": datetime.utcnow(),
    "profile": {
        "bio": "Administrator of Marrakech Reviews",
        "location": "Marrakech, Morocco",
        "website": "https://marrakechreviews.com"
    },
    "stats": {
        "reviewsCount": 0,
        "articlesCount": 0,
        "likesReceived": 0
    }
}
db.users.insert_one(admin_user)

# Create regular user
print("Creating regular user...")
regular_user = {
    "_id": ObjectId(),
    "username": "traveler123",
    "email": "user@example.com",
    "password": generate_password_hash("password123"),
    "role": "user", 
    "firstName": "John",
    "lastName": "Doe",
    "isActive": True,
    "isVerified": True,
    "createdAt": datetime.utcnow(),
    "updatedAt": datetime.utcnow(),
    "profile": {
        "bio": "Travel enthusiast exploring Morocco",
        "location": "New York, USA"
    },
    "stats": {
        "reviewsCount": 0,
        "articlesCount": 0,
        "likesReceived": 0
    }
}
db.users.insert_one(regular_user)

# Create categories
print("Creating categories...")
categories = [
    {"name": "Restaurants", "slug": "restaurants", "description": "Best dining experiences in Marrakech"},
    {"name": "Hotels & Riads", "slug": "hotels", "description": "Accommodation reviews and recommendations"},
    {"name": "Attractions", "slug": "attractions", "description": "Must-visit places and landmarks"},
    {"name": "Shopping", "slug": "shopping", "description": "Markets, souks, and shopping destinations"},
    {"name": "Activities", "slug": "activities", "description": "Tours, experiences, and adventures"}
]

for cat in categories:
    cat["_id"] = ObjectId()
    cat["createdAt"] = datetime.utcnow()
    cat["updatedAt"] = datetime.utcnow()
    cat["articlesCount"] = 0

db.categories.insert_many(categories)

# Create sample articles
print("Creating sample articles...")
articles = [
    {
        "_id": ObjectId(),
        "title": "Jemaa el-Fna: The Heart of Marrakech",
        "slug": "jemaa-el-fna-heart-of-marrakech",
        "content": "<p>Jemaa el-Fna is the main square and marketplace in Marrakech's medina quarter. This UNESCO World Heritage site comes alive every evening with food stalls, musicians, snake charmers, and storytellers.</p><p>During the day, you'll find orange juice vendors, henna artists, and traditional musicians. As the sun sets, the square transforms into a massive outdoor restaurant with dozens of food stalls serving traditional Moroccan cuisine.</p>",
        "excerpt": "Discover the vibrant heart of Marrakech at Jemaa el-Fna square, where tradition meets modernity in spectacular fashion.",
        "category": "attractions",
        "tags": ["jemaa el-fna", "medina", "unesco", "food", "culture"],
        "author": admin_user["_id"],
        "status": "published",
        "featuredImage": "https://images.unsplash.com/photo-1539650116574-75c0c6d73f6e?w=800",
        "views": 1250,
        "likes": 89,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
        "publishedAt": datetime.utcnow(),
        "seo": {
            "metaTitle": "Jemaa el-Fna Square Marrakech - Complete Guide 2025",
            "metaDescription": "Everything you need to know about visiting Jemaa el-Fna, the famous main square in Marrakech. Food, entertainment, and cultural experiences.",
            "keywords": ["jemaa el-fna", "marrakech square", "morocco travel", "medina"]
        }
    },
    {
        "_id": ObjectId(),
        "title": "Majorelle Garden: A Blue Oasis in Marrakech",
        "slug": "majorelle-garden-blue-oasis-marrakech",
        "content": "<p>The Majorelle Garden is a stunning botanical garden created by French artist Jacques Majorelle in the 1920s and later owned by fashion designer Yves Saint Laurent.</p><p>The garden is famous for its cobalt blue buildings, exotic plants, and peaceful atmosphere. It houses the Berber Museum and the Yves Saint Laurent Museum.</p>",
        "excerpt": "Escape the bustling medina at the serene Majorelle Garden, a botanical paradise painted in the iconic Majorelle blue.",
        "category": "attractions",
        "tags": ["majorelle garden", "yves saint laurent", "botanical", "art", "peaceful"],
        "author": admin_user["_id"],
        "status": "published",
        "featuredImage": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800",
        "views": 980,
        "likes": 67,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
        "publishedAt": datetime.utcnow(),
        "seo": {
            "metaTitle": "Majorelle Garden Marrakech - Visitor Guide & Tips",
            "metaDescription": "Visit the famous Majorelle Garden in Marrakech. Opening hours, tickets, and what to expect at this beautiful botanical garden.",
            "keywords": ["majorelle garden", "marrakech gardens", "yves saint laurent", "botanical garden"]
        }
    },
    {
        "_id": ObjectId(),
        "title": "Best Riads in Marrakech for 2025",
        "slug": "best-riads-marrakech-2025",
        "content": "<p>Riads are traditional Moroccan houses built around a central courtyard. Staying in a riad is one of the most authentic ways to experience Marrakech.</p><p>From luxury riads with rooftop pools to budget-friendly options in the medina, here are our top recommendations for the best riads in Marrakech.</p>",
        "excerpt": "Discover the most beautiful and authentic riads in Marrakech, from luxury retreats to charming budget options.",
        "category": "hotels",
        "tags": ["riads", "accommodation", "medina", "traditional", "luxury"],
        "author": admin_user["_id"],
        "status": "published",
        "featuredImage": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800",
        "views": 2100,
        "likes": 156,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
        "publishedAt": datetime.utcnow(),
        "seo": {
            "metaTitle": "Best Riads in Marrakech 2025 - Top Recommendations",
            "metaDescription": "Find the perfect riad for your stay in Marrakech. Reviews and recommendations for the best traditional Moroccan accommodations.",
            "keywords": ["riads marrakech", "marrakech hotels", "traditional accommodation", "medina hotels"]
        }
    }
]

db.articles.insert_many(articles)

# Create sample reviews
print("Creating sample reviews...")
reviews = [
    {
        "_id": ObjectId(),
        "title": "Amazing experience at Jemaa el-Fna",
        "content": "The energy at Jemaa el-Fna is incredible! The food stalls offer delicious traditional dishes and the atmosphere is electric. A must-visit when in Marrakech.",
        "rating": 5,
        "location": {
            "name": "Jemaa el-Fna",
            "type": "attraction",
            "coordinates": [31.6259, -7.9891]
        },
        "author": regular_user["_id"],
        "status": "approved",
        "helpful": 12,
        "likes": 8,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
        "visitDate": datetime.utcnow(),
        "tags": ["food", "atmosphere", "culture"]
    },
    {
        "_id": ObjectId(),
        "title": "Peaceful escape at Majorelle Garden",
        "content": "After the chaos of the medina, Majorelle Garden is a perfect peaceful retreat. The blue buildings are stunning and the plants are beautiful. Worth the entrance fee!",
        "rating": 4,
        "location": {
            "name": "Majorelle Garden",
            "type": "attraction",
            "coordinates": [31.6414, -8.0033]
        },
        "author": regular_user["_id"],
        "status": "approved",
        "helpful": 7,
        "likes": 5,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
        "visitDate": datetime.utcnow(),
        "tags": ["peaceful", "beautiful", "art"]
    }
]

db.reviews.insert_many(reviews)

print("Sample data created successfully!")
print("Admin credentials: admin@marrakechreviews.com / SecureAdmin123!")
print("User credentials: user@example.com / password123")

client.close()
