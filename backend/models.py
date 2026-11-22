"""
SQLAlchemy database models.
"""
from datetime import datetime
from extensions import db


class Feedback(db.Model):
    """Stores student feedback submissions with predictions."""
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(100), nullable=True)
    course_name = db.Column(db.String(200), nullable=False, index=True)
    semester = db.Column(db.String(50), nullable=False, index=True)
    academic_category = db.Column(db.String(100), nullable=False, index=True)
    feedback_text = db.Column(db.Text, nullable=False)
    predicted_emotion = db.Column(db.String(50), nullable=False, index=True)
    predicted_sentiment = db.Column(db.String(20), nullable=False, index=True)
    confidence_score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self, include_text=True):
        data = {
            "id": self.id,
            "course_name": self.course_name,
            "semester": self.semester,
            "academic_category": self.academic_category,
            "predicted_emotion": self.predicted_emotion,
            "predicted_sentiment": self.predicted_sentiment,
            "confidence_score": round(self.confidence_score, 4),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_text:
            data["feedback_text"] = self.feedback_text
        # Only include student_id if it's not null/empty
        if self.student_id:
            data["student_id"] = self.student_id
        return data


class Course(db.Model):
    """Tracks unique course names."""
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(200), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "course_name": self.course_name}


class ModelInformation(db.Model):
    """Stores model metadata and performance metrics."""
    __tablename__ = "model_information"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_name = db.Column(db.String(200), nullable=False)
    model_version = db.Column(db.String(50), nullable=False)
    dataset_name = db.Column(db.String(200), nullable=False)
    accuracy = db.Column(db.Float, nullable=True)
    macro_f1 = db.Column(db.Float, nullable=True)
    training_date = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "dataset_name": self.dataset_name,
            "accuracy": self.accuracy,
            "macro_f1": self.macro_f1,
            "training_date": self.training_date.isoformat() if self.training_date else None,
        }
