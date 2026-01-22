import os
import json
import time
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
import warnings
from PIL import Image

# Suppress warnings
warnings.filterwarnings('ignore')

from insightface.app import FaceAnalysis

logger = logging.getLogger(__name__)


class TrainingService:
    """
    Face Embedding based training service
    Builds face embedding database instead of training CNN
    """

    def __init__(self):
        self.dataset_dir = Path("dataset")
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)

        self.db_path = self.models_dir / "face_db.npy"
        self.meta_path = self.models_dir / "face_db.json"

        # MobileFaceNet (very fast, Raspberry Pi friendly)
        # Suppress verbose output
        import logging as log
        log.getLogger('insightface').setLevel(log.ERROR)
        
        self.face_app = FaceAnalysis(name="buffalo_l")
        self.face_app.prepare(ctx_id=-1)   # CPU mode

    # ============================================================
    # BUILD FACE DATABASE
    # ============================================================
    def build_face_database(self):

        embeddings = []
        stats = {}

        total_images = 0
        total_faces = 0

        for person in sorted(self.dataset_dir.iterdir()):
            if not person.is_dir():
                continue

            person_id = person.name
            stats[person_id] = 0

            for img_file in person.iterdir():
                try:
                    img = np.array(Image.open(img_file).convert("RGB"))
                    faces = self.face_app.get(img)

                    if len(faces) == 0:
                        logger.warning(f"No face detected: {img_file}")
                        continue

                    face = faces[0]
                    emb = face.embedding

                    embeddings.append({
                        "id": person_id,
                        "embedding": emb
                    })

                    stats[person_id] += 1
                    total_faces += 1

                except Exception as e:
                    logger.warning(f"Failed {img_file}: {e}")

                total_images += 1

        if total_faces == 0:
            raise RuntimeError("No faces detected in dataset")

        # Save numpy database
        np.save(self.db_path, embeddings)

        # Save metadata
        meta = {
            "users": list(stats.keys()),
            "samples_per_user": stats,
            "total_images": total_images,
            "total_faces": total_faces,
            "embedding_dim": len(embeddings[0]["embedding"]),
            "model": "InsightFace MobileFaceNet (buffalo_l)",
            "timestamp": datetime.now().isoformat()
        }

        with open(self.meta_path, "w") as f:
            json.dump(meta, f, indent=2)

        logger.info("Face embedding database created")
        logger.info(f"Users: {len(stats)}")
        logger.info(f"Total faces: {total_faces}")

        return meta
    
    # ============================================================
    # TRAIN (Alias for build_face_database untuk backward compatibility)
    # ============================================================
    def train(self, epochs=None, batch_size=None, validation_split=None, continue_training=None):
        """
        Build face embedding database (Full Rebuild)
        
        NOTE: Ini BUKAN training neural network!
        - Model InsightFace sudah pre-trained
        - Kita hanya ekstrak embeddings dari foto
        - Selalu rebuild SEMUA (10-30 detik)
        - Tidak ada "continue" training (not applicable)
        
        Args (diabaikan untuk backward compatibility):
            epochs: Tidak digunakan (no training epochs)
            batch_size: Tidak digunakan (no batching)
            validation_split: Tidak digunakan (no validation)
            continue_training: Tidak digunakan (always full rebuild)
        
        Returns:
            dict: Statistics (num_data, num_classes, etc.)
        """
        import time
        start_time = time.time()
        
        logger.info("=" * 50)
        logger.info("BUILDING FACE EMBEDDING DATABASE")
        logger.info("=" * 50)
        logger.info("Method: InsightFace (Pre-trained MobileFaceNet)")
        logger.info("Mode: FULL REBUILD (always fresh)")
        logger.info("No training needed - extracting embeddings only")
        logger.info("=" * 50)
        
        # Build database
        meta = self.build_face_database()
        
        training_time = time.time() - start_time
        
        # Return stats in format yang sama dengan training lama
        stats = {
            'num_data': meta['total_images'],
            'num_classes': len(meta['users']),
            'class_labels': meta['users'],
            'test_accuracy': 1.0,  # N/A untuk embedding-based
            'test_loss': 0.0,  # N/A untuk embedding-based
            'training_time_seconds': training_time,
            'training_time_minutes': round(training_time / 60, 2),
            'epochs_trained': 0,  # No epochs in embedding extraction
            'model_path': str(self.db_path),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("\n" + "=" * 50)
        logger.info("DATABASE BUILD COMPLETE")
        logger.info("=" * 50)
        logger.info(f"Total images: {meta['total_images']}")
        logger.info(f"Total faces detected: {meta['total_faces']}")
        logger.info(f"Number of users: {len(meta['users'])}")
        logger.info(f"Embedding dimension: {meta['embedding_dim']}")
        logger.info(f"Time taken: {round(training_time / 60, 2)} minutes")
        logger.info(f"Database saved: {self.db_path}")
        logger.info("=" * 50 + "\n")
        
        return stats


    # ============================================================
    # LOAD DATABASE
    # ============================================================
    def load_database(self):
        if not self.db_path.exists():
            raise FileNotFoundError("Face database not found, run training first")

        return np.load(self.db_path, allow_pickle=True)


    # ============================================================
    # RECOGNIZE
    # ============================================================
    def recognize(self, image, threshold=0.7):
        """
        image: numpy RGB image
        """
        from sklearn.metrics.pairwise import cosine_similarity

        db = self.load_database()
        faces = self.face_app.get(image)

        if not faces:
            return None, 0.0

        emb = faces[0].embedding.reshape(1, -1)

        best_name = "unknown"
        best_score = 0

        for item in db:
            score = cosine_similarity(
                emb,
                item["embedding"].reshape(1, -1)
            )[0][0]

            if score > best_score:
                best_score = score
                best_name = item["id"]

        if best_score < threshold:
            return "unknown", float(best_score)

        return best_name, float(best_score)

    # ============================================================
    # BUILD EMBEDDINGS FOR SINGLE USER (INCREMENTAL)
    # ============================================================
    def build_embeddings_for_user(self, user_id):
        """
        Build face embeddings for a single user and save to PostgreSQL
        
        This is INCREMENTAL - only processes one user, very fast (1-3 seconds)
        
        Args:
            user_id: User ID to build embeddings for
            
        Returns:
            dict: Statistics (faces_processed, embeddings_created, etc.)
        """
        import time
        from app.utils.db import get_db_connection
        
        start_time = time.time()
        
        logger.info("=" * 50)
        logger.info(f"BUILDING EMBEDDINGS FOR USER {user_id}")
        logger.info("=" * 50)
        logger.info("Method: InsightFace (Incremental)")
        logger.info("=" * 50)
        
        # Check if user folder exists
        user_folder = self.dataset_dir / str(user_id)
        if not user_folder.exists() or not user_folder.is_dir():
            raise FileNotFoundError(f"Dataset folder for user {user_id} not found: {user_folder}")
        
        # Process all images for this user
        embeddings_created = 0
        faces_processed = 0
        
        # Delete old embeddings for this user first
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM face_embeddings WHERE user_id = %s", (user_id,))
                deleted_count = cur.rowcount
                logger.info(f"Deleted {deleted_count} old embeddings for user {user_id}")
        
        # Extract new embeddings
        for img_file in user_folder.iterdir():
            if not img_file.is_file():
                continue
                
            try:
                # Load image
                img = np.array(Image.open(img_file).convert("RGB"))
                faces = self.face_app.get(img)
                
                if len(faces) == 0:
                    logger.warning(f"No face detected: {img_file}")
                    continue
                
                # Get embedding from first face
                face = faces[0]
                embedding = face.embedding.tolist()  # Convert to list for PostgreSQL
                
                # Save to PostgreSQL
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO face_embeddings (user_id, embedding, photo_path, created_at)
                            VALUES (%s, %s, %s, NOW())
                            """,
                            (user_id, embedding, str(img_file))
                        )
                
                embeddings_created += 1
                faces_processed += 1
                logger.info(f"✓ Processed: {img_file.name}")
                
            except Exception as e:
                logger.warning(f"Failed to process {img_file}: {e}")
        
        if faces_processed == 0:
            raise ValueError(f"No faces detected for user {user_id}")
        
        processing_time = time.time() - start_time
        
        logger.info("\n" + "=" * 50)
        logger.info(f"INCREMENTAL BUILD COMPLETE FOR USER {user_id}")
        logger.info("=" * 50)
        logger.info(f"Faces processed: {faces_processed}")
        logger.info(f"Embeddings created: {embeddings_created}")
        logger.info(f"Time taken: {processing_time:.2f} seconds")
        logger.info("=" * 50 + "\n")
        
        return {
            'user_id': user_id,
            'faces_processed': faces_processed,
            'embeddings_created': embeddings_created,
            'processing_time_seconds': round(processing_time, 2),
            'timestamp': datetime.now().isoformat()
        }
