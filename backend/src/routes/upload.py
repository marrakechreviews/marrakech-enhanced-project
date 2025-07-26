from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from PIL import Image
import io

from src.models.database import mongo_db, create_response
from src.utils.decorators import user_required, admin_required, audit_log

upload_bp = Blueprint('upload', __name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_upload_folder():
    """Create upload folder if it doesn't exist"""
    upload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', UPLOAD_FOLDER)
    os.makedirs(upload_path, exist_ok=True)
    return upload_path

def resize_image(image_data, max_width=1200, max_height=800, quality=85):
    """Resize image while maintaining aspect ratio"""
    try:
        image = Image.open(io.BytesIO(image_data))
        
        # Convert RGBA to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Calculate new dimensions
        width, height = image.size
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save to bytes
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
    except Exception as e:
        print(f"Error resizing image: {e}")
        return image_data

@upload_bp.route('/image', methods=['POST'])
@user_required
@audit_log('upload_image', 'upload')
def upload_image():
    """Upload single image"""
    try:
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
                error={"code": "INVALID_FILE_TYPE", "message": f"Allowed file types: {', '.join(ALLOWED_EXTENSIONS)}"}
            )), 400
        
        # Check file size
        file_data = file.read()
        if len(file_data) > MAX_FILE_SIZE:
            return jsonify(create_response(
                success=False,
                error={"code": "FILE_TOO_LARGE", "message": f"File size must be less than {MAX_FILE_SIZE // (1024*1024)}MB"}
            )), 400
        
        # Create upload folder
        upload_path = create_upload_folder()
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Resize image if it's too large
        if file_extension in ['jpg', 'jpeg', 'png', 'webp']:
            file_data = resize_image(file_data)
            file_extension = 'jpg'  # Convert to JPEG after processing
            unique_filename = f"{uuid.uuid4().hex}.jpg"
        
        # Save file
        file_path = os.path.join(upload_path, unique_filename)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Create file record
        current_user_id = get_jwt_identity()
        file_record = {
            "filename": unique_filename,
            "originalName": file.filename,
            "size": len(file_data),
            "mimeType": f"image/{file_extension}",
            "uploadedBy": current_user_id,
            "uploadedAt": datetime.utcnow(),
            "path": f"/api/v1/upload/files/{unique_filename}"
        }
        
        result = mongo_db.db.uploads.insert_one(file_record)
        file_record['_id'] = str(result.inserted_id)
        
        return jsonify(create_response(
            success=True,
            data={
                "filename": unique_filename,
                "url": f"/api/v1/upload/files/{unique_filename}",
                "size": len(file_data),
                "originalName": file.filename
            },
            message="Image uploaded successfully"
        )), 201
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "UPLOAD_ERROR", "message": str(e)}
        )), 500

@upload_bp.route('/images', methods=['POST'])
@user_required
@audit_log('upload_multiple_images', 'upload')
def upload_multiple_images():
    """Upload multiple images"""
    try:
        if 'files' not in request.files:
            return jsonify(create_response(
                success=False,
                error={"code": "NO_FILES", "message": "No files provided"}
            )), 400
        
        files = request.files.getlist('files')
        
        if not files or len(files) == 0:
            return jsonify(create_response(
                success=False,
                error={"code": "NO_FILES", "message": "No files selected"}
            )), 400
        
        if len(files) > 10:  # Limit to 10 files per upload
            return jsonify(create_response(
                success=False,
                error={"code": "TOO_MANY_FILES", "message": "Maximum 10 files allowed per upload"}
            )), 400
        
        uploaded_files = []
        errors = []
        
        # Create upload folder
        upload_path = create_upload_folder()
        current_user_id = get_jwt_identity()
        
        for file in files:
            try:
                if file.filename == '':
                    errors.append({"file": "unnamed", "error": "No filename"})
                    continue
                
                if not allowed_file(file.filename):
                    errors.append({"file": file.filename, "error": "Invalid file type"})
                    continue
                
                # Check file size
                file_data = file.read()
                if len(file_data) > MAX_FILE_SIZE:
                    errors.append({"file": file.filename, "error": "File too large"})
                    continue
                
                # Generate unique filename
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                
                # Resize image if it's too large
                if file_extension in ['jpg', 'jpeg', 'png', 'webp']:
                    file_data = resize_image(file_data)
                    file_extension = 'jpg'
                    unique_filename = f"{uuid.uuid4().hex}.jpg"
                
                # Save file
                file_path = os.path.join(upload_path, unique_filename)
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                
                # Create file record
                file_record = {
                    "filename": unique_filename,
                    "originalName": file.filename,
                    "size": len(file_data),
                    "mimeType": f"image/{file_extension}",
                    "uploadedBy": current_user_id,
                    "uploadedAt": datetime.utcnow(),
                    "path": f"/api/v1/upload/files/{unique_filename}"
                }
                
                result = mongo_db.db.uploads.insert_one(file_record)
                
                uploaded_files.append({
                    "filename": unique_filename,
                    "url": f"/api/v1/upload/files/{unique_filename}",
                    "size": len(file_data),
                    "originalName": file.filename
                })
                
            except Exception as e:
                errors.append({"file": file.filename, "error": str(e)})
        
        return jsonify(create_response(
            success=True,
            data={
                "uploaded": uploaded_files,
                "errors": errors,
                "total": len(files),
                "successful": len(uploaded_files),
                "failed": len(errors)
            },
            message=f"Uploaded {len(uploaded_files)} of {len(files)} files successfully"
        )), 201
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "UPLOAD_ERROR", "message": str(e)}
        )), 500

@upload_bp.route('/avatar', methods=['POST'])
@user_required
@audit_log('upload_avatar', 'upload')
def upload_avatar():
    """Upload user avatar"""
    try:
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
                error={"code": "INVALID_FILE_TYPE", "message": f"Allowed file types: {', '.join(ALLOWED_EXTENSIONS)}"}
            )), 400
        
        # Check file size (smaller limit for avatars)
        file_data = file.read()
        if len(file_data) > 5 * 1024 * 1024:  # 5MB limit for avatars
            return jsonify(create_response(
                success=False,
                error={"code": "FILE_TOO_LARGE", "message": "Avatar file size must be less than 5MB"}
            )), 400
        
        # Create upload folder
        upload_path = create_upload_folder()
        
        # Generate unique filename
        unique_filename = f"avatar_{uuid.uuid4().hex}.jpg"
        
        # Resize avatar to square format
        try:
            image = Image.open(io.BytesIO(file_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Resize to square (200x200)
            size = (200, 200)
            image = image.resize(size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=90, optimize=True)
            file_data = output.getvalue()
            
        except Exception as e:
            return jsonify(create_response(
                success=False,
                error={"code": "IMAGE_PROCESSING_ERROR", "message": "Failed to process avatar image"}
            )), 400
        
        # Save file
        file_path = os.path.join(upload_path, unique_filename)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Update user avatar
        current_user_id = get_jwt_identity()
        avatar_url = f"/api/v1/upload/files/{unique_filename}"
        
        mongo_db.db.users.update_one(
            {"_id": ObjectId(current_user_id)},
            {
                "$set": {
                    "avatar": avatar_url,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        # Create file record
        file_record = {
            "filename": unique_filename,
            "originalName": file.filename,
            "size": len(file_data),
            "mimeType": "image/jpeg",
            "uploadedBy": current_user_id,
            "uploadedAt": datetime.utcnow(),
            "path": avatar_url,
            "type": "avatar"
        }
        
        mongo_db.db.uploads.insert_one(file_record)
        
        return jsonify(create_response(
            success=True,
            data={
                "filename": unique_filename,
                "url": avatar_url,
                "size": len(file_data)
            },
            message="Avatar uploaded successfully"
        )), 201
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "AVATAR_UPLOAD_ERROR", "message": str(e)}
        )), 500

@upload_bp.route('/files/<filename>', methods=['GET'])
def serve_file(filename):
    """Serve uploaded files"""
    try:
        upload_path = create_upload_folder()
        return send_from_directory(upload_path, filename)
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "FILE_NOT_FOUND", "message": "File not found"}
        )), 404

@upload_bp.route('/<filename>', methods=['DELETE'])
@admin_required
@audit_log('delete_file', 'upload')
def delete_file(filename):
    """Delete uploaded file (admin only)"""
    try:
        # Find file record
        file_record = mongo_db.db.uploads.find_one({"filename": filename})
        if not file_record:
            return jsonify(create_response(
                success=False,
                error={"code": "FILE_NOT_FOUND", "message": "File not found"}
            )), 404
        
        # Delete physical file
        upload_path = create_upload_folder()
        file_path = os.path.join(upload_path, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete file record
        mongo_db.db.uploads.delete_one({"filename": filename})
        
        return jsonify(create_response(
            success=True,
            message="File deleted successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "DELETE_FILE_ERROR", "message": str(e)}
        )), 500

@upload_bp.route('/admin/files', methods=['GET'])
@admin_required
def get_all_files():
    """Get all uploaded files (admin only)"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Get paginated files
        skip = (page - 1) * limit
        files = list(mongo_db.db.uploads.find({}).sort("uploadedAt", -1).skip(skip).limit(limit))
        total = mongo_db.db.uploads.count_documents({})
        
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
        
        # Serialize files
        files_data = []
        for file_doc in files:
            file_data = {
                "id": str(file_doc['_id']),
                "filename": file_doc['filename'],
                "originalName": file_doc['originalName'],
                "size": file_doc['size'],
                "mimeType": file_doc['mimeType'],
                "uploadedBy": str(file_doc['uploadedBy']),
                "uploadedAt": file_doc['uploadedAt'].isoformat(),
                "url": file_doc['path']
            }
            files_data.append(file_data)
        
        return jsonify(create_response(
            success=True,
            data=files_data,
            pagination=pagination,
            message="Files retrieved successfully"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={"code": "GET_FILES_ERROR", "message": str(e)}
        )), 500

