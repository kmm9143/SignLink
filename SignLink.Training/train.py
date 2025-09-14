# DESCRIPTION:  This script defines and trains a baseline Convolutional Neural Network (CNN) model for
#               American Sign Language (ASL) image classification. It handles dataset download, preprocessing,
#               model definition, training, and saving. The model uses multiple convolutional layers to extract
#               features from images, followed by dense layers for classification. The trained model is saved
#               for later inference or evaluation.
# LANGUAGE:     PYTHON
# SOURCE(S):    

# -----------------------------------------------------------------------------------
# Step 1: Import required libraries and modules
# -----------------------------------------------------------------------------------
from preprocess import load_and_preprocess_dataset, download_and_extract_dataset   # Import custom preprocessing and download functions
import tensorflow as tf                                                           # Import TensorFlow for deep learning operations
import os                                                                         # Import os for file and directory management

# -----------------------------------------------------------------------------------
# Step 2: Set dataset paths
# -----------------------------------------------------------------------------------
DATASET_ROOT = r"C:\Datasets\ASL_Alphabet"                                        # Root directory for the ASL dataset
DATASET_DIR = r"C:\Datasets\ASL_Alphabet\asl_alphabet_train"                      # Directory containing training images

# -----------------------------------------------------------------------------------
# Step 3: Download and extract Kaggle dataset if missing
# -----------------------------------------------------------------------------------
download_and_extract_dataset("grassknoted/asl-alphabet", DATASET_ROOT)            # Download and extract the ASL dataset from Kaggle if not present

# -----------------------------------------------------------------------------------
# Step 4: Load and preprocess dataset
# -----------------------------------------------------------------------------------
train_ds, val_ds, class_names = load_and_preprocess_dataset(DATASET_DIR)          # Load and preprocess training and validation datasets, get class names

# -----------------------------------------------------------------------------------
# Step 5: Print dataset information
# -----------------------------------------------------------------------------------
print(f"Classes found: {class_names}")                                            # Print the list of detected class names
print(f"Training batches: {len(train_ds)}, Validation batches: {len(val_ds)}")    # Print the number of batches in training and validation datasets

# -----------------------------------------------------------------------------------
# Step 6: Define the CNN model architecture
# -----------------------------------------------------------------------------------
model = tf.keras.Sequential([                                                     # Create a Sequential model for stacking layers
    tf.keras.layers.InputLayer(input_shape=(64, 64, 3)),                          # Input layer specifying image shape (64x64 RGB)
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),                        # First convolutional layer with 32 filters and ReLU activation
    tf.keras.layers.MaxPooling2D(),                                               # Max pooling layer to downsample feature maps
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),                        # Second convolutional layer with 64 filters and ReLU activation
    tf.keras.layers.MaxPooling2D(),                                               # Max pooling layer to further downsample
    tf.keras.layers.Flatten(),                                                    # Flatten layer to convert 2D features to 1D vector
    tf.keras.layers.Dense(128, activation='relu'),                                # Dense layer with 128 units and ReLU activation
    tf.keras.layers.Dense(len(class_names), activation='softmax')                 # Output layer with softmax activation for multi-class classification
])

# -----------------------------------------------------------------------------------
# Step 7: Compile the model
# -----------------------------------------------------------------------------------
model.compile(optimizer='adam',                                                   # Compile the model using Adam optimizer
              loss='sparse_categorical_crossentropy',                             # Use sparse categorical crossentropy loss for integer labels
              metrics=['accuracy'])                                               # Track accuracy during training

# -----------------------------------------------------------------------------------
# Step 8: Train the model
# -----------------------------------------------------------------------------------
model.fit(train_ds, validation_data=val_ds, epochs=5)                             # Train the model for 5 epochs using training and validation datasets

# -----------------------------------------------------------------------------------
# Step 9: Ensure the save directory exists
# -----------------------------------------------------------------------------------
save_dir = os.path.join(os.path.dirname(__file__), "saved_models")                # Define the path to the model save directory
os.makedirs(save_dir, exist_ok=True)                                              # Create the save directory if it does not exist

# -----------------------------------------------------------------------------------
# Step 10: Save the trained model
# -----------------------------------------------------------------------------------
model.save(os.path.join(save_dir, "asl_cnn_model.h5"))                            # Save the trained model to the specified directory
