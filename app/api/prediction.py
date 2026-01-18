# app/api/prediction.py
from flask_restx import Namespace, Resource
from flask import request
from werkzeug.datastructures import FileStorage
from pathlib import Path
import os
import tempfile
import logging

from app.services.prediction_service import prediction_service

logger = logging.getLogger(__name__)

api = Namespace("face", description="Face Recognition Prediction API")

# File upload parser
upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True, 
                          help='Image file (JPG/PNG) untuk prediction')

@api.route("/predict")
class FacePrediction(Resource):
    @api.expect(upload_parser)
    def post(self):
        """
        Predict user dari gambar wajah
        
        Returns:
            - user_id: ID user yang diprediksi
            - name: Nama user
            - email: Email user
            - confidence: Confidence score (0-100%)
            - all_predictions: Top 3 predictions dengan confidence
        """
        try:
            logger.info("=" * 50)
            logger.info("PREDICTION REQUEST RECEIVED")
            logger.info("=" * 50)
            
            # Parse file dari request
            try:
                args = upload_parser.parse_args()
                file = args.get('file')
                logger.info(f"File parsed: {file}")
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
                    "message": "No file provided. Please upload an image file."
                }, 400
            
            # Validasi file type
            if not file.filename:
                logger.warning("File has no filename")
                return {
                    "status": "error",
                    "message": "Invalid file - no filename"
                }, 400
            
            logger.info(f"Received file: {file.filename}")
            
            filename = file.filename.lower()
            if not (filename.endswith('.jpg') or filename.endswith('.jpeg') or 
                   filename.endswith('.png') or filename.endswith('.gif')):
                logger.warning(f"Invalid file format: {filename}")
                return {
                    "status": "error",
                    "message": f"Invalid file format: {filename}. Only JPG/PNG allowed"
                }, 400
            
            logger.info(f"File validation passed: {filename}")
            
            # Save temporary file untuk prediction
            temp_dir = Path(tempfile.gettempdir())
            temp_path = temp_dir / f"predict_{os.urandom(8).hex()}{Path(file.filename).suffix}"
            
            try:
                file.save(str(temp_path))
                logger.info(f"✓ Temporary file saved: {temp_path}")
                logger.info(f"  File size: {temp_path.stat().st_size} bytes")
                
                # Run prediction
                logger.info("Running prediction...")
                result = prediction_service.predict(temp_path)
                
                logger.info(f"✓ Prediction successful: {result['name']} ({result['confidence']}%)")
                
                return {
                    "status": "success",
                    "message": "Prediction successful",
                    "data": result
                }, 200
                
            finally:
                # Cleanup temporary file
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
        
        except ImportError as e:
            logger.error(f"Missing dependency: {str(e)}")
            return {
                "status": "error",
                "message": "Missing required dependencies",
                "error": str(e)
            }, 500
        
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": "Prediction failed",
                "error": str(e)
            }, 500


@api.route("/model-info")
class ModelInfo(Resource):
    def get(self):
        """Get current model information dan status"""
        try:
            info = prediction_service.get_model_info()
            
            if info.get('loaded'):
                return {
                    "status": "success",
                    "message": "Model is loaded and ready",
                    "data": info
                }, 200
            else:
                return {
                    "status": "error",
                    "message": "Model not loaded",
                    "data": info
                }, 404
        
        except Exception as e:
            logger.error(f"Failed to get model info: {str(e)}")
            return {
                "status": "error",
                "message": "Failed to get model information",
                "error": str(e)
            }, 500
