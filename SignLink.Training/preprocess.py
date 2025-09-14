# -*- coding: utf-8 -*-
import os
import tensorflow as tf
from kaggle.api.kaggle_api_extended import KaggleApi

IMG_SIZE = (64, 64)
BATCH_SIZE = 32

def download_and_extract_dataset(dataset_name, extract_to):
    """
    Downloads and extracts Kaggle dataset if not already present.
    Uses Kaggle Python API instead of os.system.
    """
    if not os.path.exists(extract_to):
        os.makedirs(extract_to, exist_ok=True)

    api = KaggleApi()
    api.authenticate()

    print(f"Downloading and extracting {dataset_name} to {extract_to}...")
    api.dataset_download_files(dataset_name, path=extract_to, unzip=True)
    print("Download and extraction complete.")

def load_and_preprocess_dataset(dataset_dir, validation_split=0.2, seed=123):
    """
    Loads dataset from directory, applies preprocessing, augmentation,
    and returns train/validation datasets along with class names.
    """
    if not os.path.exists(dataset_dir):
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    # Load training and validation datasets
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

    # Capture class names before mapping/prefetching
    class_names = train_ds.class_names

    # Normalize images (0-1 range)
    normalization_layer = tf.keras.layers.Rescaling(1./255)
    train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
    val_ds = val_ds.map(lambda x, y: (normalization_layer(x), y))

    # Data augmentation (applied only to training set)
    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.1),
        tf.keras.layers.RandomZoom(0.1),
    ])
    train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y))

    # Improve performance with caching and prefetching
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    return train_ds, val_ds, class_names