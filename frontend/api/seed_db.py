import os
from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGODB_URI")

if not MONGO_URI:
    print("Error: MONGODB_URI environment variable not set. Please set it in your .env file.")
    exit(1)

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client.get_default_database() # This gets the database specified in the URI
    print(f"Successfully connected to MongoDB: {db.name}")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

# --- Clear existing data (optional, for fresh seeding) ---
print("Clearing existing data...")
db.users.delete_many({})
db.articles.delete_many({})
db.reviews.delete_many({})
db.categories.delete_many({})
print("Existing data cleared.")

# --- Seed Users ---
print("Seeding users...")
users_data = [
    {
        "username": "admin",
        "email": "admin@marrakechreviews.com",
        "password": generate_password_hash("SecureAdmin123!"),
        "role": "admin",
        "isActive": True,
        "createdAt": datetime.utcnow(),
        "lastLogin": datetime.utcnow()
    },
    {
        "username": "testuser",
        "email": "user@example.com",
        "password": generate_password_hash("password123"),
        "role": "user",
        "isActive": True,
        "createdAt": datetime.utcnow(),
        "lastLogin": datetime.utcnow()
    }
]

db.users.insert_many(users_data)
print("Users seeded.")

# --- Seed Categories ---
print("Seeding categories...")
categories_data = [
    {"name": "Restaurants", "slug": "restaurants", "description": "Best places to eat in Marrakech"},
    {"name": "Hotels & Riads", "slug": "hotels-riads", "description": "Accommodation options"},
    {"name": "Attractions", "slug": "attractions", "description": "Must-visit landmarks"},
    {"name": "Shopping", "slug": "shopping", "description": "Souks and markets"},
    {"name": "Activities", "slug": "activities", "description": "Things to do"},
]
db.categories.insert_many(categories_data)
print("Categories seeded.")

# --- Seed Articles ---
print("Seeding articles...")
articles_data = [
    {
        "title": "Exploring the Medina",
        "slug": "exploring-the-medina",
        "content": "A deep dive into the bustling alleys and hidden gems of Marrakech's old city.",
        "excerpt": "Discover the vibrant heart of Marrakech.",
        "author": "admin@marrakechreviews.com",
        "category": "Attractions",
        "tags": ["medina", "culture", "history"],
        "featuredImage": "https://res.cloudinary.com/your-cloud-name/image/upload/v1/marrakech-reviews/medina.jpg",
        "status": "published",
        "views": 1200,
        "publishedAt": datetime.utcnow(),
        "createdAt": datetime.utcnow()
    },
    {
        "title": "Marrakech Cuisine Guide",
        "slug": "marrakech-cuisine-guide",
        "content": "Savor the flavors of Morocco with our guide to the best food spots.",
        "excerpt": "A culinary journey through the Red City.",
        "author": "admin@marrakechreviews.com",
        "category": "Restaurants",
        "tags": ["food", "cuisine", "moroccan"],
        "featuredImage": "https://res.cloudinary.com/your-cloud-name/image/upload/v1/marrakech-reviews/food.jpg",
        "status": "published",
        "views": 950,
        "publishedAt": datetime.utcnow(),
        "createdAt": datetime.utcnow()
    },
    {
        "title": "Day Trips from Marrakech",
        "slug": "day-trips-from-marrakech",
        "content": "Discover exciting excursions to the Atlas Mountains and coastal towns.",
        "excerpt": "Beyond the city walls.",
        "author": "admin@marrakechreviews.com",
        "category": "Activities",
        "tags": ["atlas mountains", "essaouira", "desert"],
        "featuredImage": "https://res.cloudinary.com/your-cloud-name/image/upload/v1/marrakech-reviews/daytrip.jpg",
        "status": "published",
        "views": 780,
        "publishedAt": datetime.utcnow(),
        "createdAt": datetime.utcnow()
    }
]
db.articles.insert_many(articles_data)
print("Articles seeded.")

# --- Seed Reviews ---
print("Seeding reviews...")
reviews_data = [
    {
        "title": "Amazing experience at Jemaa el-Fna",
        "content": "The energy at Jemaa el-Fna is incredible! The food stalls offer delicious traditional dishes and the atmosphere is electric. A must-visit when in Marrakech.",
        "rating": 5,
        "author": "user@example.com",
        "location": {"name": "Jemaa el-Fna", "coordinates": [ -7.9892, 31.6362 ]},
        "tags": ["food", "atmosphere", "culture"],
        "helpfulVotes": 12,
        "likes": 8,
        "status": "published",
        "createdAt": datetime.utcnow()
    },
    {
        "title": "Peaceful escape at Majorelle Garden",
        "content": "After the chaos of the medina, Majorelle Garden is a perfect peaceful retreat. The blue buildings are stunning and the plants are beautiful. Worth the entrance fee!",
        "rating": 4,
        "author": "user@example.com",
        "location": {"name": "Majorelle Garden", "coordinates": [ -7.9920, 31.6380 ]},
        "tags": ["peaceful", "beautiful", "art"],
        "helpfulVotes": 7,
        "likes": 5,
        "status": "published",
        "createdAt": datetime.utcnow()
    }
]
db.reviews.insert_many(reviews_data)
print("Reviews seeded.")

print("Database seeding complete!")
client.close()


