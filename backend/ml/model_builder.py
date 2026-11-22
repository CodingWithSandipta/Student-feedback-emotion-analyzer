"""
Bi-LSTM model architecture builder.
"""
import json
import pickle
from pathlib import Path
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import (
    Embedding, Bidirectional, LSTM, Dense, Dropout, GlobalMaxPooling1D
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau


def build_bilstm_model(
    vocab_size: int,
    embedding_dim: int = 128,
    max_sequence_length: int = 100,
    lstm_units: int = 64,
    dense_units: int = 64,
    dropout_rate: float = 0.3,
    num_classes: int = 7,
    learning_rate: float = 0.001,
) -> tf.keras.Model:
    """
    Build a Bidirectional LSTM model for emotion classification.

    Architecture:
        Input -> Embedding -> Bi-LSTM -> Dropout -> Dense(ReLU) -> Dropout -> Softmax

    Args:
        vocab_size: Size of vocabulary (number of unique tokens).
        embedding_dim: Dimension of token embeddings.
        max_sequence_length: Length of padded sequences.
        lstm_units: Number of LSTM units per direction.
        dense_units: Neurons in intermediate dense layer.
        dropout_rate: Dropout probability.
        num_classes: Number of output emotion classes.
        learning_rate: Adam optimizer learning rate.

    Returns:
        Compiled Keras model.
    """
    model = Sequential([
        # Embedding layer converts token IDs to dense vectors
        Embedding(
            input_dim=vocab_size,
            output_dim=embedding_dim,
            input_length=max_sequence_length,
            mask_zero=True,
            name="embedding"
        ),

        # Bidirectional LSTM: processes sequence in both directions
        # return_sequences=False: use the final hidden state
        Bidirectional(
            LSTM(lstm_units, dropout=dropout_rate, recurrent_dropout=0.0),
            name="bidirectional_lstm"
        ),

        # Dropout for regularization
        Dropout(dropout_rate, name="dropout_1"),

        # Dense hidden layer with ReLU activation
        Dense(dense_units, activation='relu', name="dense_hidden"),

        # Second dropout
        Dropout(dropout_rate, name="dropout_2"),

        # Softmax output: probabilities over 7 emotion classes
        Dense(num_classes, activation='softmax', name="emotion_output"),
    ])

    optimizer = Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model


def get_callbacks(model_path: Path) -> list:
    """
    Get training callbacks:
    - EarlyStopping on validation loss
    - ModelCheckpoint to save best weights
    - ReduceLROnPlateau on validation loss plateau
    """
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=3,
            restore_best_weights=True,
            verbose=1,
        ),
        ModelCheckpoint(
            filepath=str(model_path),
            monitor='val_loss',
            save_best_only=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            verbose=1,
        ),
    ]
    return callbacks


def save_model_config(config: dict, path: Path) -> None:
    """Save model configuration to JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Model config saved to {path}")


def load_saved_model(model_path: Path) -> tf.keras.Model:
    """Load a saved Keras model."""
    return load_model(str(model_path))
