# DESCRIPTION:  This script provides utility functions for downloading, extracting, and preprocessing
#               the American Sign Language (ASL) Alphabet image dataset for deep learning tasks.
#               It includes Kaggle API integration for dataset management and TensorFlow-based
#               preprocessing pipelines with normalization and augmentation for robust model training.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] Kaggle. (2025, September 10). Datasets API — Public API. Kaggle. Retrieved September 12, 2025, from https://www.kaggle.com/docs/api
#               [2] Kaggle. (2025, September 10). Kaggle API (Official GitHub Repository). GitHub. Retrieved September 12, 2025, from https://github.com/Kaggle/kaggle-api
#               [3] Gazioğlu, M. (2022, March 30). Download any dataset from Kaggle with Kaggle API and Python. Medium. Retrieved September 12, 2025, from https://medium.com/@mine.gazioglu40/download-any-dataset-from-kaggle-with-kaggle-api-and-python-9ab84165aea0
#               [4] TensorFlow. (2025, September 10). tf.keras.utils.image_dataset_from_directory. TensorFlow API Documentation. Retrieved September 12, 2025, from https://www.tensorflow.org/api_docs/python/tf/keras/preprocessing/image_dataset_from_directory
#               [5] TensorFlow. (2025, September 10). Data augmentation. TensorFlow Tutorials. Retrieved September 12, 2025, from https://www.tensorflow.org/tutorials/images/data_augmentation
#               [6] Keras. (2025, September 10). Image classification from scratch. Keras Documentation. Retrieved September 12, 2025, from https://keras.io/examples/vision/image_classification_from_scratch/

# -----------------------------------------------------------------------------------
# Step 1: Import required libraries
# -----------------------------------------------------------------------------------
import os                                                      # Import the os module for file and directory operations
import tensorflow as tf                                        # Import TensorFlow for machine learning and data processing
from kaggle.api.kaggle_api_extended import KaggleApi           # Import KaggleApi for programmatic access to Kaggle datasets

# If using custom augmentation, import it here
try:
    from .data_augmentation import tf_augment_image            # Import custom Albumentations-based augmentation
except ImportError:
    tf_augment_image = None                                    # If not available, set to None

IMG_SIZE = (64, 64)                                            # Set the target image size for resizing input images
BATCH_SIZE = 32                                                # Set the batch size for training and validation datasets

# -----------------------------------------------------------------------------------
# Step 2: Define function to download and extract Kaggle dataset
# -----------------------------------------------------------------------------------
def download_and_extract_dataset(dataset_name, extract_to):     # Define a function to download and extract a Kaggle dataset
    """
    Downloads and extracts Kaggle dataset if not already present.
    Uses Kaggle Python API instead of os.system.

    Args:
        dataset_name (str): Kaggle dataset identifier (e.g., 'grassknoted/asl-alphabet').
        extract_to (str): Local directory to extract dataset files.
    """
    if not os.path.exists(extract_to):                         # Check if the extraction directory exists
        os.makedirs(extract_to, exist_ok=True)                 # If not, create the extraction directory

    api = KaggleApi()                                          # Instantiate the KaggleApi object
    api.authenticate()                                         # Authenticate with Kaggle using stored credentials

    print(f"Downloading and extracting {dataset_name} to {extract_to}...") # Print status message
    api.dataset_download_files(dataset_name, path=extract_to, unzip=True)  # Download and unzip the dataset files
    print("Download and extraction complete.")                 # Print completion message

# -----------------------------------------------------------------------------------
# Step 3: Define function to load and preprocess dataset
# -----------------------------------------------------------------------------------
def load_and_preprocess_dataset(dataset_dir, validation_split=0.2, seed=123, use_custom_augmentation=False): # Define a function to load and preprocess the dataset
    """
    Loads dataset from directory, applies preprocessing, augmentation,
    and returns train/validation datasets along with class names.

    Args:
        dataset_dir (str): Path to the dataset directory containing class subfolders.
        validation_split (float): Fraction of data to use for validation.
        seed (int): Random seed for reproducibility.
        use_custom_augmentation (bool): Whether to use custom Albumentations-based augmentation.

    Returns:
        train_ds (tf.data.Dataset): Preprocessed training dataset.
        val_ds (tf.data.Dataset): Preprocessed validation dataset.
        class_names (list): List of class names.
    """
    if not os.path.exists(dataset_dir):                        # Check if the dataset directory exists
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}") # Raise error if directory is missing

    # 1. Load training dataset as unbatched if using custom augmentation
    if use_custom_augmentation and tf_augment_image is not None:
        train_ds = tf.keras.utils.image_dataset_from_directory(
            dataset_dir,
            validation_split=validation_split,
            subset="training",
            seed=seed,
            image_size=IMG_SIZE,
            batch_size=None  # <--- IMPORTANT: no batching here!
        )
    else:
        train_ds = tf.keras.utils.image_dataset_from_directory(
            dataset_dir,
            validation_split=validation_split,
            subset="training",
            seed=seed,
            image_size=IMG_SIZE,
            batch_size=BATCH_SIZE
        )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        dataset_dir,
        validation_split=validation_split,
        subset="validation",
        seed=seed,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE
    )

    class_names = train_ds.class_names if not use_custom_augmentation else val_ds.class_names

    # 2. Apply custom Albumentations-based augmentation, then batch
    if use_custom_augmentation and tf_augment_image is not None:
        train_ds = train_ds.map(tf_augment_image)
        train_ds = train_ds.batch(BATCH_SIZE)

    # 3. Normalize pixel values to [0, 1]
    normalization_layer = tf.keras.layers.Rescaling(1./255)
    train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
    val_ds = val_ds.map(lambda x, y: (normalization_layer(x), y))

    # 4. If not using custom augmentation, use built-in Keras augmentation
    if not use_custom_augmentation:
        data_augmentation = tf.keras.Sequential([
            tf.keras.layers.RandomFlip("horizontal"),
            tf.keras.layers.RandomRotation(0.1),
            tf.keras.layers.RandomZoom(0.1),
        ])
        train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y))

    # 5. Optimize dataset pipeline for performance
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    return train_ds, val_ds, class_names                       # Return the processed training and validation datasets and class names

# -----------------------------------------------------------------------------------
# Step 4: (Optional) Custom Albumentations wrapper for single image augmentation
# -----------------------------------------------------------------------------------
def tf_augment_image(image, label):
    aug_img = tf.py_function(func=augment_image, inp=[image], Tout=tf.uint8) # Apply Albumentations via py_function
    aug_img.set_shape([64, 64, 3])                                          # Set static shape for TensorFlow
    aug_img = tf.cast(aug_img, tf.float32) / 255.0                          # Normalize to [0, 1]
    label = tf.cast(label, tf.int32)                                        # Ensure label is int32
    return aug_img, label