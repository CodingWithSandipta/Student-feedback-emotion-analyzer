"""
Feedback routes: submit, retrieve, delete.
"""
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import or_

from extensions import db
from models import Feedback, Course
from config import MIN_FEEDBACK_LENGTH, MAX_FEEDBACK_LENGTH, SEMESTERS, ACADEMIC_CATEGORIES
from ml.predict import predict_emotion

logger = logging.getLogger(__name__)
feedback_bp = Blueprint('feedback', __name__)


def validate_feedback_input(data: dict) -> tuple[bool, str]:
    """Validate incoming feedback data. Returns (is_valid, error_message)."""
    text = data.get('feedback_text', '').strip()
    if not text:
        return False, "Feedback text is required"
    if len(text) < MIN_FEEDBACK_LENGTH:
        return False, f"Feedback must be at least {MIN_FEEDBACK_LENGTH} characters"
    if len(text) > MAX_FEEDBACK_LENGTH:
        return False, f"Feedback must not exceed {MAX_FEEDBACK_LENGTH} characters"

    course = data.get('course_name', '').strip()
    if not course:
        return False, "Course name is required"
    if len(course) > 200:
        return False, "Course name too long"

    semester = data.get('semester', '').strip()
    if semester not in SEMESTERS:
        return False, f"Invalid semester. Must be one of: {', '.join(SEMESTERS)}"

    category = data.get('academic_category', '').strip()
    if category not in ACADEMIC_CATEGORIES:
        return False, f"Invalid academic category. Must be one of: {', '.join(ACADEMIC_CATEGORIES)}"

    return True, ""


@feedback_bp.route('/analyze', methods=['POST'])
def analyze_feedback():
    """
    POST /api/analyze
    Analyze feedback text and store results.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON body"}), 400

    # Validate
    is_valid, error_msg = validate_feedback_input(data)
    if not is_valid:
        return jsonify({"success": False, "error": error_msg}), 400

    # Run prediction
    try:
        prediction = predict_emotion(data['feedback_text'].strip())
    except RuntimeError as e:
        return jsonify({
            "success": False,
            "error": "Model not available",
            "message": str(e),
        }), 503
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Prediction failed"}), 500

    # Save to database
    try:
        student_id = data.get('student_id', '').strip() or None
        feedback = Feedback(
            student_id=student_id,
            course_name=data['course_name'].strip(),
            semester=data['semester'].strip(),
            academic_category=data['academic_category'].strip(),
            feedback_text=data['feedback_text'].strip(),
            predicted_emotion=prediction['predicted_emotion'],
            predicted_sentiment=prediction['predicted_sentiment'],
            confidence_score=prediction['confidence'],
        )
        db.session.add(feedback)

        # Track course
        existing_course = Course.query.filter_by(course_name=data['course_name'].strip()).first()
        if not existing_course:
            db.session.add(Course(course_name=data['course_name'].strip()))

        db.session.commit()

        return jsonify({
            "success": True,
            "feedback_id": feedback.id,
            "predicted_emotion": prediction['predicted_emotion'],
            "predicted_sentiment": prediction['predicted_sentiment'],
            "confidence": prediction['confidence'],
            "emotion_probabilities": prediction['emotion_probabilities'],
            "course_name": feedback.course_name,
            "semester": feedback.semester,
            "academic_category": feedback.academic_category,
            "created_at": feedback.created_at.isoformat(),
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Database error"}), 500


@feedback_bp.route('/feedback', methods=['GET'])
def get_feedback():
    """
    GET /api/feedback
    Retrieve feedback with filtering and pagination.
    """
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    # Filters
    course = request.args.get('course', '').strip()
    semester = request.args.get('semester', '').strip()
    emotion = request.args.get('emotion', '').strip()
    sentiment = request.args.get('sentiment', '').strip()
    category = request.args.get('category', '').strip()
    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'newest')

    query = Feedback.query

    if course:
        query = query.filter(Feedback.course_name.ilike(f'%{course}%'))
    if semester:
        query = query.filter(Feedback.semester == semester)
    if emotion:
        query = query.filter(Feedback.predicted_emotion == emotion)
    if sentiment:
        query = query.filter(Feedback.predicted_sentiment == sentiment)
    if category:
        query = query.filter(Feedback.academic_category == category)
    if search:
        query = query.filter(Feedback.feedback_text.ilike(f'%{search}%'))

    if sort == 'oldest':
        query = query.order_by(Feedback.created_at.asc())
    else:
        query = query.order_by(Feedback.created_at.desc())

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "success": True,
        "feedback": [f.to_dict() for f in paginated.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": paginated.total,
            "pages": paginated.pages,
            "has_next": paginated.has_next,
            "has_prev": paginated.has_prev,
        }
    })


@feedback_bp.route('/feedback/<int:feedback_id>', methods=['GET'])
def get_feedback_by_id(feedback_id):
    """GET /api/feedback/<id>"""
    feedback = Feedback.query.get_or_404(feedback_id)
    return jsonify({"success": True, "feedback": feedback.to_dict()})


@feedback_bp.route('/feedback/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    """DELETE /api/feedback/<id>"""
    feedback = Feedback.query.get_or_404(feedback_id)
    try:
        db.session.delete(feedback)
        db.session.commit()
        return jsonify({"success": True, "message": f"Feedback {feedback_id} deleted"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete error: {e}")
        return jsonify({"success": False, "error": "Delete failed"}), 500
