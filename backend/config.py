"""
Configuration settings for the Student Feedback Emotion Analyzer.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.absolute()

# Database
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "feedback.db"
DATABASE_URI = f"sqlite:///{DATABASE_PATH}"

# Model artifacts
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "bilstm_emotion_model.keras"
TOKENIZER_PATH = MODELS_DIR / "tokenizer.pkl"
LABEL_ENCODER_PATH = MODELS_DIR / "label_encoder.pkl"
MODEL_CONFIG_PATH = MODELS_DIR / "model_config.json"

# Reports
REPORTS_DIR = BASE_DIR / "reports"
CLASSIFICATION_REPORT_PATH = REPORTS_DIR / "classification_report.json"
CONFUSION_MATRIX_PATH = REPORTS_DIR / "confusion_matrix.png"
TRAINING_HISTORY_PATH = REPORTS_DIR / "training_history.png"
MODEL_METRICS_PATH = REPORTS_DIR / "model_metrics.json"

# Dataset
DATASETS_DIR = BASE_DIR / "datasets"
RAW_DATA_DIR = DATASETS_DIR / "raw"
PROCESSED_DATA_DIR = DATASETS_DIR / "processed"
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "processed_data.csv"
DATASET_STATS_PATH = PROCESSED_DATA_DIR / "dataset_stats.json"

# ML Hyperparameters
MAX_VOCAB_SIZE = 20000
MAX_SEQUENCE_LENGTH = 100
EMBEDDING_DIM = 128
LSTM_UNITS = 64
DROPOUT_RATE = 0.3
DENSE_UNITS = 64
NUM_CLASSES = 7
BATCH_SIZE = 32
MAX_EPOCHS = 15
LEARNING_RATE = 0.001

# Emotion classes
EMOTION_CLASSES = ["joy", "satisfaction", "anger", "sadness", "fear", "frustration", "neutral"]

# Sentiment mapping
SENTIMENT_MAP = {
    "joy": "positive",
    "satisfaction": "positive",
    "anger": "negative",
    "sadness": "negative",
    "fear": "negative",
    "frustration": "negative",
    "neutral": "neutral",
}

# GoEmotions to our emotion mapping
GOEMOTIONS_MAPPING = {
    "joy": "joy",
    "amusement": "joy",
    "excitement": "joy",
    "approval": "satisfaction",
    "admiration": "satisfaction",
    "gratitude": "satisfaction",
    "love": "satisfaction",
    "optimism": "satisfaction",
    "relief": "satisfaction",
    "pride": "satisfaction",
    "anger": "anger",
    "disgust": "anger",
    "sadness": "sadness",
    "grief": "sadness",
    "disappointment": "sadness",
    "remorse": "sadness",
    "fear": "fear",
    "nervousness": "fear",
    "annoyance": "frustration",
    "neutral": "neutral",
}

# Academic categories
ACADEMIC_CATEGORIES = [
    "Teaching Quality",
    "Faculty Behavior",
    "Course Curriculum",
    "Examination",
    "Assignments",
    "Infrastructure",
    "Laboratory",
    "General Feedback",
]

# Semesters
SEMESTERS = [f"Semester {i}" for i in range(1, 9)]

# API Settings
MAX_FEEDBACK_LENGTH = 2000
MIN_FEEDBACK_LENGTH = 5

# Ensure directories exist
for d in [DATABASE_DIR, MODELS_DIR, REPORTS_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR]:
    d.mkdir(parents=True, exist_ok=True)
