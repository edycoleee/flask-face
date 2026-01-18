# app/api/auth.py
from flask_restx import Namespace, Resource, fields
from flask import request
from werkzeug.datastructures import FileStorage
from pathlib import Path
import os
import tempfile
import logging

from app.services.auth_service import auth_service

logger = logging.getLogger(__name__)

api = Namespace("auth", description="Face Recognition Authentication API")

# File upload parser
login_parser = api.parser()
login_parser.add_argument('file', location='files', type=FileStorage, required=True,
                         help='Face image untuk login')

# File upload parser with user_id for verification
verify_login_parser = api.parser()
verify_login_parser.add_argument('user_id', location='form', type=int, required=True,
                                help='User ID to verify')
verify_login_parser.add_argument('file', location='files', type=FileStorage, required=True,
                                help='Face image untuk verification')

# Token verification model
verify_model = api.model("VerifyToken", {
    "token": fields.String(required=True, description='UUID token', example='550e8400-e29b-41d4-a716-446655440000')
})

# Logout model
logout_model = api.model("Logout", {
    "token": fields.String(required=True, description='UUID token', example='550e8400-e29b-41d4-a716-446655440000')
})

@api.route("/login-face")
class FaceLogin(Resource):
    @api.expect(login_parser)
    def post(self):
        """
        Login menggunakan face recognition
        
        Process:
        1. Upload foto wajah
        2. Prediksi user dengan CNN model
        3. Jika confidence > threshold (70%) → generate UUID token
        4. Simpan token ke database
        
        Returns:
            - user_id: ID user
            - name: Nama user
            - token: UUID token untuk authentication
            - confidence: Confidence score
            - expires_at: Token expiry time
        """
        try:
            logger.info("=" * 50)
            logger.info("LOGIN WITH FACE REQUEST")
            logger.info("=" * 50)
            
            # Parse file dari request
            try:
                args = login_parser.parse_args()
                file = args.get('file')
            except Exception as e:
                logger.error(f"Failed to parse args: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Failed to parse request: {str(e)}"
                }, 400
            
            if not file:
                logger.warning("No file in request")
                return {
                    "status": "error",
                    "message": "No file provided. Please upload a face image."
                }, 400
            
            # Validasi file
            if not file.filename:
                return {
                    "status": "error",
                    "message": "Invalid file - no filename"
                }, 400
            
            logger.info(f"Received file: {file.filename}")
            
            filename = file.filename.lower()
            if not (filename.endswith('.jpg') or filename.endswith('.jpeg') or 
                   filename.endswith('.png') or filename.endswith('.gif')):
                return {
                    "status": "error",
                    "message": f"Invalid file format. Only JPG/PNG allowed"
                }, 400
            
            # Save temporary file
            temp_dir = Path(tempfile.gettempdir())
            temp_path = temp_dir / f"login_{os.urandom(8).hex()}{Path(file.filename).suffix}"
            
            try:
                file.save(str(temp_path))
                logger.info(f"✓ Temporary file saved: {temp_path}")
                
                # Login with face
                result = auth_service.login_with_face(temp_path)
                
                if result['success']:
                    return {
                        "status": "success",
                        "message": "Login successful",
                        "data": {
                            "user_id": result['user_id'],
                            "name": result['name'],
                            "email": result['email'],
                            "token": result['token'],
                            "confidence": result['confidence'],
                            "expires_at": result['expires_at']
                        }
                    }, 200
                else:
                    return {
                        "status": "error",
                        "message": result['message'],
                        "data": {
                            "confidence": result['confidence'],
                            "required_confidence": result['required_confidence']
                        }
                    }, 401
                    
            finally:
                # Cleanup
                if temp_path.exists():
                    temp_path.unlink()
                    logger.info(f"✓ Temporary file deleted: {temp_path}")
        
        except FileNotFoundError as e:
            logger.error(f"Model not found: {str(e)}")
            return {
                "status": "error",
                "message": "Model not found. Please train the model first.",
                "error": str(e)
            }, 404
        
        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": "Login failed",
                "error": str(e)
            }, 500


@api.route("/login-face-verify")
class FaceLoginVerify(Resource):
    @api.expect(verify_login_parser)
    def post(self):
        """
        Login dengan face verification (1:1 - LEBIH CEPAT & AKURAT)
        
        Berbeda dengan /login-face yang melakukan face recognition (1:N),
        endpoint ini melakukan face verification (1:1) untuk user specific.
        
        Keuntungan:
        - ⚡ Lebih cepat (tidak perlu prediksi semua classes)
        - 🎯 Lebih akurat (focused comparison)
        - 💡 Real use case (user input email/username dulu)
        - 🔒 More secure (explicit user claim + verification)
        
        Process:
        1. User input user_id (dari email/username lookup)
        2. Upload foto wajah
        3. Verify apakah wajah cocok dengan user_id
        4. Jika match dan confidence > threshold → generate token
        
        Input:
            - user_id (form): ID user yang ingin login
            - file (file): Face image
        
        Returns:
            - match: True/False (apakah wajah cocok)
            - user_id, name, token (jika success)
            - confidence: Confidence score
        """
        try:
            logger.info("=" * 50)
            logger.info("FACE VERIFICATION LOGIN (1:1)")
            logger.info("=" * 50)
            
            # Parse args
            try:
                args = verify_login_parser.parse_args()
                user_id = args.get('user_id')
                file = args.get('file')
            except Exception as e:
                logger.error(f"Failed to parse args: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Failed to parse request: {str(e)}"
                }, 400
            
            if not user_id:
                return {
                    "status": "error",
                    "message": "user_id is required"
                }, 400
            
            if not file:
                return {
                    "status": "error",
                    "message": "No file provided. Please upload a face image."
                }, 400
            
            logger.info(f"User ID: {user_id}")
            logger.info(f"File: {file.filename}")
            
            # Validasi file
            if not file.filename:
                return {
                    "status": "error",
                    "message": "Invalid file - no filename"
                }, 400
            
            filename = file.filename.lower()
            if not (filename.endswith('.jpg') or filename.endswith('.jpeg') or 
                   filename.endswith('.png') or filename.endswith('.gif')):
                return {
                    "status": "error",
                    "message": f"Invalid file format. Only JPG/PNG allowed"
                }, 400
            
            # Save temporary file
            temp_dir = Path(tempfile.gettempdir())
            temp_path = temp_dir / f"verify_{os.urandom(8).hex()}{Path(file.filename).suffix}"
            
            try:
                file.save(str(temp_path))
                logger.info(f"✓ Temporary file saved: {temp_path}")
                
                # Verify face
                result = auth_service.verify_face(user_id, temp_path)
                
                if result['success']:
                    return {
                        "status": "success",
                        "message": "Face verification successful",
                        "data": {
                            "match": result['match'],
                            "user_id": result['user_id'],
                            "name": result['name'],
                            "email": result['email'],
                            "token": result['token'],
                            "confidence": result['confidence'],
                            "expires_at": result['expires_at']
                        }
                    }, 200
                else:
                    # Return different error codes based on reason
                    if not result.get('match', False):
                        # Face doesn't match (wrong person)
                        return {
                            "status": "error",
                            "message": result['message'],
                            "data": {
                                "match": False,
                                "predicted_user_id": result.get('predicted_user_id'),
                                "claimed_user_id": result.get('claimed_user_id'),
                                "confidence": result.get('confidence')
                            }
                        }, 403  # Forbidden
                    else:
                        # Match but low confidence
                        return {
                            "status": "error",
                            "message": result['message'],
                            "data": {
                                "match": True,
                                "confidence": result.get('confidence'),
                                "required_confidence": result.get('required_confidence')
                            }
                        }, 401  # Unauthorized
                    
            finally:
                # Cleanup
                if temp_path.exists():
                    temp_path.unlink()
                    logger.info(f"✓ Temporary file deleted: {temp_path}")
        
        except FileNotFoundError as e:
            logger.error(f"Model not found: {str(e)}")
            return {
                "status": "error",
                "message": "Model not found. Please train the model first.",
                "error": str(e)
            }, 404
        
        except Exception as e:
            logger.error(f"Verification error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": "Verification failed",
                "error": str(e)
            }, 500


@api.route("/verify")
class VerifyToken(Resource):
    @api.expect(verify_model)
    def post(self):
        """
        Verify token validity dan return user info
        
        Returns user information jika token valid dan belum expired
        """
        try:
            payload = api.payload
            token = payload.get('token')
            
            if not token:
                return {
                    "status": "error",
                    "message": "Token is required"
                }, 400
            
            # Verify token
            user_info = auth_service.verify_token(token)
            
            if user_info:
                return {
                    "status": "success",
                    "message": "Token is valid",
                    "data": user_info
                }, 200
            else:
                return {
                    "status": "error",
                    "message": "Invalid or expired token"
                }, 401
                
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return {
                "status": "error",
                "message": "Verification failed",
                "error": str(e)
            }, 500


@api.route("/logout")
class Logout(Resource):
    @api.expect(logout_model)
    def post(self):
        """
        Logout (deactivate token)
        """
        try:
            payload = api.payload
            token = payload.get('token')
            
            if not token:
                return {
                    "status": "error",
                    "message": "Token is required"
                }, 400
            
            # Deactivate token
            success = auth_service.deactivate_token(token)
            
            if success:
                return {
                    "status": "success",
                    "message": "Logout successful"
                }, 200
            else:
                return {
                    "status": "error",
                    "message": "Logout failed"
                }, 500
                
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return {
                "status": "error",
                "message": "Logout failed",
                "error": str(e)
            }, 500


@api.route("/tokens/<int:user_id>")
class UserTokens(Resource):
    def get(self, user_id):
        """Get all active tokens untuk user"""
        try:
            tokens = auth_service.get_user_active_tokens(user_id)
            
            return {
                "status": "success",
                "message": f"Found {len(tokens)} active tokens",
                "data": tokens
            }, 200
            
        except Exception as e:
            logger.error(f"Failed to get tokens: {str(e)}")
            return {
                "status": "error",
                "message": "Failed to get tokens",
                "error": str(e)
            }, 500
