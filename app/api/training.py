from flask import request
from flask_restx import Api, Resource, Namespace, fields
import logging
from app.services.training_service import TrainingService

logger = logging.getLogger(__name__)

# Create training namespace
training_ns = Namespace('training', description='Training CNN Model Operations')

# Request models
training_request_model = training_ns.model('TrainingRequest', {
    'epochs': fields.Integer(description='[IGNORED] Number of epochs (for backward compatibility)', required=False),
    'batch_size': fields.Integer(description='[IGNORED] Batch size (for backward compatibility)', required=False),
    'validation_split': fields.Float(description='[IGNORED] Validation split (for backward compatibility)', required=False),
    'continue_training': fields.Boolean(description='[IGNORED] Always full rebuild (for backward compatibility)', required=False),
})

# Response models
training_response_model = training_ns.model('TrainingResponse', {
    'success': fields.Boolean(required=True, description='Training success status'),
    'message': fields.String(description='Response message'),
    'data': fields.Raw(description='Training statistics'),
})

error_response_model = training_ns.model('ErrorResponse', {
    'success': fields.Boolean(required=True),
    'message': fields.String(description='Error message'),
    'error': fields.String(description='Error details'),
})


@training_ns.route('/start')
class TrainingStart(Resource):
    """Start training CNN model"""
    
    @training_ns.doc('start_training')
    @training_ns.expect(training_request_model, validate=False)
    @training_ns.response(200, 'Training started successfully', training_response_model)
    @training_ns.response(400, 'Bad request', error_response_model)
    @training_ns.response(500, 'Server error', error_response_model)
    def post(self):
        """
        Build Face Embedding Database (FULL REBUILD)
        
        **IMPORTANT:** This is NOT neural network training!
        - Uses pre-trained InsightFace model
        - Extracts embeddings from all photos in dataset/
        - Always rebuilds entire database (10-30 seconds)
        - No "continue" mode (not applicable for embeddings)
        
        **Parameters (IGNORED - for backward compatibility only):**
        - `epochs`: Not used (no training)
        - `batch_size`: Not used (no batching)
        - `validation_split`: Not used (no validation)
        - `continue_training`: Not used (always full rebuild)
        
        **How it works:**
        1. Scan all folders in `dataset/`
        2. Detect faces in each photo
        3. Extract 512-D embeddings using InsightFace
        4. Save to `models/face_db.npy`
        
        **When to rebuild:**
        - ✅ After adding new users
        - ✅ After uploading new photos
        - ✅ After deleting users (cleanup orphaned data)
        - ✅ Anytime (very fast: 10-30 seconds)
        
        **Returns statistics:**
        - num_data: Total number of images processed
        - num_classes: Number of unique users
        - total_faces: Number of faces detected
        - training_time_seconds: Time taken to build database
        - model_path: Path to saved database
        """
        try:
            logger.info("Face database rebuild request received")
            
            # Get parameters from request (all ignored, for backward compatibility)
            data = request.get_json() or {}
            
            # Log parameters (even though ignored)
            if data:
                logger.info(f"Parameters received (will be ignored): {data}")
            
            logger.info("Building face embedding database (full rebuild)...")
            
            # Initialize service
            service = TrainingService()
            
            # Build database (always full rebuild)
            stats = service.train()
            
            return {
                'success': True,
                'message': 'Face database built successfully',
                'data': stats
            }, 200
            
        except FileNotFoundError as e:
            logger.error(f"Dataset not found: {str(e)}")
            return {
                'success': False,
                'message': 'Dataset not found',
                'error': str(e)
            }, 400
            
        except ValueError as e:
            logger.error(f"Data error: {str(e)}")
            return {
                'success': False,
                'message': 'Invalid data',
                'error': str(e)
            }, 400
            
        except ImportError as e:
            logger.error(f"Missing dependency: {str(e)}")
            return {
                'success': False,
                'message': 'Missing required dependency',
                'error': str(e)
            }, 400
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': 'Training failed',
                'error': str(e)
            }, 500


@training_ns.route('/status')
class TrainingStatus(Resource):
    """Get training status and model information"""
    
    @training_ns.doc('get_training_status')
    def get(self):
        """
        Get information about the trained model (Face Embedding Database)
        
        Returns database statistics if available
        """
        try:
            import json
            from pathlib import Path
            
            models_dir = Path('models')
            
            if not models_dir.exists():
                return {
                    'success': False,
                    'message': 'No trained model found',
                    'data': {
                        'model_available': False
                    }
                }, 200
            
            # Check for embedding database files (NEW system)
            db_file = models_dir / 'face_db.npy'
            meta_file = models_dir / 'face_db.json'
            
            if not db_file.exists() or not meta_file.exists():
                return {
                    'success': False,
                    'message': 'Face database not found. Please build database first.',
                    'data': {
                        'model_available': False
                    }
                }, 200
            
            # Load metadata
            with open(meta_file, 'r') as f:
                meta_data = json.load(f)
            
            return {
                'success': True,
                'message': 'Face database information retrieved',
                'data': {
                    'model_available': True,
                    'model_path': str(db_file),
                    'num_classes': len(meta_data.get('users', [])),
                    'num_data': meta_data.get('total_images', 0),
                    'class_labels': meta_data.get('users', []),
                    'users': meta_data.get('users', []),
                    'total_faces': meta_data.get('total_faces', 0),
                    'embedding_dim': meta_data.get('embedding_dim', 512),
                    'samples_per_user': meta_data.get('samples_per_user', {}),
                    'timestamp': meta_data.get('timestamp', 'N/A')
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Failed to get training status: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to retrieve status',
                'error': str(e)
            }, 500
