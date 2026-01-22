# app/services/prediction_service.py
import json
import numpy as np
from pathlib import Path
import logging
import warnings
from PIL import Image

# Suppress warnings
warnings.filterwarnings('ignore')

from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity

from app.utils.db import get_db_connection, get_db_cursor

logger = logging.getLogger(__name__)

class PredictionService:
    """Service untuk face recognition prediction menggunakan InsightFace"""
    
    def __init__(self):
        self.models_dir = Path('models')
        self.db_path = self.models_dir / 'face_db.npy'
        self.meta_path = self.models_dir / 'face_db.json'
        
        self.face_app = None
        self.face_db = None
        self.meta = None
        self.is_loaded = False
    
    def load_model(self):
        """Load face database dan InsightFace model"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Face database not found at {self.db_path}. Please train model first.")
        
        if not self.meta_path.exists():
            raise FileNotFoundError(f"Metadata not found at {self.meta_path}. Please train model first.")
        
        try:
            # Load InsightFace model
            logger.info("Loading InsightFace model (buffalo_l)...")
            
            # Suppress verbose output
            import logging as log
            log.getLogger('insightface').setLevel(log.ERROR)
            
            self.face_app = FaceAnalysis(name="buffalo_l")
            self.face_app.prepare(ctx_id=-1)  # CPU mode
            logger.info("✓ InsightFace model loaded successfully")
            
            # Load face database
            logger.info(f"Loading face database from {self.db_path}...")
            self.face_db = np.load(self.db_path, allow_pickle=True)
            logger.info(f"✓ Face database loaded: {len(self.face_db)} embeddings")
            
            # Load metadata
            with open(self.meta_path, 'r') as f:
                self.meta = json.load(f)
            logger.info(f"✓ Metadata loaded: {len(self.meta.get('users', []))} users")
            
            self.is_loaded = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}", exc_info=True)
            raise
    
    def predict(self, image_path):
        """
        Predict user dari gambar menggunakan cosine similarity
        
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
            # Load and process image
            logger.info(f"Processing image: {image_path}")
            img = np.array(Image.open(image_path).convert("RGB"))
            
            # Detect face and extract embedding
            logger.info("Detecting face and extracting embedding...")
            faces = self.face_app.get(img)
            
            if len(faces) == 0:
                raise ValueError("No face detected in image")
            
            # Get embedding dari wajah pertama
            query_embedding = faces[0].embedding.reshape(1, -1)
            logger.info(f"✓ Face detected, embedding extracted (dim: {query_embedding.shape[1]})")
            
            # Calculate cosine similarity with all database embeddings
            logger.info("Calculating cosine similarities...")
            similarities = []
            
            for item in self.face_db:
                user_id = item["id"]
                db_embedding = item["embedding"].reshape(1, -1)
                
                # Cosine similarity
                similarity = cosine_similarity(query_embedding, db_embedding)[0][0]
                
                similarities.append({
                    'user_id': user_id,
                    'similarity': float(similarity)
                })
            
            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Get top prediction
            if not similarities:
                raise ValueError("No embeddings in database for matching")
            
            top_match = similarities[0]
            predicted_label = top_match['user_id']
            top_similarity = top_match['similarity']
            
            # Convert cosine similarity [0, 1] to confidence [0, 100]
            confidence_percentage = top_similarity * 100
            
            logger.info(f"Prediction: user_id={predicted_label}, similarity={top_similarity:.4f}, confidence={confidence_percentage:.2f}%")
            
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
            
            for match in similarities[:3]:  # Top 3
                user_id = match['user_id']
                similarity = match['similarity']
                conf_pct = similarity * 100
                
                # Get user info
                conn = get_db_connection()
                u = conn.execute(
                    "SELECT id, name FROM users WHERE id = ?",
                    (int(user_id),)
                ).fetchone()
                conn.close()
                
                user_name = dict(u)['name'] if u else f'User {user_id}'
                
                all_predictions.append({
                    'user_id': int(user_id),
                    'name': user_name,
                    'confidence': round(conf_pct, 2),
                    'cosine_similarity': round(similarity, 4)
                })
            
            # Prepare result
            result = {
                'user_id': user_data['id'],
                'name': user_data['name'],
                'email': user_data.get('email', ''),
                'confidence': round(confidence_percentage, 2),
                'cosine_similarity': round(top_similarity, 4),
                'all_predictions': all_predictions,
                'method': 'InsightFace + Cosine Similarity'
            }
            
            logger.info(f"Prediction result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}", exc_info=True)
            raise
    
    def extract_embedding(self, image_path):
        """
        Extract face embedding dari image (tanpa prediksi)
        Digunakan untuk face verification (1:1) yang lebih cepat
        
        Args:
            image_path: Path ke image file
            
        Returns:
            numpy.ndarray: Face embedding (512-D vector)
        """
        # Load model jika belum
        if not self.is_loaded:
            self.load_model()
        
        try:
            # Load and process image
            logger.info(f"Extracting embedding from: {image_path}")
            img = np.array(Image.open(image_path).convert("RGB"))
            
            # Detect face and extract embedding
            faces = self.face_app.get(img)
            
            if len(faces) == 0:
                raise ValueError("No face detected in image")
            
            if len(faces) > 1:
                logger.warning(f"Multiple faces detected ({len(faces)}), using the first one")
            
            # Get embedding dari wajah pertama
            embedding = faces[0].embedding
            logger.info(f"✓ Embedding extracted (dim: {embedding.shape[0]})")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to extract embedding: {str(e)}", exc_info=True)
            raise
    
    def verify_face_with_user(self, image_path, user_id, similarity_threshold=0.7):
        """
        Verify face dengan specific user menggunakan PostgreSQL pgvector (1:1)
        LEBIH CEPAT daripada predict() karena hanya compare dengan 1 user
        
        Args:
            image_path: Path ke image file
            user_id: ID user yang ingin diverifikasi
            similarity_threshold: Minimum similarity (default: 0.7)
            
        Returns:
            dict: {
                'match': bool,
                'user_id': int,
                'name': str,
                'email': str,
                'confidence': float,
                'similarity': float
            }
        """
        try:
            logger.info("=" * 50)
            logger.info(f"FACE VERIFICATION (1:1) - User ID: {user_id}")
            logger.info("=" * 50)
            
            # Extract embedding dari uploaded image
            query_embedding = self.extract_embedding(image_path)
            logger.info(f"Query embedding shape: {query_embedding.shape}")
            
            # Convert numpy array to list for PostgreSQL
            embedding_list = query_embedding.tolist()
            
            # Call PostgreSQL function verify_face()
            with get_db_connection() as conn:
                cursor = get_db_cursor(conn)
                
                logger.info(f"Calling PostgreSQL verify_face() function...")
                logger.info(f"User ID: {user_id}, Threshold: {similarity_threshold}")
                
                cursor.execute(
                    "SELECT * FROM verify_face(%s::vector, %s, %s)",
                    (embedding_list, user_id, similarity_threshold)
                )
                result = cursor.fetchone()
            
            if not result:
                logger.warning(f"No result from verify_face() - user might not have embeddings")
                return {
                    'match': False,
                    'user_id': user_id,
                    'name': None,
                    'email': None,
                    'confidence': 0.0,
                    'similarity': 0.0,
                    'message': 'User has no face embeddings in database'
                }
            
            match = result['match']
            similarity = float(result['similarity'])
            confidence = similarity * 100  # Convert to percentage
            
            logger.info(f"Verification result:")
            logger.info(f"  Match: {match}")
            logger.info(f"  Similarity: {similarity:.4f}")
            logger.info(f"  Confidence: {confidence:.2f}%")
            logger.info(f"  Threshold: {similarity_threshold}")
            
            return {
                'match': match,
                'user_id': user_id,
                'name': result['user_name'],
                'email': result['user_email'],
                'confidence': round(confidence, 2),
                'similarity': round(similarity, 4),
                'threshold': similarity_threshold,
                'method': 'PostgreSQL pgvector (1:1)'
            }
            
        except Exception as e:
            logger.error(f"Face verification failed: {str(e)}", exc_info=True)
            raise
    
    def get_model_info(self):
        """Get model information"""
        if not self.is_loaded:
            try:
                self.load_model()
            except Exception as e:
                return {
                    'loaded': False,
                    'error': str(e),
                    'num_users': 0,
                    'total_faces': 0,
                    'users': []  # Empty array untuk prevent undefined error
                }
        
        try:
            users = self.meta.get('users', [])
            
            return {
                'loaded': True,
                'database_path': str(self.db_path),
                'num_users': len(users),
                'total_faces': self.meta.get('total_faces', 0),
                'total_images': self.meta.get('total_images', 0),
                'embedding_dim': self.meta.get('embedding_dim', 512),
                'model': self.meta.get('model', 'InsightFace'),
                'training_date': self.meta.get('timestamp', 'N/A'),
                'users': users,  # Array of user IDs
                'samples_per_user': self.meta.get('samples_per_user', {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get model info: {str(e)}")
            return {
                'loaded': False,
                'error': str(e),
                'num_users': 0,
                'total_faces': 0,
                'users': []  # Empty array untuk prevent undefined error
            }


# Global instance
prediction_service = PredictionService()
