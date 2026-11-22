"""
Training pipeline for the Bi-LSTM emotion classifier.

Dataset: GoEmotions (Google Research)
Source: https://github.com/google-research/google-research/tree/master/goemotions
        Available via HuggingFace datasets library

IMPORTANT DISCLAIMER:
GoEmotions contains general conversational Reddit text, NOT exclusively student feedback.
This dataset is used as a training corpus for emotion classification,
with acknowledged domain limitations. See docs/DATASET_DOCUMENTATION.md.

This module handles:
1. Dataset loading from HuggingFace
2. Label mapping to 7-class taxonomy
3. Text preprocessing
4. Train/validation/test split (70/15/15)
5. Class imbalance handling
6. Model training with callbacks
7. Saving all artifacts
"""

import sys
import json
import pickle
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    MAX_VOCAB_SIZE, MAX_SEQUENCE_LENGTH, EMBEDDING_DIM, LSTM_UNITS,
    DROPOUT_RATE, DENSE_UNITS, NUM_CLASSES, BATCH_SIZE, MAX_EPOCHS,
    LEARNING_RATE, EMOTION_CLASSES, MODEL_PATH, TOKENIZER_PATH,
    LABEL_ENCODER_PATH, MODEL_CONFIG_PATH, PROCESSED_DATA_PATH,
    DATASET_STATS_PATH, REPORTS_DIR, TRAINING_HISTORY_PATH,
    CONFUSION_MATRIX_PATH, CLASSIFICATION_REPORT_PATH, MODEL_METRICS_PATH
)
from ml.label_mapping import map_goemotions_labels, TARGET_EMOTIONS
from ml.preprocessing import clean_text, build_tokenizer, texts_to_sequences, save_tokenizer
from ml.model_builder import build_bilstm_model, get_callbacks, save_model_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_goemotions_dataset() -> pd.DataFrame:
    """
    Load GoEmotions dataset from HuggingFace datasets library.
    Falls back to cached CSV if network is unavailable.

    Returns:
        DataFrame with columns ['text', 'emotion']
    """
    logger.info("Loading GoEmotions dataset from HuggingFace...")

    try:
        from datasets import load_dataset
        dataset = load_dataset("go_emotions", "simplified", trust_remote_code=True)
        logger.info("Dataset loaded successfully from HuggingFace")

        records = []
        label_names = dataset['train'].features['labels'].feature.names
        logger.info(f"GoEmotions label names: {label_names}")

        for split_name in ['train', 'validation', 'test']:
            split = dataset[split_name]
            for item in split:
                text = item['text']
                labels = item['labels']
                # Map integer label IDs to string names
                label_strings = [label_names[i] for i in labels]
                mapped_emotion = map_goemotions_labels(label_strings)
                if mapped_emotion is not None and text and len(text.strip()) > 2:
                    records.append({'text': text, 'emotion': mapped_emotion})

        df = pd.DataFrame(records)
        logger.info(f"Loaded {len(df)} usable samples after label mapping")
        return df

    except Exception as e:
        logger.error(f"Failed to load from HuggingFace: {e}")
        raise RuntimeError(
            f"Could not load GoEmotions dataset: {e}\n"
            "Please ensure you have internet access and the 'datasets' package installed.\n"
            "Run: pip install datasets\n"
            "Then retry: python train_model.py"
        )


def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess the dataset.
    """
    logger.info("Preprocessing dataset...")
    initial_len = len(df)

    # Clean text
    df['text'] = df['text'].apply(clean_text)

    # Remove empty or too-short texts
    df = df[df['text'].str.len() >= 5].copy()

    # Remove duplicates
    df = df.drop_duplicates(subset=['text']).copy()

    # Remove NaN
    df = df.dropna(subset=['text', 'emotion']).copy()

    # Filter to valid emotion classes only
    df = df[df['emotion'].isin(TARGET_EMOTIONS)].copy()

    logger.info(f"After preprocessing: {len(df)} samples (removed {initial_len - len(df)})")
    return df


def compute_class_distribution(df: pd.DataFrame) -> dict:
    """Compute and log class distribution."""
    dist = df['emotion'].value_counts().to_dict()
    logger.info("Class distribution:")
    for emotion, count in sorted(dist.items()):
        pct = 100 * count / len(df)
        logger.info(f"  {emotion:15s}: {count:6d} ({pct:.1f}%)")
    return dist


def get_class_weights(y_train: np.ndarray, num_classes: int) -> dict:
    """Compute class weights to handle class imbalance."""
    class_indices = np.argmax(y_train, axis=1)
    classes = np.arange(num_classes)
    weights = compute_class_weight('balanced', classes=classes, y=class_indices)
    class_weight_dict = {i: w for i, w in enumerate(weights)}
    logger.info(f"Class weights: {class_weight_dict}")
    return class_weight_dict


def save_dataset_stats(df: pd.DataFrame, train_size: int, val_size: int, test_size: int) -> None:
    """Save dataset statistics for documentation."""
    stats = {
        "dataset_name": "GoEmotions (Google Research)",
        "dataset_source": "HuggingFace: go_emotions/simplified",
        "total_samples_after_mapping": len(df),
        "train_samples": train_size,
        "validation_samples": val_size,
        "test_samples": test_size,
        "split_ratio": "70/15/15",
        "emotion_distribution": df['emotion'].value_counts().to_dict(),
        "disclaimer": (
            "GoEmotions is a general conversational dataset (Reddit comments). "
            "It is NOT a student feedback dataset. Domain adaptation limitations apply."
        ),
        "label_mapping_strategy": (
            "Multi-label samples mapped to single class only if all labels agree on target class. "
            "Ambiguous and excluded-label samples are discarded."
        ),
        "preprocessing": [
            "Lowercase",
            "URL removal",
            "HTML tag removal",
            "Non-ASCII removal",
            "Duplicate removal",
            "Empty record removal",
            "Minimum 5 character filter",
        ],
        "generated_at": datetime.now().isoformat(),
    }
    with open(DATASET_STATS_PATH, 'w') as f:
        json.dump(stats, f, indent=2)
    logger.info(f"Dataset stats saved to {DATASET_STATS_PATH}")


def plot_training_history(history) -> None:
    """Generate and save training history plots."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Accuracy
    axes[0].plot(history.history['accuracy'], label='Train Accuracy', color='steelblue', linewidth=2)
    axes[0].plot(history.history['val_accuracy'], label='Val Accuracy', color='orange', linewidth=2)
    axes[0].set_title('Model Accuracy', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Accuracy')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Loss
    axes[1].plot(history.history['loss'], label='Train Loss', color='steelblue', linewidth=2)
    axes[1].plot(history.history['val_loss'], label='Val Loss', color='orange', linewidth=2)
    axes[1].set_title('Model Loss', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(TRAINING_HISTORY_PATH, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Training history plot saved to {TRAINING_HISTORY_PATH}")


def train_model():
    """
    Main training pipeline.
    """
    logger.info("=" * 60)
    logger.info("STUDENT FEEDBACK EMOTION ANALYZER - MODEL TRAINING")
    logger.info("=" * 60)

    # Step 1: Load dataset
    df = load_goemotions_dataset()

    # Step 2: Preprocess
    df = preprocess_dataset(df)

    # Step 3: Check distribution
    distribution = compute_class_distribution(df)

    # Step 4: Encode labels
    label_encoder = LabelEncoder()
    label_encoder.fit(TARGET_EMOTIONS)  # Fixed order
    encoded_labels = label_encoder.transform(df['emotion'].values)

    import tensorflow as tf
    from tensorflow.keras.utils import to_categorical
    y_categorical = to_categorical(encoded_labels, num_classes=NUM_CLASSES)

    logger.info(f"Label encoder classes: {list(label_encoder.classes_)}")

    # Step 5: Stratified train/val/test split
    texts = df['text'].values
    # 70/15/15 split
    X_train, X_temp, y_train, y_temp = train_test_split(
        texts, y_categorical,
        test_size=0.30,
        random_state=42,
        stratify=encoded_labels
    )
    encoded_temp = np.argmax(y_temp, axis=1)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp,
        test_size=0.50,
        random_state=42,
        stratify=encoded_temp
    )

    logger.info(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

    # Save dataset stats
    save_dataset_stats(df, len(X_train), len(X_val), len(X_test))

    # Save processed data for reference
    processed_df = pd.DataFrame({'text': texts, 'emotion': df['emotion'].values})
    processed_df.to_csv(PROCESSED_DATA_PATH, index=False)
    logger.info(f"Processed data saved to {PROCESSED_DATA_PATH}")

    # Step 6: Build tokenizer
    tokenizer = build_tokenizer(X_train.tolist(), MAX_VOCAB_SIZE)
    actual_vocab_size = min(len(tokenizer.word_index) + 1, MAX_VOCAB_SIZE)
    logger.info(f"Vocabulary size: {actual_vocab_size}")

    # Step 7: Pad sequences
    X_train_seq = texts_to_sequences(tokenizer, X_train.tolist(), MAX_SEQUENCE_LENGTH)
    X_val_seq = texts_to_sequences(tokenizer, X_val.tolist(), MAX_SEQUENCE_LENGTH)
    X_test_seq = texts_to_sequences(tokenizer, X_test.tolist(), MAX_SEQUENCE_LENGTH)

    # Step 8: Build model
    model = build_bilstm_model(
        vocab_size=actual_vocab_size,
        embedding_dim=EMBEDDING_DIM,
        max_sequence_length=MAX_SEQUENCE_LENGTH,
        lstm_units=LSTM_UNITS,
        dense_units=DENSE_UNITS,
        dropout_rate=DROPOUT_RATE,
        num_classes=NUM_CLASSES,
        learning_rate=LEARNING_RATE,
    )
    model.summary()

    # Step 9: Compute class weights
    class_weights = get_class_weights(y_train, NUM_CLASSES)

    # Step 10: Train
    logger.info("Starting training...")
    callbacks = get_callbacks(MODEL_PATH)
    history = model.fit(
        X_train_seq, y_train,
        validation_data=(X_val_seq, y_val),
        epochs=MAX_EPOCHS,
        batch_size=BATCH_SIZE,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1,
    )

    # Step 11: Evaluate on test set
    logger.info("Evaluating on held-out test set...")
    test_loss, test_accuracy = model.evaluate(X_test_seq, y_test, verbose=0)
    logger.info(f"Test Loss: {test_loss:.4f}")
    logger.info(f"Test Accuracy: {test_accuracy:.4f}")

    # Step 12: Save model
    model.save(str(MODEL_PATH))
    logger.info(f"Model saved to {MODEL_PATH}")

    # Step 13: Save tokenizer and label encoder
    save_tokenizer(tokenizer, TOKENIZER_PATH)
    with open(LABEL_ENCODER_PATH, 'wb') as f:
        pickle.dump(label_encoder, f)
    logger.info(f"Label encoder saved to {LABEL_ENCODER_PATH}")

    # Step 14: Save model config
    model_config = {
        "model_name": "Bi-LSTM Emotion Classifier",
        "model_version": "1.0",
        "architecture": "Bidirectional LSTM",
        "vocab_size": actual_vocab_size,
        "embedding_dim": EMBEDDING_DIM,
        "max_sequence_length": MAX_SEQUENCE_LENGTH,
        "lstm_units": LSTM_UNITS,
        "dense_units": DENSE_UNITS,
        "dropout_rate": DROPOUT_RATE,
        "num_classes": NUM_CLASSES,
        "emotion_classes": TARGET_EMOTIONS,
        "label_encoder_classes": list(label_encoder.classes_),
        "optimizer": "Adam",
        "loss": "categorical_crossentropy",
        "batch_size": BATCH_SIZE,
        "max_epochs": MAX_EPOCHS,
        "actual_epochs": len(history.history['accuracy']),
        "test_accuracy": float(test_accuracy),
        "test_loss": float(test_loss),
        "dataset": "GoEmotions (Google Research) via HuggingFace",
        "train_samples": int(len(X_train)),
        "val_samples": int(len(X_val)),
        "test_samples": int(len(X_test)),
        "trained_at": datetime.now().isoformat(),
    }
    save_model_config(model_config, MODEL_CONFIG_PATH)

    # Step 15: Generate evaluation report and plots
    from ml.evaluation import generate_full_evaluation
    generate_full_evaluation(model, X_test_seq, y_test, label_encoder, history)

    # Step 16: Plot training history
    plot_training_history(history)

    logger.info("=" * 60)
    logger.info("TRAINING COMPLETE")
    logger.info(f"Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
    logger.info("=" * 60)
    return model_config


if __name__ == "__main__":
    train_model()
