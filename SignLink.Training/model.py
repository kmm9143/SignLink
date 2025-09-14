# DESCRIPTION:  This script defines a Convolutional Neural Network (CNN) model builder for
#               American Sign Language (ASL) image classification. The model uses multiple
#               convolutional layers to extract features, followed by dense layers for classification.
#               Dropout is used for regularization, and the model is compiled with the Adam optimizer.
# LANGUAGE:     PYTHON
# SOURCE(S):    

import tensorflow as tf                                         # Import TensorFlow for deep learning operations
from keras import layers, models                                # Import Keras layers and models for building neural networks

def build_asl_cnn(input_shape=(64, 64, 3), num_classes=29):     # Define a function to build the ASL CNN model
    model = models.Sequential([                                 # Create a Sequential model for stacking layers
        layers.Conv2D(32, (3,3), activation='relu', input_shape=input_shape), # First convolutional layer: 32 filters, 3x3 kernel, ReLU activation, input shape specified
        layers.MaxPooling2D((2,2)),                            # First max pooling layer: downsample feature maps by factor of 2

        layers.Conv2D(64, (3,3), activation='relu'),           # Second convolutional layer: 64 filters, 3x3 kernel, ReLU activation
        layers.MaxPooling2D((2,2)),                            # Second max pooling layer: further downsample feature maps

        layers.Conv2D(128, (3,3), activation='relu'),          # Third convolutional layer: 128 filters, 3x3 kernel, ReLU activation
        layers.MaxPooling2D((2,2)),                            # Third max pooling layer: further downsample feature maps

        layers.Flatten(),                                      # Flatten layer: convert 3D feature maps to 1D vector

        layers.Dense(128, activation='relu'),                  # Dense layer: 128 units, ReLU activation for learning complex patterns
        layers.Dropout(0.5),                                   # Dropout layer: 50% rate for regularization to prevent overfitting
        layers.Dense(num_classes, activation='softmax')        # Output layer: softmax activation for multi-class classification
    ])

    model.compile(                                             # Compile the model with optimizer, loss, and metrics
        optimizer='adam',                                      # Adam optimizer for adaptive learning rate
        loss='categorical_crossentropy',                       # Categorical crossentropy loss for multi-class classification
        metrics=['accuracy']                                   # Track accuracy during training
    )
    return model                                               # Return the compiled model