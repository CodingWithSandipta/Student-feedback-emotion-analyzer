"""
Evaluation module for the Bi-LSTM emotion classifier.
Generates classification report, confusion matrix, and model metrics.
"""
import json
import logging
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, f1_score, precision_score, recall_score
)
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)


def generate_full_evaluation(
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    label_encoder: LabelEncoder,
    history=None,
) -> dict:
    """
    Generate comprehensive evaluation metrics and visualizations.

    Args:
        model: Trained Keras model
        X_test: Test sequences (padded)
        y_test: True labels (one-hot encoded)
        label_encoder: Fitted LabelEncoder
        history: Keras training History object (optional)

    Returns:
        Dictionary of metrics
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import (
        REPORTS_DIR, CLASSIFICATION_REPORT_PATH,
        CONFUSION_MATRIX_PATH, MODEL_METRICS_PATH
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Get predictions
    y_pred_probs = model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_pred_probs, axis=1)
    y_true = np.argmax(y_test, axis=1)

    class_names = list(label_encoder.classes_)

    # Overall metrics
    accuracy = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    macro_precision = precision_score(y_true, y_pred, average='macro', zero_division=0)
    macro_recall = recall_score(y_true, y_pred, average='macro', zero_division=0)

    logger.info(f"Test Accuracy:        {accuracy:.4f}")
    logger.info(f"Macro F1:             {macro_f1:.4f}")
    logger.info(f"Weighted F1:          {weighted_f1:.4f}")
    logger.info(f"Macro Precision:      {macro_precision:.4f}")
    logger.info(f"Macro Recall:         {macro_recall:.4f}")

    # Per-class report
    report_dict = classification_report(
        y_true, y_pred,
        target_names=class_names,
        output_dict=True,
        zero_division=0
    )
    report_text = classification_report(
        y_true, y_pred,
        target_names=class_names,
        zero_division=0
    )
    logger.info(f"\nClassification Report:\n{report_text}")

    # Save classification report
    full_report = {
        "classification_report": report_dict,
        "classification_report_text": report_text,
        "overall_metrics": {
            "accuracy": float(accuracy),
            "macro_f1": float(macro_f1),
            "weighted_f1": float(weighted_f1),
            "macro_precision": float(macro_precision),
            "macro_recall": float(macro_recall),
        },
        "class_names": class_names,
        "test_samples": int(len(y_true)),
    }
    with open(CLASSIFICATION_REPORT_PATH, 'w') as f:
        json.dump(full_report, f, indent=2)

    # Confusion matrix plot
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=class_names,
        yticklabels=class_names,
        linewidths=0.5,
    )
    plt.title('Confusion Matrix - Bi-LSTM Emotion Classifier', fontsize=14, fontweight='bold', pad=15)
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(CONFUSION_MATRIX_PATH, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Confusion matrix saved to {CONFUSION_MATRIX_PATH}")

    # Training history if available
    training_history = {}
    if history is not None:
        training_history = {
            "accuracy": [float(v) for v in history.history.get('accuracy', [])],
            "val_accuracy": [float(v) for v in history.history.get('val_accuracy', [])],
            "loss": [float(v) for v in history.history.get('loss', [])],
            "val_loss": [float(v) for v in history.history.get('val_loss', [])],
        }

    # Save model metrics
    metrics = {
        "model_name": "Bi-LSTM Emotion Classifier",
        "dataset": "GoEmotions (Google Research)",
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "per_class_metrics": {
            class_name: {
                "precision": float(report_dict[class_name]["precision"]),
                "recall": float(report_dict[class_name]["recall"]),
                "f1_score": float(report_dict[class_name]["f1-score"]),
                "support": int(report_dict[class_name]["support"]),
            }
            for class_name in class_names
            if class_name in report_dict
        },
        "training_history": training_history,
        "confusion_matrix": cm.tolist(),
        "class_names": class_names,
        "disclaimer": (
            "These metrics reflect performance on a held-out test split of GoEmotions "
            "(general conversational data). Performance on real student feedback may differ "
            "due to domain mismatch."
        ),
    }

    with open(MODEL_METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Model metrics saved to {MODEL_METRICS_PATH}")

    return metrics


def load_model_metrics() -> dict:
    """Load saved model metrics."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import MODEL_METRICS_PATH

    if not MODEL_METRICS_PATH.exists():
        return {}
    with open(MODEL_METRICS_PATH, 'r') as f:
        return json.load(f)
