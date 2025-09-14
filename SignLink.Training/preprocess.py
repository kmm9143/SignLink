# DESCRIPTION:  This script provides utility functions for downloading, extracting, and preprocessing
#               the American Sign Language (ASL) Alphabet image dataset for deep learning tasks.
#               It includes Kaggle API integration for dataset management and TensorFlow-based
#               preprocessing pipelines with normalization and augmentation for robust model training.
# LANGUAGE:     PYTHON
# SOURCE(S):    

# -----------------------------------------------------------------------------------
# Step 1: Import required libraries
# -----------------------------------------------------------------------------------
import os                                                      # Import the os module for file and directory operations
import tensorflow as tf                                        # Import TensorFlow for machine learning and data processing
from kaggle.api.kaggle_api_extended import KaggleApi           # Import KaggleApi for programmatic access to Kaggle datasets

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
def load_and_preprocess_dataset(dataset_dir, validation_split=0.2, seed=123): # Define a function to load and preprocess the dataset
    """
    Loads dataset from directory, applies preprocessing, augmentation,
    and returns train/validation datasets along with class names.

    Args:
        dataset_dir (str): Path to the dataset directory containing class subfolders.
        validation_split (float): Fraction of data to use for validation.
        seed (int): Random seed for reproducibility.

    Returns:
        train_ds (tf.data.Dataset): Preprocessed training dataset.
        val_ds (tf.data.Dataset): Preprocessed validation dataset.
        class_names (list): List of class names.
    """
    if not os.path.exists(dataset_dir):                        # Check if the dataset directory exists
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}") # Raise error if directory is missing

    # Load training dataset from directory with split
    train_ds = tf.keras.utils.image_dataset_from_directory(    # Create a training dataset from images in the directory
        dataset_dir,                                           # Path to the dataset directory
        validation_split=validation_split,                     # Fraction of data to use for validation
        subset="training",                                     # Specify that this is the training subset
        seed=seed,                                             # Set random seed for reproducibility
        image_size=IMG_SIZE,                                   # Resize images to target size
        batch_size=BATCH_SIZE                                  # Set batch size
    )

    # Load validation dataset from directory with split
    val_ds = tf.keras.utils.image_dataset_from_directory(      # Create a validation dataset from images in the directory
        dataset_dir,                                           # Path to the dataset directory
        validation_split=validation_split,                     # Fraction of data to use for validation
        subset="validation",                                   # Specify that this is the validation subset
        seed=seed,                                             # Set random seed for reproducibility
        image_size=IMG_SIZE,                                   # Resize images to target size
        batch_size=BATCH_SIZE                                  # Set batch size
    )

    class_names = train_ds.class_names                         # Get the list of class names from the training dataset

    # Normalize pixel values to [0, 1] for stable training [2]
    normalization_layer = tf.keras.layers.Rescaling(1./255)    # Create a normalization layer to scale pixel values
    train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y)) # Apply normalization to training dataset
    val_ds = val_ds.map(lambda x, y: (normalization_layer(x), y))     # Apply normalization to validation dataset

    # Data augmentation for improved generalization [2]
    data_augmentation = tf.keras.Sequential([                  # Create a sequential model for data augmentation
        tf.keras.layers.RandomFlip("horizontal"),              # Randomly flip images horizontally
        tf.keras.layers.RandomRotation(0.1),                   # Randomly rotate images by up to 10%
        tf.keras.layers.RandomZoom(0.1),                       # Randomly zoom images by up to 10%
    ])
    train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y)) # Apply augmentation to training dataset

    # Optimize dataset pipeline for performance
    AUTOTUNE = tf.data.AUTOTUNE                                # Set AUTOTUNE for automatic performance optimization
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE) # Cache, shuffle, and prefetch training data
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)     # Cache and prefetch validation data

    return train_ds, val_ds, class_names                       # Return the processed training and validation datasets and class names