from flask import request
from flask_restx import Api, Resource, Namespace, fields
import logging
from app.services.training_service import TrainingService

logger = logging.getLogger(__name__)

# Create training namespace
training_ns = Namespace('training', description='Training CNN Model Operations')

# Request models
training_request_model = training_ns.model('TrainingRequest', {
    'epochs': fields.Integer(description='Number of epochs (default: 50)', required=False),
    'batch_size': fields.Integer(description='Batch size (default: 16)', required=False),
    'validation_split': fields.Float(description='Validation split ratio (default: 0.2)', required=False),
    'continue_training': fields.Boolean(description='Continue training from existing model (default: False)', required=False),
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
        Start CNN model training
        
        **Parameters:**
        - `epochs`: Number of epochs (default: 50)
        - `batch_size`: Batch size per iteration (default: 16)
        - `validation_split`: Validation data ratio (default: 0.2)
        - `continue_training`: True = lanjut training model existing, False = training baru (default: False)
        
        **Returns training statistics:**
        - num_data: Total number of training images
        - num_classes: Number of unique users
        - test_accuracy: Model accuracy on test set
        - test_loss: Model loss on test set
        - training_time_seconds: Total training time in seconds
        - epochs_trained: Number of epochs trained
        - model_path: Path to saved model
        """
        try:
            logger.info("Training request received")
            
            # Get parameters from request body
            data = request.get_json() or {}
            epochs = data.get('epochs', 50)
            batch_size = data.get('batch_size', 16)
            validation_split = data.get('validation_split', 0.2)
            continue_training = data.get('continue_training', False)
            
            logger.info(f"Training params: epochs={epochs}, batch_size={batch_size}, "
                       f"validation_split={validation_split}, continue_training={continue_training}")
            
            # Initialize service
            service = TrainingService()
            
            # Run training
            stats = service.train(
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                continue_training=continue_training
            )
            
            return {
                'success': True,
                'message': 'Training completed successfully',
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
                    'model_available': False
                }, 200
            
            # Check for embedding database files (NEW system)
            db_file = models_dir / 'face_db.npy'
            meta_file = models_dir / 'face_db.json'
            
            if not db_file.exists() or not meta_file.exists():
                return {
                    'success': False,
                    'message': 'Face database not found. Please build database first.',
                    'model_available': False
                }, 200
            
            # Load metadata
            with open(meta_file, 'r') as f:
                meta_data = json.load(f)
            
            return {
                'success': True,
                'message': 'Face database information retrieved',
                'model_available': True,
                'accuracy_metrics': {
                    'model': meta_data.get('model', 'InsightFace'),
                    'embedding_dim': meta_data.get('embedding_dim', 512),
                    'timestamp': meta_data.get('timestamp', 'N/A')
                },
                'num_classes': len(meta_data.get('users', [])),
                'class_labels': meta_data.get('users', []),
                'total_faces': meta_data.get('total_faces', 0),
                'total_images': meta_data.get('total_images', 0),
                'samples_per_user': meta_data.get('samples_per_user', {})
            }, 200
            
        except Exception as e:
            logger.error(f"Failed to get training status: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to retrieve status',
                'error': str(e)
            }, 500
