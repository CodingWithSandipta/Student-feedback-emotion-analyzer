"""
CSV export routes.
"""
import csv
import io
import logging
from datetime import datetime
from flask import Blueprint, request, make_response

from models import Feedback

logger = logging.getLogger(__name__)
export_bp = Blueprint('export', __name__)


@export_bp.route('/csv')
def export_csv():
    """GET /api/export/csv - Export filtered feedback as CSV."""
    # Filters
    course = request.args.get('course', '').strip()
    semester = request.args.get('semester', '').strip()
    emotion = request.args.get('emotion', '').strip()
    sentiment = request.args.get('sentiment', '').strip()
    category = request.args.get('category', '').strip()

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

    records = query.order_by(Feedback.created_at.desc()).all()

    # Build CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Feedback ID', 'Student ID', 'Course Name', 'Semester',
        'Academic Category', 'Feedback Text', 'Predicted Emotion',
        'Predicted Sentiment', 'Confidence Score', 'Submission Date'
    ])

    for f in records:
        writer.writerow([
            f.id,
            f.student_id or 'Anonymous',
            f.course_name,
            f.semester,
            f.academic_category,
            f.feedback_text,
            f.predicted_emotion,
            f.predicted_sentiment,
            f"{f.confidence_score:.4f}",
            f.created_at.strftime('%Y-%m-%d %H:%M:%S') if f.created_at else '',
        ])

    csv_content = output.getvalue()
    output.close()

    filename = f"feedback_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response = make_response(csv_content)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
