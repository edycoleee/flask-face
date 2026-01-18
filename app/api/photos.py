from flask_restx import Namespace, Resource, fields
from flask import request
from werkzeug.datastructures import FileStorage
from app.services.photo_service import PhotoService

api = Namespace("photos", description="Photo Upload & Management")

# Definisi Model untuk Swagger UI
photo_response_model = api.model("PhotoResponse", {
    "id": fields.Integer(readonly=True),
    "user_id": fields.Integer(),
    "filename": fields.String(),
    "filepath": fields.String(),
    "width": fields.Integer(),
    "height": fields.Integer(),
    "created_at": fields.String()
})

photo_list_response_model = api.model("PhotoListResponse", {
    "files": fields.List(fields.Nested(photo_response_model)),
    "total": fields.Integer(),
    "errors": fields.Raw()
})

@api.route("/<int:user_id>/upload")
class PhotoUpload(Resource):
    @api.doc(
        responses={
            201: "Photo uploaded successfully",
            400: "Bad request - invalid file or user",
            404: "User not found"
        },
        params={
            "user_id": "User ID"
        }
    )
    @api.marshal_with(photo_response_model)
    def post(self, user_id):
        """Upload single photo (JPG/PNG), auto-resize to 224x224"""
        # Check if user exists
        from app.services.user_service import UserService
        user = UserService.get_user(user_id)
        if not user:
            api.abort(404, "User tidak ditemukan")
        
        # Check if file is provided
        if 'file' not in request.files:
            api.abort(400, "File tidak ditemukan dalam request")
        
        file = request.files['file']
        
        photo, error = PhotoService.upload_photo(user_id, file)
        if error:
            api.abort(400, error)
        
        return photo, 201

@api.route("/<int:user_id>/upload/multiple")
class PhotoUploadMultiple(Resource):
    @api.doc(
        responses={
            201: "Photos uploaded successfully",
            400: "Bad request - invalid files or user",
            404: "User not found"
        },
        params={
            "user_id": "User ID"
        }
    )
    @api.marshal_with(photo_list_response_model)
    def post(self, user_id):
        """Upload multiple photos (JPG/PNG), auto-resize to 224x224 each"""
        # Check if user exists
        from app.services.user_service import UserService
        user = UserService.get_user(user_id)
        if not user:
            api.abort(404, "User tidak ditemukan")
        
        # Check if files are provided
        if 'files[]' not in request.files:
            api.abort(400, "Files tidak ditemukan dalam request")
        
        files = request.files.getlist('files[]')
        
        response, error = PhotoService.upload_multiple_photos(user_id, files)
        if error:
            api.abort(400, error)
        
        return response, 201

@api.route("/<int:user_id>")
class UserPhotos(Resource):
    @api.doc(
        responses={
            200: "Photos retrieved successfully",
            404: "User not found"
        },
        params={
            "user_id": "User ID"
        }
    )
    @api.marshal_list_with(photo_response_model)
    def get(self, user_id):
        """Get all photos for a user"""
        from app.services.user_service import UserService
        user = UserService.get_user(user_id)
        if not user:
            api.abort(404, "User tidak ditemukan")
        
        photos = PhotoService.get_user_photos(user_id)
        if photos is None:
            api.abort(500, "Error mengambil data foto")
        
        return photos

@api.route("/<int:user_id>/<int:photo_id>")
class PhotoDelete(Resource):
    @api.doc(
        responses={
            200: "Photo deleted successfully",
            404: "Photo or user not found",
            500: "Server error"
        },
        params={
            "user_id": "User ID",
            "photo_id": "Photo ID"
        }
    )
    def delete(self, user_id, photo_id):
        """Delete a photo by ID"""
        from app.services.user_service import UserService
        user = UserService.get_user(user_id)
        if not user:
            api.abort(404, "User tidak ditemukan")
        
        success, error = PhotoService.delete_photo(photo_id, user_id)
        if not success:
            if "tidak ditemukan" in error:
                api.abort(404, error)
            api.abort(500, error)
        
        return {"message": f"Foto {photo_id} berhasil dihapus"}, 200
