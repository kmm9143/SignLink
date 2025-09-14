from preprocess import load_and_preprocess_dataset, download_and_extract_dataset
import tensorflow as tf

# Local dataset folder
DATASET_ROOT = r"C:\Datasets\ASL_Alphabet"
DATASET_DIR = r"C:\Datasets\ASL_Alphabet\asl_alphabet_train"

# Step 1: Download and extract Kaggle dataset if missing
download_and_extract_dataset("grassknoted/asl-alphabet", DATASET_ROOT)

# Step 2: Load and preprocess dataset
train_ds, val_ds, class_names = load_and_preprocess_dataset(DATASET_DIR)

# Optional: Print dataset info
print(f"Classes found: {class_names}")
print(f"Training batches: {len(train_ds)}, Validation batches: {len(val_ds)}")

# Step 3: Define a simple CNN model (example)
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

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Step 4: Train the model
model.fit(train_ds, validation_data=val_ds, epochs=5)
