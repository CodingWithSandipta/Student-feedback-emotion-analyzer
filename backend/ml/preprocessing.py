"""
Text preprocessing utilities for the Bi-LSTM emotion classifier.
"""
import re
import string
import numpy as np
import pickle
from pathlib import Path
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences


def clean_text(text: str) -> str:
    """
    Clean and normalize input text.
    - Lowercase
    - Remove URLs
    - Remove special characters (keep basic punctuation)
    - Remove extra whitespace
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Remove excess punctuation but keep sentence-ending punctuation
    text = re.sub(r'[^\w\s\.\,\!\?]', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def build_tokenizer(texts: list, max_vocab_size: int = 20000) -> Tokenizer:
    """
    Build and fit a Keras Tokenizer on the training texts.
    """
    tokenizer = Tokenizer(
        num_words=max_vocab_size,
        oov_token="<OOV>",
        filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n',
        lower=True,
    )
    tokenizer.fit_on_texts(texts)
    return tokenizer


def texts_to_sequences(tokenizer: Tokenizer, texts: list, max_len: int = 100) -> np.ndarray:
    """
    Convert texts to padded sequences.
    """
    sequences = tokenizer.texts_to_sequences(texts)
    padded = pad_sequences(sequences, maxlen=max_len, padding='post', truncating='post')
    return padded


def save_tokenizer(tokenizer: Tokenizer, path: Path) -> None:
    """Save tokenizer to disk."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        pickle.dump(tokenizer, f)
    print(f"Tokenizer saved to {path}")


def load_tokenizer(path: Path) -> Tokenizer:
    """Load tokenizer from disk."""
    with open(path, 'rb') as f:
        tokenizer = pickle.load(f)
    return tokenizer


def preprocess_for_inference(text: str, tokenizer: Tokenizer, max_len: int = 100) -> np.ndarray:
    """
    Full preprocessing pipeline for a single text input.
    """
    cleaned = clean_text(text)
    sequence = tokenizer.texts_to_sequences([cleaned])
    padded = pad_sequences(sequence, maxlen=max_len, padding='post', truncating='post')
    return padded
