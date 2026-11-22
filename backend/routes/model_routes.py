"""
Model performance routes.
"""
import json
import logging
from pathlib import Path
from flask import Blueprint, jsonify, send_file

logger = logging.getLogger(__name__)
model_bp = Blueprint('model', __name__)


@model_bp.route('/metrics')
def get_model_metrics():
    """GET /api/model/metrics - Return model evaluation metrics."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import MODEL_METRICS_PATH, MODEL_CONFIG_PATH, CLASSIFICATION_REPORT_PATH

    response = {"success": True}

    if MODEL_METRICS_PATH.exists():
        with open(MODEL_METRICS_PATH, 'r') as f:
            response["metrics"] = json.load(f)
    else:
        response["metrics"] = None
        response["message"] = "Model not yet trained. Run train_model.py to generate metrics."

    if MODEL_CONFIG_PATH.exists():
        with open(MODEL_CONFIG_PATH, 'r') as f:
            response["config"] = json.load(f)
    else:
        response["config"] = None

    return jsonify(response)


@model_bp.route('/confusion_matrix')
def get_confusion_matrix():
    """GET /api/model/confusion_matrix - Serve confusion matrix image."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import CONFUSION_MATRIX_PATH

    if not CONFUSION_MATRIX_PATH.exists():
        return jsonify({"success": False, "error": "Confusion matrix not generated yet. Train the model first."}), 404

    return send_file(str(CONFUSION_MATRIX_PATH), mimetype='image/png')


@model_bp.route('/training_history')
def get_training_history():
    """GET /api/model/training_history - Serve training history plot."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import TRAINING_HISTORY_PATH

    if not TRAINING_HISTORY_PATH.exists():
        return jsonify({"success": False, "error": "Training history not available. Train the model first."}), 404

    return send_file(str(TRAINING_HISTORY_PATH), mimetype='image/png')
