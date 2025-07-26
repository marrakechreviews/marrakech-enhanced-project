from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from PIL import Image
import os
import uuid
from datetime import datetime

from src.models.database import mongo_db, create_response
from src.models.media import Media
from src.utils.decorators import admin_required, moderator_required, user_required

media_bp = Blueprint('media', __name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'mp4', 'mov', 'avi', 'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_dimensions(file_path, mime_type):
    """Get image dimensions"""
    if not mime_type.startswith('image/'):
        return {}
    
    try:
        with Image.open(file_path) as img:
            return {"width": img.width, "height": img.height}
    except Exception:
        return {}

@media_bp.route('/upload', methods=['POST'])
@user_required
def upload_file():
    """Upload a file to the media library"""
    try:
        current_user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify(create_response(
                success=False,
                error={"code": "NO_FILE", "message": "No file provided"}
            )), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify(create_response(
                success=False,
                error={"code": "NO_FILENAME", "message": "No file selected"}
            )), 400
        
        if not allowed_file(file.filename):
            return jsonify(create_response(
                success=False,
                error={"code": "INVALID_FILE_TYPE", "message": "File type not allowed"}
            )), 400
        
        # Get form data
        folder = request.form.get('folder', 'uploads')
        alt = request.form.get('alt', '')
        caption = request.form.get('caption', '')
        tags = request.form.get('tags', '').split(',') if request.form.get('tags') else []
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Create folder if it doesn't exist
        folder_path = os.path.join(UPLOAD_FOLDER, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(folder_path, unique_filename)
        file.save(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        mime_type = file.content_type or 'application/octet-stream'
        dimensions = get_file_dimensions(file_path, mime_type)
        
        # Create media record
        media_data = {
            "filename": unique_filename,
            "originalName": original_filename,
            "path": file_path,
            "url": f"/api/v1/media/file/{folder}/{unique_filename}",
            "mimeType": mime_type,
            "size": file_size,
            "dimensions": dimensions,
            "alt": alt,
            "caption": caption,
            "folder": folder,
            "tags": [tag.strip() for tag in tags if tag.strip()],
            "uploadedBy": current_user_id
        }
        
        media = Media.create(media_data)
        
        return jsonify(create_response(
            success=True,
            data=media,
            message="File uploaded successfully"
        )), 201
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "UPLOAD_ERROR", "message": str(e)}
        )), 500

@media_bp.route('/file/<folder>/<filename>', methods=['GET'])
def serve_file(folder, filename):
    """Serve uploaded files"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, folder, filename)
        
        if not os.path.exists(file_path):
            return jsonify(create_response(
                success=False,
                error={"code": "FILE_NOT_FOUND", "message": "File not found"}
            )), 404
        
        return send_file(file_path)
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "SERVE_FILE_ERROR", "message": str(e)}
        )), 500

@media_bp.route('', methods=['GET'])
@user_required
def get_media():
    """Get media library with pagination and filters"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        folder = request.args.get('folder')
        file_type = request.args.get('type')  # image, video, document
        search = request.args.get('search')
        
        if search:
            media_list, pagination = Media.search(search, page, limit)
        elif folder:
            media_list, pagination = Media.find_by_folder(folder, page, limit)
        elif file_type:
            type_map = {
                'image': 'image/',
                'video': 'video/',
                'document': 'application/'
            }
            mime_prefix = type_map.get(file_type, file_type)
            media_list, pagination = Media.find_by_type(mime_prefix, page, limit)
        else:
            media_list, pagination = Media.find_all(page=page, limit=limit)
        
        return jsonify(create_response(
            success=True,
            data=media_list,
            pagination=pagination,
            message="Media retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_MEDIA_ERROR", "message": str(e)}
        )), 500

@media_bp.route('/<media_id>', methods=['GET'])
@user_required
def get_media_by_id(media_id):
    """Get specific media file details"""
    try:
        media = Media.find_by_id(media_id)
        
        if not media:
            return jsonify(create_response(
                success=False,
                error={"code": "MEDIA_NOT_FOUND", "message": "Media not found"}
            )), 404
        
        return jsonify(create_response(
            success=True,
            data=media,
            message="Media retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_MEDIA_BY_ID_ERROR", "message": str(e)}
        )), 500

@media_bp.route('/<media_id>', methods=['PUT'])
@user_required
def update_media(media_id):
    """Update media metadata"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        media = Media.find_by_id(media_id)
        if not media:
            return jsonify(create_response(
                success=False,
                error={"code": "MEDIA_NOT_FOUND", "message": "Media not found"}
            )), 404
        
        # Check permissions (owner or admin/moderator)
        current_user = mongo_db.db.users.find_one({"_id": current_user_id})
        is_owner = str(media['uploadedBy']) == current_user_id
        is_admin_or_moderator = current_user and current_user.get('role') in ['admin', 'moderator']
        
        if not (is_owner or is_admin_or_moderator):
            return jsonify(create_response(
                success=False,
                error={"code": "ACCESS_DENIED", "message": "You can only edit your own media"}
            )), 403
        
        # Update allowed fields
        update_data = {}
        updatable_fields = ['alt', 'caption', 'folder', 'tags']
        
        for field in updatable_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify(create_response(
                success=False,
                error={"code": "NO_UPDATE_DATA", "message": "No valid fields to update"}
            )), 400
        
        updated_media = Media.update(media_id, update_data)
        
        return jsonify(create_response(
            success=True,
            data=updated_media,
            message="Media updated successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "UPDATE_MEDIA_ERROR", "message": str(e)}
        )), 500

@media_bp.route('/<media_id>', methods=['DELETE'])
@user_required
def delete_media(media_id):
    """Delete media file"""
    try:
        current_user_id = get_jwt_identity()
        
        media = Media.find_by_id(media_id)
        if not media:
            return jsonify(create_response(
                success=False,
                error={"code": "MEDIA_NOT_FOUND", "message": "Media not found"}
            )), 404
        
        # Check permissions (owner or admin)
        current_user = mongo_db.db.users.find_one({"_id": current_user_id})
        is_owner = str(media['uploadedBy']) == current_user_id
        is_admin = current_user and current_user.get('role') == 'admin'
        
        if not (is_owner or is_admin):
            return jsonify(create_response(
                success=False,
                error={"code": "ACCESS_DENIED", "message": "You can only delete your own media"}
            )), 403
        
        # Check if media is being used
        # Check articles
        article_usage = mongo_db.db.articles.find_one({
            "$or": [
                {"featuredImage": media['url']},
                {"gallery": media['url']}
            ]
        })
        
        # Check user avatars
        user_usage = mongo_db.db.users.find_one({"avatar": media['url']})
        
        if article_usage or user_usage:
            return jsonify(create_response(
                success=False,
                error={"code": "MEDIA_IN_USE", "message": "Media is being used and cannot be deleted"}
            )), 409
        
        success = Media.delete(media_id)
        
        if success:
            return jsonify(create_response(
                success=True,
                message="Media deleted successfully"
            )), 200
        else:
            return jsonify(create_response(
                success=False,
                error={"code": "DELETE_FAILED", "message": "Failed to delete media"}
            )), 500
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "DELETE_MEDIA_ERROR", "message": str(e)}
        )), 500

@media_bp.route('/folders', methods=['GET'])
@user_required
def get_folders():
    """Get all media folders"""
    try:
        folders = Media.get_folders()
        
        return jsonify(create_response(
            success=True,
            data=folders,
            message="Folders retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_FOLDERS_ERROR", "message": str(e)}
        )), 500

@media_bp.route('/folders', methods=['POST'])
@moderator_required
def create_folder():
    """Create a new folder"""
    try:
        data = request.get_json()
        folder_name = data.get('name', '').strip()
        
        if not folder_name:
            return jsonify(create_response(
                success=False,
                error={"code": "MISSING_FOLDER_NAME", "message": "Folder name is required"}
            )), 400
        
        # Validate folder name
        if not folder_name.replace('-', '').replace('_', '').isalnum():
            return jsonify(create_response(
                success=False,
                error={"code": "INVALID_FOLDER_NAME", "message": "Folder name can only contain letters, numbers, hyphens, and underscores"}
            )), 400
        
        success = Media.create_folder(folder_name)
        
        if success:
            return jsonify(create_response(
                success=True,
                data={"name": folder_name},
                message="Folder created successfully"
            )), 201
        else:
            return jsonify(create_response(
                success=False,
                error={"code": "FOLDER_EXISTS", "message": "Folder already exists"}
            )), 409
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "CREATE_FOLDER_ERROR", "message": str(e)}
        )), 500

@media_bp.route('/folders/<folder_name>', methods=['DELETE'])
@admin_required
def delete_folder(folder_name):
    """Delete a folder and all its contents"""
    try:
        success = Media.delete_folder(folder_name)
        
        return jsonify(create_response(
            success=True,
            message="Folder deleted successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "DELETE_FOLDER_ERROR", "message": str(e)}
        )), 500

@media_bp.route('/bulk/move', methods=['POST'])
@moderator_required
def bulk_move_media():
    """Move multiple media files to a folder"""
    try:
        data = request.get_json()
        media_ids = data.get('media_ids', [])
        folder_name = data.get('folder', 'uploads')
        
        if not media_ids:
            return jsonify(create_response(
                success=False,
                error={"code": "NO_MEDIA_IDS", "message": "No media IDs provided"}
            )), 400
        
        moved_count = Media.move_to_folder(media_ids, folder_name)
        
        return jsonify(create_response(
            success=True,
            data={"moved_count": moved_count},
            message=f"Moved {moved_count} files to {folder_name}"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "BULK_MOVE_ERROR", "message": str(e)}
        )), 500

@media_bp.route('/bulk/delete', methods=['POST'])
@admin_required
def bulk_delete_media():
    """Delete multiple media files"""
    try:
        data = request.get_json()
        media_ids = data.get('media_ids', [])
        
        if not media_ids:
            return jsonify(create_response(
                success=False,
                error={"code": "NO_MEDIA_IDS", "message": "No media IDs provided"}
            )), 400
        
        deleted_count = Media.bulk_delete(media_ids)
        
        return jsonify(create_response(
            success=True,
            data={"deleted_count": deleted_count},
            message=f"Deleted {deleted_count} files"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "BULK_DELETE_ERROR", "message": str(e)}
        )), 500

@media_bp.route('/stats', methods=['GET'])
@moderator_required
def get_media_stats():
    """Get media library statistics"""
    try:
        stats = Media.get_stats()
        
        return jsonify(create_response(
            success=True,
            data=stats,
            message="Media statistics retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_MEDIA_STATS_ERROR", "message": str(e)}
        )), 500

