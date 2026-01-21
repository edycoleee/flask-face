import os
import json
import time
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models
    from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    tf = None
    keras = None
    layers = None
    models = None
    ImageDataGenerator = None
    load_img = None
    img_to_array = None

try:
    from sklearn.preprocessing import LabelEncoder
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    LabelEncoder = None

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

logger = logging.getLogger(__name__)

class TrainingService:
    """Service untuk training CNN model untuk face recognition"""
    
    def __init__(self):
        self.dataset_dir = Path('dataset')
        self.models_dir = Path('models')
        self.models_dir.mkdir(exist_ok=True)
        
        self.model = None
        self.label_encoder = None
        self.history = None
        self.training_stats = {}
    
    def _validate_dataset(self):
        """Validate dataset matches database users"""
        import sqlite3
        
        # Get valid user IDs from database
        db_path = Path('instance') / 'app.db'
        if not db_path.exists():
            logger.warning("Database not found, skipping validation")
            return
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users ORDER BY id")
        valid_ids = {str(row[0]) for row in cursor.fetchall()}
        conn.close()
        
        # Get dataset folders
        if not self.dataset_dir.exists():
            raise FileNotFoundError(f"Dataset directory not found: {self.dataset_dir}")
        
        dataset_folders = {f.name for f in self.dataset_dir.iterdir() 
                          if f.is_dir() and f.name.isdigit()}
        
        # Check for orphaned folders
        orphaned = dataset_folders - valid_ids
        missing = valid_ids - dataset_folders
        
        logger.info(f"Database users: {len(valid_ids)}")
        logger.info(f"Dataset folders: {len(dataset_folders)}")
        
        if orphaned:
            error_msg = (
                f"❌ ORPHANED FOLDERS DETECTED: {', '.join(sorted(orphaned))}\n"
                f"These folders don't have matching users in database.\n"
                f"This will cause training to fail with wrong number of classes.\n"
                f"Run: python cleanup_dataset.py to fix this issue."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if missing:
            logger.warning(f"Missing folders for users: {', '.join(sorted(missing))}")
        
        logger.info("✓ Dataset validation passed")
    
    def load_dataset(self):
        """Load semua gambar dari dataset folder"""
        images = []
        labels = []
        unique_labels = set()
        
        logger.info(f"Loading dataset from {self.dataset_dir}...")
        
        # Scan semua folder di dataset
        if not self.dataset_dir.exists():
            logger.error(f"Dataset directory not found: {self.dataset_dir}")
            raise FileNotFoundError(f"Dataset directory not found: {self.dataset_dir}")
        
        # Collect all image files and labels
        for user_folder in sorted(self.dataset_dir.iterdir()):
            if user_folder.is_dir():
                user_label = user_folder.name
                unique_labels.add(user_label)
                
                # Load images from user folder
                image_files = list(user_folder.glob('*.jpg')) + \
                             list(user_folder.glob('*.jpeg')) + \
                             list(user_folder.glob('*.png')) + \
                             list(user_folder.glob('*.JPG')) + \
                             list(user_folder.glob('*.gif')) + \
                             list(user_folder.glob('*.PNG'))
                
                logger.info(f"Found {len(image_files)} images for user: {user_label}")
                
                for img_file in image_files:
                    try:
                        # Load and preprocess image
                        img = load_img(str(img_file), target_size=(300, 300))
                        img_array = img_to_array(img)
                        img_array = img_array / 255.0  # Normalize
                        
                        images.append(img_array)
                        labels.append(user_label)
                    except Exception as e:
                        logger.warning(f"Failed to load image {img_file}: {str(e)}")
                        continue
        
        if not images:
            raise ValueError("No valid images found in dataset")
        
        images = np.array(images)
        logger.info(f"Dataset loaded: {len(images)} images, {len(unique_labels)} users")
        
        return images, labels, list(unique_labels)
    
    def preprocess_data(self, images, labels):
        """Preprocess data untuk training"""
        # Encode labels
        self.label_encoder = LabelEncoder()
        encoded_labels = self.label_encoder.fit_transform(labels)
        
        # Convert to one-hot encoding
        num_classes = len(self.label_encoder.classes_)
        labels_encoded = keras.utils.to_categorical(encoded_labels, num_classes)
        
        logger.info(f"Preprocessing complete: {num_classes} classes")
        
        return images, labels_encoded, num_classes
    
    def build_model(self, num_classes):
        """Build CNN model untuk face recognition dengan architecture yang lebih akurat"""
        logger.info("Building improved face recognition model...")
        
        # Load EfficientNetB3 (Top-1 accuracy 81.6% vs B0 77.1%)
        # Input size 300x300 untuk detail lebih baik
        base_model = keras.applications.EfficientNetB3(
            input_shape=(300, 300, 3),
            include_top=False,
            weights='imagenet',
            pooling=None  # We'll add custom pooling
        )
        
        # Fine-tuning strategy: Unfreeze top layers untuk better accuracy
        # Freeze semua layers dulu
        base_model.trainable = False
        
        # Unfreeze top 30 layers untuk fine-tuning (lebih banyak karena B3 lebih dalam)
        # Ini akan memberikan model kemampuan untuk adapt ke face dataset kita
        for layer in base_model.layers[-30:]:
            layer.trainable = True
        
        logger.info(f"  Base model: EfficientNetB3 (ImageNet weights)")
        logger.info(f"  Total layers: {len(base_model.layers)}")
        logger.info(f"  Trainable layers: {sum([1 for l in base_model.layers if l.trainable])}")
        
        # Build model dengan deeper classification head untuk better feature extraction
        model = models.Sequential([
            # Base model
            base_model,
            
            # Global pooling
            layers.GlobalAveragePooling2D(),
            
            # First dense block - extract high-level features
            layers.Dense(512, kernel_regularizer=keras.regularizers.l2(0.01)),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.Dropout(0.5),
            
            # Second dense block - refine features
            layers.Dense(256, kernel_regularizer=keras.regularizers.l2(0.01)),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.Dropout(0.4),
            
            # Third dense block - face-specific features
            layers.Dense(128, kernel_regularizer=keras.regularizers.l2(0.01)),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.Dropout(0.3),
            
            # Output layer
            layers.Dense(num_classes, activation='softmax')
        ])
        
        # Compile dengan optimizer yang lebih baik dan learning rate scheduling
        # Learning rate lebih kecil karena kita fine-tune
        model.compile(
            optimizer=keras.optimizers.Adam(
                learning_rate=0.0001,  # Lower LR untuk fine-tuning
                beta_1=0.9,
                beta_2=0.999,
                epsilon=1e-07
            ),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=2, name='top_2_accuracy')]
        )
        
        logger.info("✓ Enhanced face recognition model built successfully")
        logger.info(f"  Architecture: EfficientNetB3 + Deep Classification Head")
        logger.info(f"  Input size: 300x300 (higher resolution for better accuracy)")
        logger.info(f"  Total parameters: {model.count_params():,}")
        logger.info(f"  Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")
        logger.info(f"  Non-trainable parameters: {sum([tf.size(w).numpy() for w in model.non_trainable_weights]):,}")
        logger.info(f"  Dense layers: 512 → 256 → 128 → {num_classes}")
        
        return model
    
    def train(self, epochs=50, batch_size=16, validation_split=0.2, continue_training=False):
        """
        Train model dengan dataset
        
        Args:
            epochs: Jumlah epoch untuk training
            batch_size: Ukuran batch per iterasi
            validation_split: Rasio validasi (0.2 = 20%)
            continue_training: True = lanjut training model existing, False = training baru
        """
        # Check all required dependencies
        if not TENSORFLOW_AVAILABLE:
            raise ImportError(
                "TensorFlow is not installed. Install with:\n"
                "pip install tensorflow keras"
            )
        if not SKLEARN_AVAILABLE:
            raise ImportError(
                "scikit-learn is not installed. Install with:\n"
                "pip install scikit-learn"
            )
        if not PIL_AVAILABLE:
            raise ImportError(
                "Pillow is not installed. Install with:\n"
                "pip install Pillow"
            )
        
        try:
            start_time = time.time()
            
            # Validate dataset before training
            logger.info("=" * 50)
            logger.info("VALIDATING DATASET")
            logger.info("=" * 50)
            self._validate_dataset()
            
            # Load dataset
            logger.info("=" * 50)
            logger.info("PHASE 4: CNN Model Training")
            logger.info("=" * 50)
            
            images, labels, unique_labels = self.load_dataset()
            num_data = len(images)
            num_classes = len(unique_labels)
            
            # Preprocess
            images, labels_encoded, num_classes = self.preprocess_data(images, labels)
            
            # Check if continue training
            model_path = self.models_dir / 'model.h5'
            if continue_training and model_path.exists():
                logger.info(f"\n🔄 Loading existing model untuk lanjut training...")
                self.model = keras.models.load_model(str(model_path))
                logger.info("✓ Model loaded successfully")
                training_mode = "CONTINUE"
            else:
                logger.info(f"\n🆕 Building new model untuk training fresh...")
                # Build model
                self.model = self.build_model(num_classes)
                training_mode = "NEW"
            
            # Manually split data for validation
            num_train = int(len(images) * (1 - validation_split))
            train_images = images[:num_train]
            train_labels = labels_encoded[:num_train]
            val_images = images[num_train:]
            val_labels = labels_encoded[num_train:]
            
            logger.info(f"Data split:")
            logger.info(f"  Training samples: {len(train_images)}")
            logger.info(f"  Validation samples: {len(val_images)}")
            
            # Data augmentation - only for training data
            datagen = ImageDataGenerator(
                rotation_range=20,
                width_shift_range=0.2,
                height_shift_range=0.2,
                horizontal_flip=True,
                zoom_range=0.2,
                brightness_range=[0.8, 1.2],  # Brightness variation
                fill_mode='nearest'
            )
            
            logger.info(f"\nTraining configuration:")
            logger.info(f"  Mode: {training_mode}")
            logger.info(f"  Epochs: {epochs}")
            logger.info(f"  Batch size: {batch_size}")
            logger.info(f"  Validation split: {validation_split}")
            logger.info(f"  Data augmentation: Enhanced (rotation, shift, flip, zoom, brightness)")
            
            # Enhanced callbacks untuk better training
            callbacks_list = [
                # Early stopping - stop jika tidak ada improvement
                keras.callbacks.EarlyStopping(
                    monitor='val_accuracy',
                    mode='max',
                    patience=15,  # Lebih sabar karena fine-tuning butuh lebih lama
                    restore_best_weights=True,
                    verbose=1
                ),
                # Learning rate reduction - kurangi LR jika stuck
                keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=5,
                    min_lr=1e-7,
                    verbose=1
                ),
                # Model checkpoint - save best model
                keras.callbacks.ModelCheckpoint(
                    filepath=str(self.models_dir / 'best_model.h5'),
                    monitor='val_accuracy',
                    mode='max',
                    save_best_only=True,
                    verbose=1
                ),
                # Custom logger
                TrainingLogger()
            ]
            
            # Train model dengan callback lebih baik
            logger.info("\nStarting training with enhanced architecture...")
            logger.info("  Strategy: Transfer Learning + Fine-Tuning")
            logger.info("  Expected: Higher accuracy but slower training")
            
            self.history = self.model.fit(
                datagen.flow(train_images, train_labels, batch_size=batch_size),
                epochs=epochs,
                validation_data=(val_images, val_labels),
                verbose=1,
                callbacks=callbacks_list
            )
            
            training_time = time.time() - start_time
            
            # Evaluate model
            logger.info("\nEvaluating model...")
            eval_results = self.model.evaluate(images, labels_encoded, verbose=0)
            
            # Unpack results (support both 2 and 3+ metrics)
            test_loss = eval_results[0]
            test_accuracy = eval_results[1]
            test_top_2_accuracy = eval_results[2] if len(eval_results) > 2 else 0.0
            
            # Use best model (from ModelCheckpoint) as final model
            best_model_path = self.models_dir / 'best_model.h5'
            model_path = self.models_dir / 'model.h5'
            
            if best_model_path.exists():
                # Copy best_model.h5 to model.h5 untuk konsistensi
                import shutil
                shutil.copy2(str(best_model_path), str(model_path))
                logger.info(f"✓ Using best model (val_accuracy tertinggi)")
                logger.info(f"  Best model: {best_model_path}")
                logger.info(f"  Copied to: {model_path}")
            else:
                # Fallback: save current model
                self.model.save(str(model_path))
                logger.info(f"Model saved: {model_path}")
            
            # Save label mapping
            label_map = {idx: label for idx, label in enumerate(self.label_encoder.classes_)}
            label_map_path = self.models_dir / 'label_map.json'
            with open(label_map_path, 'w') as f:
                json.dump(label_map, f, indent=2)
            logger.info(f"Label map saved: {label_map_path}")
            
            # Save accuracy metrics
            accuracy_data = {
                'test_loss': float(test_loss),
                'test_accuracy': float(test_accuracy),
                'test_top_2_accuracy': float(test_top_2_accuracy),
                'training_accuracy': float(self.history.history['accuracy'][-1]),
                'training_loss': float(self.history.history['loss'][-1]),
                'validation_accuracy': float(self.history.history['val_accuracy'][-1]),
                'validation_loss': float(self.history.history['val_loss'][-1]),
                'top_2_accuracy': float(self.history.history.get('top_2_accuracy', [0])[-1]),
                'val_top_2_accuracy': float(self.history.history.get('val_top_2_accuracy', [0])[-1]),
                'epochs_trained': len(self.history.history['loss']),
                'best_epoch': len(self.history.history['loss']) - 15,  # Estimate based on early stopping patience
                'model_architecture': 'EfficientNetB3 + Deep Classification Head (300x300)',  
                'timestamp': datetime.now().isoformat()
            }
            accuracy_path = self.models_dir / 'accuracy.json'
            with open(accuracy_path, 'w') as f:
                json.dump(accuracy_data, f, indent=2)
            logger.info(f"Accuracy metrics saved: {accuracy_path}")
            
            # Prepare stats
            self.training_stats = {
                'num_data': num_data,
                'num_classes': num_classes,
                'class_labels': unique_labels,
                'test_accuracy': float(test_accuracy),
                'test_loss': float(test_loss),
                'training_time_seconds': training_time,
                'training_time_minutes': round(training_time / 60, 2),
                'epochs_trained': len(self.history.history['loss']),
                'model_path': str(model_path),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("\n" + "=" * 50)
            logger.info("TRAINING COMPLETE")
            logger.info("=" * 50)
            logger.info(f"Dataset size: {num_data} images")
            logger.info(f"Number of classes: {num_classes}")
            logger.info(f"Test Accuracy: {test_accuracy:.4f}")
            logger.info(f"Test Loss: {test_loss:.4f}")
            logger.info(f"Training Time: {round(training_time / 60, 2)} minutes")
            logger.info("=" * 50 + "\n")
            
            return self.training_stats
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}", exc_info=True)
            raise


# Define TrainingLogger only if TensorFlow is available
if TENSORFLOW_AVAILABLE and keras is not None:
    class TrainingLogger(keras.callbacks.Callback):
        """Custom callback untuk logging epoch progress"""
        
        def on_epoch_end(self, epoch, logs=None):
            logs = logs or {}
            logger.info(
                f"Epoch {epoch + 1}: "
                f"loss={logs.get('loss', 0):.4f}, "
                f"accuracy={logs.get('accuracy', 0):.4f}, "
                f"val_loss={logs.get('val_loss', 0):.4f}, "
                f"val_accuracy={logs.get('val_accuracy', 0):.4f}"
            )
else:
    class TrainingLogger:
        """Placeholder for TrainingLogger when TensorFlow not available"""
        pass
