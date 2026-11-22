"""
Inference module for the Bi-LSTM emotion classifier.
Loads model artifacts from disk and provides prediction functions.
"""
import sys
import json
import pickle
import logging
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# Global model state - loaded once on first use
_model = None
_tokenizer = None
_label_encoder = None
_model_config = None


def _get_config_paths():
    """Import config from parent directory."""
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import (
        MODEL_PATH, TOKENIZER_PATH, LABEL_ENCODER_PATH,
        MODEL_CONFIG_PATH, MAX_SEQUENCE_LENGTH, EMOTION_CLASSES
    )
    return MODEL_PATH, TOKENIZER_PATH, LABEL_ENCODER_PATH, MODEL_CONFIG_PATH, MAX_SEQUENCE_LENGTH, EMOTION_CLASSES


def load_artifacts():
    """
    Load model, tokenizer, and label encoder from disk.
    Raises RuntimeError if any artifact is missing.
    """
    global _model, _tokenizer, _label_encoder, _model_config

    MODEL_PATH, TOKENIZER_PATH, LABEL_ENCODER_PATH, MODEL_CONFIG_PATH, MAX_SEQUENCE_LENGTH, EMOTION_CLASSES = _get_config_paths()

    # Check all artifacts exist
    missing = []
    for path in [MODEL_PATH, TOKENIZER_PATH, LABEL_ENCODER_PATH, MODEL_CONFIG_PATH]:
        if not Path(path).exists():
            missing.append(str(path))

    if missing:
        raise RuntimeError(
            f"Model artifacts not found:\n" +
            "\n".join(f"  - {p}" for p in missing) +
            "\n\nTo train the model, run:\n"
            "  cd backend\n"
            "  python train_model.py\n\n"
            "This requires internet access to download the GoEmotions dataset.\n"
            "Training takes approximately 10-30 minutes depending on hardware."
        )

    if _model is None:
        logger.info("Loading Bi-LSTM model from disk...")
        from tensorflow.keras.models import load_model
        _model = load_model(str(MODEL_PATH))
        logger.info("Model loaded successfully")

    if _tokenizer is None:
        logger.info("Loading tokenizer...")
        with open(TOKENIZER_PATH, 'rb') as f:
            _tokenizer = pickle.load(f)
        logger.info("Tokenizer loaded")

    if _label_encoder is None:
        logger.info("Loading label encoder...")
        with open(LABEL_ENCODER_PATH, 'rb') as f:
            _label_encoder = pickle.load(f)
        logger.info("Label encoder loaded")

    if _model_config is None:
        with open(MODEL_CONFIG_PATH, 'r') as f:
            _model_config = json.load(f)

    return _model, _tokenizer, _label_encoder, _model_config


def is_model_loaded() -> bool:
    """Check if model artifacts are available."""
    MODEL_PATH, TOKENIZER_PATH, LABEL_ENCODER_PATH, MODEL_CONFIG_PATH, _, _ = _get_config_paths()
    return all(Path(p).exists() for p in [MODEL_PATH, TOKENIZER_PATH, LABEL_ENCODER_PATH, MODEL_CONFIG_PATH])


def predict_emotion(text: str) -> dict:
    """
    Predict emotion for a single text input.

    Args:
        text: Raw feedback text

    Returns:
        Dictionary with:
        - predicted_emotion: str
        - predicted_sentiment: str
        - confidence: float (0-1)
        - emotion_probabilities: dict {emotion: probability}
    """
    MODEL_PATH, TOKENIZER_PATH, LABEL_ENCODER_PATH, MODEL_CONFIG_PATH, MAX_SEQUENCE_LENGTH, EMOTION_CLASSES = _get_config_paths()

    model, tokenizer, label_encoder, model_config = load_artifacts()

    from ml.preprocessing import preprocess_for_inference
    from ml.label_mapping import get_sentiment

    # Preprocess
    seq = preprocess_for_inference(text, tokenizer, MAX_SEQUENCE_LENGTH)

    # Predict
    probs = model.predict(seq, verbose=0)[0]  # shape: (num_classes,)

    # Get class names from label encoder
    class_names = list(label_encoder.classes_)

    # Map probabilities to class names
    emotion_probs = {class_names[i]: float(probs[i]) for i in range(len(class_names))}

    # Predicted emotion and confidence
    pred_idx = int(np.argmax(probs))
    predicted_emotion = class_names[pred_idx]
    confidence = float(probs[pred_idx])

    # Derive sentiment
    predicted_sentiment = get_sentiment(predicted_emotion)

    return {
        "predicted_emotion": predicted_emotion,
        "predicted_sentiment": predicted_sentiment,
        "confidence": confidence,
        "emotion_probabilities": emotion_probs,
    }


if __name__ == "__main__":
    # Quick test
    test_texts = [
        "The professor was amazing and explained everything so clearly!",
        "I am very frustrated with the exam schedule. It is unfair.",
        "The lab facilities are okay, nothing special.",
        "I feel really sad about the lack of support from faculty.",
        "The curriculum is well-designed and I love learning here.",
    ]

    print("Running inference test...\n")
    for text in test_texts:
        result = predict_emotion(text)
        print(f"Text: {text[:60]}...")
        print(f"  Emotion: {result['predicted_emotion']} (confidence: {result['confidence']:.2%})")
        print(f"  Sentiment: {result['predicted_sentiment']}")
        print()
