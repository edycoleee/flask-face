# app/services/auth_service.py
import uuid
import logging
from datetime import datetime, timedelta
from pathlib import Path

from app.utils.db import get_db_connection
from app.services.prediction_service import prediction_service

logger = logging.getLogger(__name__)

class AuthService:
    """Service untuk face recognition authentication"""
    
    def __init__(self, confidence_threshold=70.0, token_expiry_hours=24):
        """
        Initialize auth service
        
        Args:
            confidence_threshold: Minimum confidence untuk login (default: 70%)
            token_expiry_hours: Token expiry dalam jam (default: 24 jam)
        """
        self.confidence_threshold = confidence_threshold
        self.token_expiry_hours = token_expiry_hours
    
    def login_with_face(self, image_path):
        """
        Login menggunakan face recognition
        
        Args:
            image_path: Path ke gambar wajah
            
        Returns:
            dict: {
                'success': bool,
                'user_id': int,
                'name': str,
                'token': str,
                'confidence': float,
                'expires_at': str
            }
        """
        try:
            logger.info("=" * 50)
            logger.info("FACE LOGIN ATTEMPT")
            logger.info("=" * 50)
            
            # Run face prediction
            logger.info(f"Processing image: {image_path}")
            prediction_result = prediction_service.predict(image_path)
            
            user_id = prediction_result['user_id']
            name = prediction_result['name']
            email = prediction_result.get('email', '')
            confidence = prediction_result['confidence']
            
            logger.info(f"Prediction: {name} (ID: {user_id})")
            logger.info(f"Confidence: {confidence}%")
            logger.info(f"Threshold: {self.confidence_threshold}%")
            
            # Check confidence threshold
            if confidence < self.confidence_threshold:
                logger.warning(f"❌ Confidence too low: {confidence}% < {self.confidence_threshold}%")
                return {
                    'success': False,
                    'message': f'Confidence too low: {confidence}%. Required: {self.confidence_threshold}%',
                    'confidence': confidence,
                    'required_confidence': self.confidence_threshold
                }
            
            # Generate UUID token
            token = str(uuid.uuid4())
            logger.info(f"✓ Generating token: {token}")
            
            # Calculate expiry
            created_at = datetime.now()
            expires_at = created_at + timedelta(hours=self.token_expiry_hours)
            
            # Save token to database
            conn = get_db_connection()
            try:
                conn.execute('''
                    INSERT INTO auth_tokens (user_id, token, confidence, expires_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, token, confidence, expires_at.isoformat()))
                conn.commit()
                logger.info("✓ Token saved to database")
            finally:
                conn.close()
            
            logger.info("=" * 50)
            logger.info("✅ LOGIN SUCCESSFUL")
            logger.info(f"User: {name} (ID: {user_id})")
            logger.info(f"Token: {token}")
            logger.info(f"Expires: {expires_at.isoformat()}")
            logger.info("=" * 50)
            
            return {
                'success': True,
                'user_id': user_id,
                'name': name,
                'email': email,
                'token': token,
                'confidence': confidence,
                'created_at': created_at.isoformat(),
                'expires_at': expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}", exc_info=True)
            raise
    
    def verify_token(self, token):
        """
        Verify token dan return user info
        
        Args:
            token: UUID token
            
        Returns:
            dict: User info jika valid, None jika invalid
        """
        try:
            conn = get_db_connection()
            
            # Get token info
            result = conn.execute('''
                SELECT t.*, u.name, u.email
                FROM auth_tokens t
                JOIN users u ON t.user_id = u.id
                WHERE t.token = ? AND t.is_active = 1
            ''', (token,)).fetchone()
            
            conn.close()
            
            if not result:
                logger.warning(f"Token not found or inactive: {token}")
                return None
            
            token_data = dict(result)
            
            # Check expiry
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            if datetime.now() > expires_at:
                logger.warning(f"Token expired: {token}")
                # Deactivate expired token
                self.deactivate_token(token)
                return None
            
            return {
                'user_id': token_data['user_id'],
                'name': token_data['name'],
                'email': token_data['email'],
                'confidence': token_data['confidence'],
                'created_at': token_data['created_at'],
                'expires_at': token_data['expires_at']
            }
            
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return None
    
    def deactivate_token(self, token):
        """Deactivate token (logout)"""
        try:
            conn = get_db_connection()
            conn.execute('''
                UPDATE auth_tokens
                SET is_active = 0
                WHERE token = ?
            ''', (token,))
            conn.commit()
            conn.close()
            logger.info(f"Token deactivated: {token}")
            return True
        except Exception as e:
            logger.error(f"Failed to deactivate token: {str(e)}")
            return False
    
    def get_user_active_tokens(self, user_id):
        """Get all active tokens untuk user"""
        try:
            conn = get_db_connection()
            results = conn.execute('''
                SELECT token, confidence, created_at, expires_at
                FROM auth_tokens
                WHERE user_id = ? AND is_active = 1
                ORDER BY created_at DESC
            ''', (user_id,)).fetchall()
            conn.close()
            
            tokens = []
            for row in results:
                token_data = dict(row)
                # Check if expired
                expires_at = datetime.fromisoformat(token_data['expires_at'])
                if datetime.now() <= expires_at:
                    tokens.append(token_data)
                else:
                    # Auto-deactivate expired token
                    self.deactivate_token(token_data['token'])
            
            return tokens
            
        except Exception as e:
            logger.error(f"Failed to get user tokens: {str(e)}")
            return []
    
    def cleanup_expired_tokens(self):
        """Cleanup all expired tokens"""
        try:
            conn = get_db_connection()
            now = datetime.now().isoformat()
            result = conn.execute('''
                UPDATE auth_tokens
                SET is_active = 0
                WHERE expires_at < ? AND is_active = 1
            ''', (now,))
            count = result.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {count} expired tokens")
            return count
            
        except Exception as e:
            logger.error(f"Failed to cleanup tokens: {str(e)}")
            return 0
    
    def verify_face(self, user_id, image_path):
        """
        Verify face untuk specific user (1:1 verification)
        Lebih cepat dan akurat daripada face recognition (1:N)
        
        Args:
            user_id: ID user yang ingin diverifikasi
            image_path: Path ke gambar wajah
            
        Returns:
            dict: {
                'success': bool,
                'user_id': int,
                'name': str,
                'token': str,
                'confidence': float,
                'match': bool
            }
        """
        try:
            logger.info("=" * 50)
            logger.info("FACE VERIFICATION (1:1)")
            logger.info("=" * 50)
            logger.info(f"User ID: {user_id}")
            
            # Get user info dari database
            conn = get_db_connection()
            user = conn.execute(
                "SELECT id, name, email FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
            conn.close()
            
            if not user:
                logger.warning(f"User not found: {user_id}")
                return {
                    'success': False,
                    'message': f'User ID {user_id} not found',
                    'match': False
                }
            
            user_data = dict(user)
            logger.info(f"Verifying face for: {user_data['name']} (ID: {user_id})")
            
            # Run face prediction
            logger.info(f"Processing image: {image_path}")
            prediction_result = prediction_service.predict(image_path)
            
            predicted_user_id = prediction_result['user_id']
            confidence = prediction_result['confidence']
            
            logger.info(f"Predicted User ID: {predicted_user_id}")
            logger.info(f"Confidence: {confidence}%")
            logger.info(f"Threshold: {self.confidence_threshold}%")
            
            # Check if predicted user matches claimed user
            if predicted_user_id != user_id:
                logger.warning(f"❌ Face does not match! Predicted: {predicted_user_id}, Claimed: {user_id}")
                return {
                    'success': False,
                    'message': f'Face does not match user {user_id}',
                    'match': False,
                    'predicted_user_id': predicted_user_id,
                    'claimed_user_id': user_id,
                    'confidence': confidence
                }
            
            # Check confidence threshold
            if confidence < self.confidence_threshold:
                logger.warning(f"❌ Confidence too low: {confidence}% < {self.confidence_threshold}%")
                return {
                    'success': False,
                    'message': f'Confidence too low: {confidence}%. Required: {self.confidence_threshold}%',
                    'match': True,  # Face matches but low confidence
                    'confidence': confidence,
                    'required_confidence': self.confidence_threshold
                }
            
            # Success! Generate token
            token = str(uuid.uuid4())
            logger.info(f"✓ Face verified! Generating token: {token}")
            
            # Calculate expiry
            created_at = datetime.now()
            expires_at = created_at + timedelta(hours=self.token_expiry_hours)
            
            # Save token
            conn = get_db_connection()
            try:
                conn.execute('''
                    INSERT INTO auth_tokens (user_id, token, confidence, expires_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, token, confidence, expires_at.isoformat()))
                conn.commit()
                logger.info("✓ Token saved to database")
            finally:
                conn.close()
            
            logger.info("=" * 50)
            logger.info("✅ VERIFICATION SUCCESSFUL")
            logger.info(f"User: {user_data['name']} (ID: {user_id})")
            logger.info(f"Token: {token}")
            logger.info(f"Expires: {expires_at.isoformat()}")
            logger.info("=" * 50)
            
            return {
                'success': True,
                'match': True,
                'user_id': user_id,
                'name': user_data['name'],
                'email': user_data['email'],
                'token': token,
                'confidence': confidence,
                'created_at': created_at.isoformat(),
                'expires_at': expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Face verification failed: {str(e)}", exc_info=True)
            raise
    
    def login_with_password(self, email, password):
        """
        Login menggunakan email dan password
        
        Args:
            email: Email user
            password: Password user
            
        Returns:
            dict: {
                'success': bool,
                'user_id': int,
                'name': str,
                'email': str,
                'token': str,
                'expires_at': str
            }
        """
        try:
            logger.info("=" * 50)
            logger.info("PASSWORD LOGIN ATTEMPT")
            logger.info("=" * 50)
            logger.info(f"Email: {email}")
            
            # Get user from database
            conn = get_db_connection()
            user = conn.execute(
                "SELECT id, name, email, password FROM users WHERE email = ?",
                (email,)
            ).fetchone()
            conn.close()
            
            if not user:
                logger.warning(f"❌ User not found: {email}")
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            user_data = dict(user)
            
            # Verify password
            if user_data['password'] != password:
                logger.warning(f"❌ Password mismatch for user: {email}")
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            logger.info(f"✓ Password verified for: {user_data['name']} (ID: {user_data['id']})")
            
            # Generate UUID token
            token = str(uuid.uuid4())
            logger.info(f"✓ Generating token: {token}")
            
            # Calculate expiry
            created_at = datetime.now()
            expires_at = created_at + timedelta(hours=self.token_expiry_hours)
            
            # Save token to database (confidence = 100.0 for password login)
            conn = get_db_connection()
            try:
                conn.execute('''
                    INSERT INTO auth_tokens (user_id, token, confidence, expires_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_data['id'], token, 100.0, expires_at.isoformat()))
                conn.commit()
                logger.info("✓ Token saved to database")
            finally:
                conn.close()
            
            logger.info("=" * 50)
            logger.info("✅ LOGIN SUCCESSFUL")
            logger.info(f"User: {user_data['name']} (ID: {user_data['id']})")
            logger.info(f"Token: {token}")
            logger.info(f"Expires: {expires_at.isoformat()}")
            logger.info("=" * 50)
            
            return {
                'success': True,
                'user_id': user_data['id'],
                'name': user_data['name'],
                'email': user_data['email'],
                'token': token,
                'created_at': created_at.isoformat(),
                'expires_at': expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Password login failed: {str(e)}", exc_info=True)
            raise


# Global instance
auth_service = AuthService(confidence_threshold=70.0, token_expiry_hours=24)
