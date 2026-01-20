# app/services/prediction_service.py
import os
import json
import numpy as np
from pathlib import Path
import logging

try:
    from tensorflow import keras
    from tensorflow.keras.preprocessing.image import load_img, img_to_array
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    keras = None
    load_img = None
    img_to_array = None

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

from app.utils.db import get_db_connection

logger = logging.getLogger(__name__)

class PredictionService:
    """Service untuk face recognition prediction"""
    
    def __init__(self):
        self.models_dir = Path('models')
        self.model_path = self.models_dir / 'model.h5'
        self.label_map_path = self.models_dir / 'label_map.json'
        
        self.model = None
        self.label_map = None
        self.is_loaded = False
    
    def load_model(self):
        """Load trained model dan label mapping"""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is not installed. Install with: pip install tensorflow keras")
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}. Please train model first.")
        
        if not self.label_map_path.exists():
            raise FileNotFoundError(f"Label map not found at {self.label_map_path}. Please train model first.")
        
        try:
            # Load model
            logger.info(f"Loading model from {self.model_path}...")
            self.model = keras.models.load_model(str(self.model_path))
            logger.info("✓ Model loaded successfully")
            
            # Load label mapping
            with open(self.label_map_path, 'r') as f:
                self.label_map = json.load(f)
            logger.info(f"✓ Label map loaded: {len(self.label_map)} classes")
            
            # Validate that all users in label_map exist in database
            self._validate_label_map()
            
            self.is_loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}", exc_info=True)
            raise
    
    def _validate_label_map(self):
        """Validate that all users in label_map exist in database"""
        conn = get_db_connection()
        
        # Get all valid user IDs from database
        valid_users = conn.execute("SELECT id FROM users").fetchall()
        valid_ids = {str(row['id']) for row in valid_users}
        
        # Check label_map users
        model_users = set(self.label_map.values())
        
        # Find users in model but not in database
        orphaned_users = model_users - valid_ids
        
        conn.close()
        
        if orphaned_users:
            error_msg = (
                f"❌ MODEL-DATABASE MISMATCH DETECTED!\n"
                f"Model has users that don't exist in database: {', '.join(sorted(orphaned_users))}\n"
                f"Database users: {', '.join(sorted(valid_ids))}\n"
                f"Model users: {', '.join(sorted(model_users))}\n\n"
                f"This happens when:\n"
                f"1. Users were deleted after model training\n"
                f"2. Model was trained with orphaned dataset folders\n\n"
                f"SOLUTION: Retrain the model\n"
                f"1. Verify dataset: python verify_dataset.py\n"
                f"2. Retrain model: POST /api/training/start"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def preprocess_image(self, image_path):
        """Preprocess image untuk prediction"""
        if not PIL_AVAILABLE:
            raise ImportError("Pillow is not installed. Install with: pip install Pillow")
        
        try:
            # Load dan resize ke 224x224
            img = load_img(str(image_path), target_size=(224, 224))
            img_array = img_to_array(img)
            
            # Normalize ke [0, 1]
            img_array = img_array / 255.0
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Failed to preprocess image: {str(e)}")
            raise
    
    def predict(self, image_path):
        """
        Predict user dari gambar
        
        Returns:
            dict: {
                'user_id': int,
                'name': str,
                'email': str,
                'confidence': float,
                'all_predictions': list
            }
        """
        # Load model jika belum
        if not self.is_loaded:
            self.load_model()
        
        try:
            # Preprocess image
            logger.info(f"Processing image: {image_path}")
            img_array = self.preprocess_image(image_path)
            
            # Predict
            logger.info("Running prediction...")
            predictions = self.model.predict(img_array, verbose=0)
            
            # Get probabilities untuk setiap class
            probabilities = predictions[0]
            
            # Get top prediction
            top_idx = np.argmax(probabilities)
            top_confidence = float(probabilities[top_idx])
            predicted_label = self.label_map[str(top_idx)]
            
            logger.info(f"Prediction: user_id={predicted_label}, confidence={top_confidence:.4f}")
            
            # Get user details dari database
            conn = get_db_connection()
            user = conn.execute(
                "SELECT id, name, email FROM users WHERE id = ?",
                (int(predicted_label),)
            ).fetchone()
            conn.close()
            
            if not user:
                logger.warning(f"User {predicted_label} not found in database")
                user_data = {
                    'id': int(predicted_label),
                    'name': f'User {predicted_label}',
                    'email': 'unknown@example.com'
                }
            else:
                user_data = dict(user)
            
            # Prepare all predictions (top 3)
            all_predictions = []
            top_indices = np.argsort(probabilities)[::-1][:3]  # Top 3
            
            for idx in top_indices:
                label = self.label_map[str(idx)]
                conf = float(probabilities[idx])
                
                # Get user info
                conn = get_db_connection()
                u = conn.execute(
                    "SELECT id, name FROM users WHERE id = ?",
                    (int(label),)
                ).fetchone()
                conn.close()
                
                user_name = dict(u)['name'] if u else f'User {label}'
                
                all_predictions.append({
                    'user_id': int(label),
                    'name': user_name,
                    'confidence': round(conf * 100, 2)
                })
            
            # Prepare result
            result = {
                'user_id': user_data['id'],
                'name': user_data['name'],
                'email': user_data.get('email', ''),
                'confidence': round(top_confidence * 100, 2),
                'all_predictions': all_predictions
            }
            
            logger.info(f"Prediction result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}", exc_info=True)
            raise
    
    def get_model_info(self):
        """Get model information"""
        if not self.is_loaded:
            try:
                self.load_model()
            except Exception as e:
                return {
                    'loaded': False,
                    'error': str(e)
                }
        
        try:
            # Get accuracy info if available
            accuracy_path = self.models_dir / 'accuracy.json'
            accuracy_data = {}
            if accuracy_path.exists():
                with open(accuracy_path, 'r') as f:
                    accuracy_data = json.load(f)
            
            return {
                'loaded': True,
                'model_path': str(self.model_path),
                'num_classes': len(self.label_map),
                'classes': list(self.label_map.values()),
                'accuracy': accuracy_data.get('test_accuracy', 'N/A'),
                'training_date': accuracy_data.get('timestamp', 'N/A')
            }
            
        except Exception as e:
            logger.error(f"Failed to get model info: {str(e)}")
            return {
                'loaded': False,
                'error': str(e)
            }


# Global instance
prediction_service = PredictionService()
