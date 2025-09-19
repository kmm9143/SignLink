# DESCRIPTION: This script defines and trains a CNN model for ASL image classification.
# LANGUAGE:    PYTHON

from preprocess import load_and_preprocess_dataset, download_and_extract_dataset
from data_augmentation import tf_augment_image
import tensorflow as tf
import os

# ---------------- Configurations ----------------
DATASET_ROOT = r"C:\Datasets\ASL_Alphabet"
DATASET_DIR = r"C:\Datasets\ASL_Alphabet\asl_alphabet_train\asl_alphabet_train"
USE_AUGMENTATION = True
BATCH_SIZE = 32
EPOCHS = 5

# ---------------- Download dataset if missing ----------------
download_and_extract_dataset("grassknoted/asl-alphabet", DATASET_ROOT)

# ---------------- Load and preprocess dataset ----------------
train_ds, val_ds, class_names = load_and_preprocess_dataset(DATASET_DIR)

# ---------------- Apply data augmentation ----------------
if USE_AUGMENTATION:
    train_ds = train_ds.map(tf_augment_image, num_parallel_calls=tf.data.AUTOTUNE)

# ---------------- Batch and prefetch ----------------
train_ds = train_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
val_ds = val_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

# ---------------- Dataset info ----------------
print(f"Classes found: {class_names}")
print(f"Training batches: {len(train_ds)}, Validation batches: {len(val_ds)}")

# ---------------- Define CNN model ----------------
model = tf.keras.Sequential([
    tf.keras.layers.InputLayer(input_shape=(64, 64, 3)),
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(len(class_names), activation='softmax')
])

# ---------------- Compile model ----------------
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# ---------------- Train model ----------------
model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS
)

# ---------------- Save model ----------------
save_dir = os.path.join(os.path.dirname(__file__), "saved_models")
os.makedirs(save_dir, exist_ok=True)
model.save(os.path.join(save_dir, "asl_cnn_model.h5"))
