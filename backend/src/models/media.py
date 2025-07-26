from datetime import datetime
from bson import ObjectId
from src.models.database import mongo_db, serialize_doc, serialize_docs
import os

class Media:
    """Media model for file management"""
    
    @staticmethod
    def create(data):
        """Create a new media record"""
        media_doc = {
            "filename": data['filename'],
            "originalName": data['originalName'],
            "path": data['path'],
            "url": data['url'],
            "mimeType": data['mimeType'],
            "size": data['size'],
            "dimensions": data.get('dimensions', {}),  # {width: int, height: int}
            "alt": data.get('alt', ''),
            "caption": data.get('caption', ''),
            "folder": data.get('folder', 'uploads'),
            "tags": data.get('tags', []),
            "uploadedBy": ObjectId(data['uploadedBy']),
            "isPublic": data.get('isPublic', True),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = mongo_db.db.media.insert_one(media_doc)
        media_doc['_id'] = result.inserted_id
        return serialize_doc(media_doc)
    
    @staticmethod
    def find_by_id(media_id):
        """Find media by ID"""
        media = mongo_db.db.media.find_one({"_id": ObjectId(media_id)})
        return serialize_doc(media) if media else None
    
    @staticmethod
    def find_by_filename(filename):
        """Find media by filename"""
        media = mongo_db.db.media.find_one({"filename": filename})
        return serialize_doc(media) if media else None
    
    @staticmethod
    def update(media_id, data):
        """Update media record"""
        update_data = data.copy()
        update_data['updatedAt'] = datetime.utcnow()
        
        result = mongo_db.db.media.update_one(
            {"_id": ObjectId(media_id)},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return Media.find_by_id(media_id)
        return None
    
    @staticmethod
    def delete(media_id):
        """Delete media record and file"""
        media = Media.find_by_id(media_id)
        if not media:
            return False
        
        # Delete physical file
        try:
            if os.path.exists(media['path']):
                os.remove(media['path'])
        except Exception as e:
            print(f"Error deleting file: {e}")
        
        # Delete database record
        result = mongo_db.db.media.delete_one({"_id": ObjectId(media_id)})
        return result.deleted_count > 0
    
    @staticmethod
    def find_all(query=None, page=1, limit=20, sort_field="createdAt", sort_order=-1):
        """Find media with pagination"""
        if query is None:
            query = {}
        
        skip = (page - 1) * limit
        total = mongo_db.db.media.count_documents(query)
        
        cursor = mongo_db.db.media.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)
        media_list = list(cursor)
        
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
        
        return serialize_docs(media_list), pagination
    
    @staticmethod
    def find_by_folder(folder, page=1, limit=20):
        """Find media by folder"""
        query = {"folder": folder}
        return Media.find_all(query, page, limit)
    
    @staticmethod
    def find_by_type(mime_type_prefix, page=1, limit=20):
        """Find media by MIME type (e.g., 'image/', 'video/')"""
        query = {"mimeType": {"$regex": f"^{mime_type_prefix}"}}
        return Media.find_all(query, page, limit)
    
    @staticmethod
    def find_by_user(user_id, page=1, limit=20):
        """Find media uploaded by user"""
        query = {"uploadedBy": ObjectId(user_id)}
        return Media.find_all(query, page, limit)
    
    @staticmethod
    def search(search_term, page=1, limit=20):
        """Search media by filename, alt text, or caption"""
        query = {
            "$or": [
                {"originalName": {"$regex": search_term, "$options": "i"}},
                {"alt": {"$regex": search_term, "$options": "i"}},
                {"caption": {"$regex": search_term, "$options": "i"}},
                {"tags": {"$in": [search_term]}}
            ]
        }
        return Media.find_all(query, page, limit)
    
    @staticmethod
    def get_folders():
        """Get all unique folders"""
        folders = mongo_db.db.media.distinct("folder")
        return folders
    
    @staticmethod
    def get_stats():
        """Get media statistics"""
        total_files = mongo_db.db.media.count_documents({})
        
        # Get total size
        size_stats = list(mongo_db.db.media.aggregate([
            {"$group": {"_id": None, "totalSize": {"$sum": "$size"}}}
        ]))
        total_size = size_stats[0]['totalSize'] if size_stats else 0
        
        # Get file type distribution
        type_stats = list(mongo_db.db.media.aggregate([
            {
                "$group": {
                    "_id": {"$substr": ["$mimeType", 0, {"$indexOfCP": ["$mimeType", "/"]}]},
                    "count": {"$sum": 1},
                    "size": {"$sum": "$size"}
                }
            }
        ]))
        
        # Get folder distribution
        folder_stats = list(mongo_db.db.media.aggregate([
            {
                "$group": {
                    "_id": "$folder",
                    "count": {"$sum": 1},
                    "size": {"$sum": "$size"}
                }
            }
        ]))
        
        return {
            "totalFiles": total_files,
            "totalSize": total_size,
            "typeDistribution": type_stats,
            "folderDistribution": folder_stats
        }
    
    @staticmethod
    def create_folder(folder_name):
        """Create a new folder (virtual folder in database)"""
        # Check if folder already exists
        existing = mongo_db.db.media.find_one({"folder": folder_name})
        if existing:
            return False
        
        # Create a placeholder document for the folder
        folder_doc = {
            "folder": folder_name,
            "isFolder": True,
            "createdAt": datetime.utcnow()
        }
        
        result = mongo_db.db.media_folders.insert_one(folder_doc)
        return result.inserted_id is not None
    
    @staticmethod
    def delete_folder(folder_name):
        """Delete a folder and all its contents"""
        # Delete all media in the folder
        mongo_db.db.media.delete_many({"folder": folder_name})
        
        # Delete folder record
        mongo_db.db.media_folders.delete_one({"folder": folder_name})
        
        return True
    
    @staticmethod
    def move_to_folder(media_ids, folder_name):
        """Move media files to a different folder"""
        object_ids = [ObjectId(mid) for mid in media_ids]
        
        result = mongo_db.db.media.update_many(
            {"_id": {"$in": object_ids}},
            {
                "$set": {
                    "folder": folder_name,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count
    
    @staticmethod
    def bulk_update_tags(media_ids, tags):
        """Bulk update tags for multiple media files"""
        object_ids = [ObjectId(mid) for mid in media_ids]
        
        result = mongo_db.db.media.update_many(
            {"_id": {"$in": object_ids}},
            {
                "$set": {
                    "tags": tags,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count
    
    @staticmethod
    def bulk_delete(media_ids):
        """Bulk delete multiple media files"""
        deleted_count = 0
        
        for media_id in media_ids:
            if Media.delete(media_id):
                deleted_count += 1
        
        return deleted_count

