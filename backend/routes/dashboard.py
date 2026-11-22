"""
Dashboard analytics routes.
"""
import logging
from collections import defaultdict
from flask import Blueprint, jsonify, request
from sqlalchemy import func, case

from extensions import db
from models import Feedback

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint('dashboard', __name__)


def _apply_date_filters(query, start_date=None, end_date=None):
    """Apply optional date filters."""
    from datetime import datetime
    if start_date:
        try:
            dt = datetime.fromisoformat(start_date)
            query = query.filter(Feedback.created_at >= dt)
        except ValueError:
            pass
    if end_date:
        try:
            dt = datetime.fromisoformat(end_date)
            query = query.filter(Feedback.created_at <= dt)
        except ValueError:
            pass
    return query


@dashboard_bp.route('/summary')
def get_summary():
    """GET /api/dashboard/summary - KPI metrics."""
    total = Feedback.query.count()

    if total == 0:
        return jsonify({
            "success": True,
            "total_feedback": 0,
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "positive_pct": 0,
            "negative_pct": 0,
            "neutral_pct": 0,
            "most_common_emotion": "N/A",
            "courses_analyzed": 0,
        })

    sentiments = db.session.query(
        Feedback.predicted_sentiment,
        func.count(Feedback.id).label('count')
    ).group_by(Feedback.predicted_sentiment).all()

    sentiment_map = {row.predicted_sentiment: row.count for row in sentiments}
    positive = sentiment_map.get('positive', 0)
    negative = sentiment_map.get('negative', 0)
    neutral = sentiment_map.get('neutral', 0)

    # Most common emotion
    top_emotion = db.session.query(
        Feedback.predicted_emotion,
        func.count(Feedback.id).label('cnt')
    ).group_by(Feedback.predicted_emotion).order_by(func.count(Feedback.id).desc()).first()

    # Unique courses
    courses_count = db.session.query(func.count(func.distinct(Feedback.course_name))).scalar()

    return jsonify({
        "success": True,
        "total_feedback": total,
        "positive_count": positive,
        "negative_count": negative,
        "neutral_count": neutral,
        "positive_pct": round(100 * positive / total, 1),
        "negative_pct": round(100 * negative / total, 1),
        "neutral_pct": round(100 * neutral / total, 1),
        "most_common_emotion": top_emotion.predicted_emotion if top_emotion else "N/A",
        "courses_analyzed": courses_count or 0,
    })


@dashboard_bp.route('/emotions')
def get_emotion_distribution():
    """GET /api/dashboard/emotions - Emotion distribution."""
    results = db.session.query(
        Feedback.predicted_emotion,
        func.count(Feedback.id).label('count')
    ).group_by(Feedback.predicted_emotion).all()

    # Ensure all 7 emotions are present
    from config import EMOTION_CLASSES
    emotion_map = {row.predicted_emotion: row.count for row in results}
    data = [
        {"emotion": e, "count": emotion_map.get(e, 0)}
        for e in EMOTION_CLASSES
    ]

    return jsonify({"success": True, "data": data})


@dashboard_bp.route('/sentiments')
def get_sentiment_distribution():
    """GET /api/dashboard/sentiments - Sentiment distribution."""
    results = db.session.query(
        Feedback.predicted_sentiment,
        func.count(Feedback.id).label('count')
    ).group_by(Feedback.predicted_sentiment).all()

    sentiment_map = {row.predicted_sentiment: row.count for row in results}
    total = sum(sentiment_map.values()) or 1

    data = [
        {
            "sentiment": s,
            "count": sentiment_map.get(s, 0),
            "percentage": round(100 * sentiment_map.get(s, 0) / total, 1)
        }
        for s in ['positive', 'negative', 'neutral']
    ]
    return jsonify({"success": True, "data": data})


@dashboard_bp.route('/courses')
def get_course_analysis():
    """GET /api/dashboard/courses - Course-wise sentiment analysis."""
    results = db.session.query(
        Feedback.course_name,
        Feedback.predicted_sentiment,
        func.count(Feedback.id).label('count')
    ).group_by(Feedback.course_name, Feedback.predicted_sentiment).all()

    # Build grouped data per course
    course_data = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
    for row in results:
        course_data[row.course_name][row.predicted_sentiment] = row.count

    data = [
        {
            "course": course,
            "positive": counts['positive'],
            "negative": counts['negative'],
            "neutral": counts['neutral'],
            "total": sum(counts.values()),
        }
        for course, counts in course_data.items()
    ]
    data.sort(key=lambda x: x['total'], reverse=True)

    return jsonify({"success": True, "data": data})


@dashboard_bp.route('/semesters')
def get_semester_trends():
    """GET /api/dashboard/semesters - Semester-wise feedback trends."""
    results = db.session.query(
        Feedback.semester,
        Feedback.predicted_sentiment,
        func.count(Feedback.id).label('count')
    ).group_by(Feedback.semester, Feedback.predicted_sentiment).all()

    from config import SEMESTERS
    sem_data = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
    for row in results:
        sem_data[row.semester][row.predicted_sentiment] = row.count

    data = [
        {
            "semester": sem,
            "positive": sem_data[sem]['positive'],
            "negative": sem_data[sem]['negative'],
            "neutral": sem_data[sem]['neutral'],
            "total": sum(sem_data[sem].values()),
        }
        for sem in SEMESTERS
    ]
    return jsonify({"success": True, "data": data})


@dashboard_bp.route('/categories')
def get_category_analysis():
    """GET /api/dashboard/categories - Academic category analysis."""
    results = db.session.query(
        Feedback.academic_category,
        Feedback.predicted_sentiment,
        func.count(Feedback.id).label('count')
    ).group_by(Feedback.academic_category, Feedback.predicted_sentiment).all()

    cat_data = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
    for row in results:
        cat_data[row.academic_category][row.predicted_sentiment] = row.count

    # Recent 10 feedback items
    recent = Feedback.query.order_by(Feedback.created_at.desc()).limit(10).all()

    return jsonify({
        "success": True,
        "categories": [
            {
                "category": cat,
                "positive": counts['positive'],
                "negative": counts['negative'],
                "neutral": counts['neutral'],
                "total": sum(counts.values()),
            }
            for cat, counts in cat_data.items()
        ],
        "recent_feedback": [f.to_dict() for f in recent],
    })
