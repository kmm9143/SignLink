# DESCRIPTION: Defines image augmentation pipeline for ASL dataset using Albumentations.
#              Provides a function to augment training dataset during loading.
# LANGUAGE:    PYTHON
# SOURCE(S):   [1] Albumentations. (n.d.). Image augmentation library. Retrieved September 17, 2025, from https://albumentations.ai/docs/
#              [2] TensorFlow. (n.d.). tf.data: Build TensorFlow input pipelines. Retrieved September 17, 2025, from https://www.tensorflow.org/guide/data

import tensorflow as tf
import albumentations as A
import numpy as np
import cv2

# Define augmentation pipeline
augment_pipeline = A.Compose([
    A.RandomBrightnessContrast(p=0.5),
    A.HueSaturationValue(p=0.5),
    A.RandomGamma(p=0.3),
    A.HorizontalFlip(p=0.5),
    A.Rotate(limit=20, p=0.5),
    A.MotionBlur(p=0.3),
    A.GaussNoise(p=0.3),
    A.RandomShadow(p=0.3),
    A.RandomFog(p=0.2),
    A.CoarseDropout(max_holes=8, max_height=8, max_width=8, p=0.4)
])

def augment_image(image):
    """Apply augmentation to a single image (NumPy array)."""
    img = image.numpy()
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    augmented = augment_pipeline(image=img)
    aug_img = cv2.cvtColor(augmented['image'], cv2.COLOR_BGR2RGB)
    return aug_img

def tf_augment_image(image, label):
    """Wrapper for TensorFlow dataset pipeline."""
    # Use tf.map_fn to apply augment_image to each image in the batch
    aug_img = tf.map_fn(
        lambda img: tf.py_function(func=augment_image, inp=[img], Tout=tf.uint8),
        image,
        fn_output_signature=tf.uint8
    )
    aug_img.set_shape([None, 64, 64, 3])  # None for batch size
    aug_img = tf.cast(aug_img, tf.float32) / 255.0

    label = tf.cast(label, tf.int32)
    # Do not reshape label; keep as is (batch shape)
    return aug_img, label
