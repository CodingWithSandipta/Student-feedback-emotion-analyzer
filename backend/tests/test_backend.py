"""
Backend tests for the Student Feedback Emotion Analyzer.
Run from the backend directory: pytest tests/ -v
"""
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def app():
    """Create test Flask app with in-memory SQLite database."""
    import os
    os.environ['TESTING'] = 'true'

    from app import create_app
    from extensions import db as _db

    # Patch config to use in-memory DB
    with patch('config.DATABASE_URI', 'sqlite:///:memory:'):
        with patch('config.DATABASE_PATH', Path(':memory:')):
            app = create_app()
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
            app.config['TESTING'] = True

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_prediction():
    """Mock prediction result for tests that don't need real model."""
    return {
        "predicted_emotion": "joy",
        "predicted_sentiment": "positive",
        "confidence": 0.85,
        "emotion_probabilities": {
            "joy": 0.85,
            "satisfaction": 0.05,
            "anger": 0.02,
            "sadness": 0.02,
            "fear": 0.02,
            "frustration": 0.02,
            "neutral": 0.02,
        }
    }


# ============================================================
# 1. API Health Check
# ============================================================
class TestHealthCheck:
    def test_health_endpoint_returns_200_or_503(self, client):
        """Health endpoint must respond."""
        response = client.get('/api/health')
        assert response.status_code in [200, 503]
        data = json.loads(response.data)
        assert 'status' in data
        assert 'database_connected' in data
        assert 'model_loaded' in data

    def test_health_response_structure(self, client):
        """Health response has required fields."""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert 'api_version' in data


# ============================================================
# 2. Database Initialization
# ============================================================
class TestDatabaseInitialization:
    def test_tables_created(self, app):
        """Database tables are created on startup."""
        from extensions import db
        from models import Feedback, Course, ModelInformation
        with app.app_context():
            # Check tables exist by querying them
            assert Feedback.query.count() >= 0
            assert Course.query.count() >= 0
            assert ModelInformation.query.count() >= 0


# ============================================================
# 3. Feedback Submission
# ============================================================
class TestFeedbackSubmission:
    def test_valid_feedback_submission(self, client, mock_prediction):
        """Valid feedback returns 201 with prediction data."""
        with patch('routes.feedback.predict_emotion', return_value=mock_prediction):
            response = client.post('/api/analyze', json={
                "feedback_text": "The professor explained the concepts very clearly and I enjoyed the class.",
                "course_name": "Machine Learning",
                "semester": "Semester 3",
                "academic_category": "Teaching Quality",
            })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'predicted_emotion' in data
        assert 'predicted_sentiment' in data
        assert 'confidence' in data
        assert 'emotion_probabilities' in data
        assert 'feedback_id' in data

    def test_valid_feedback_with_student_id(self, client, mock_prediction):
        """Feedback with optional student_id is accepted."""
        with patch('routes.feedback.predict_emotion', return_value=mock_prediction):
            response = client.post('/api/analyze', json={
                "feedback_text": "Great course material and teaching style.",
                "course_name": "Data Science",
                "semester": "Semester 4",
                "academic_category": "Teaching Quality",
                "student_id": "STU001",
            })
        assert response.status_code == 201

    def test_empty_feedback_rejected(self, client):
        """Empty feedback text returns 400."""
        response = client.post('/api/analyze', json={
            "feedback_text": "",
            "course_name": "Math",
            "semester": "Semester 1",
            "academic_category": "Teaching Quality",
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_too_short_feedback_rejected(self, client):
        """Very short feedback returns 400."""
        response = client.post('/api/analyze', json={
            "feedback_text": "Bad",
            "course_name": "Math",
            "semester": "Semester 1",
            "academic_category": "Teaching Quality",
        })
        assert response.status_code == 400

    def test_too_long_feedback_rejected(self, client):
        """Feedback exceeding 2000 chars returns 400."""
        response = client.post('/api/analyze', json={
            "feedback_text": "x" * 2001,
            "course_name": "Math",
            "semester": "Semester 1",
            "academic_category": "Teaching Quality",
        })
        assert response.status_code == 400

    def test_missing_course_rejected(self, client):
        """Missing course name returns 400."""
        response = client.post('/api/analyze', json={
            "feedback_text": "Good teaching quality overall.",
            "course_name": "",
            "semester": "Semester 1",
            "academic_category": "Teaching Quality",
        })
        assert response.status_code == 400

    def test_invalid_semester_rejected(self, client):
        """Invalid semester returns 400."""
        response = client.post('/api/analyze', json={
            "feedback_text": "Good teaching quality overall.",
            "course_name": "Math",
            "semester": "Semester 99",
            "academic_category": "Teaching Quality",
        })
        assert response.status_code == 400

    def test_invalid_category_rejected(self, client):
        """Invalid academic category returns 400."""
        response = client.post('/api/analyze', json={
            "feedback_text": "Good teaching quality overall.",
            "course_name": "Math",
            "semester": "Semester 1",
            "academic_category": "InvalidCategory",
        })
        assert response.status_code == 400

    def test_no_json_body_rejected(self, client):
        """Non-JSON request returns 400."""
        response = client.post('/api/analyze', data="not json")
        assert response.status_code == 400


# ============================================================
# 4. Feedback Retrieval
# ============================================================
class TestFeedbackRetrieval:
    def _add_sample_feedback(self, client, mock_prediction, n=5):
        """Add n feedback records."""
        for i in range(n):
            with patch('routes.feedback.predict_emotion', return_value=mock_prediction):
                client.post('/api/analyze', json={
                    "feedback_text": f"This is sample feedback number {i} for testing purposes.",
                    "course_name": f"Course {i % 3}",
                    "semester": f"Semester {(i % 8) + 1}",
                    "academic_category": "Teaching Quality",
                })

    def test_feedback_list_returns_200(self, client, mock_prediction):
        """GET /api/feedback returns 200."""
        self._add_sample_feedback(client, mock_prediction)
        response = client.get('/api/feedback')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'feedback' in data
        assert 'pagination' in data

    def test_feedback_pagination(self, client, mock_prediction):
        """Pagination works correctly."""
        self._add_sample_feedback(client, mock_prediction, n=10)
        response = client.get('/api/feedback?page=1&per_page=3')
        data = json.loads(response.data)
        assert len(data['feedback']) <= 3
        assert data['pagination']['per_page'] == 3

    def test_feedback_filter_by_emotion(self, client, mock_prediction):
        """Filter by emotion works."""
        self._add_sample_feedback(client, mock_prediction)
        response = client.get('/api/feedback?emotion=joy')
        data = json.loads(response.data)
        for fb in data['feedback']:
            assert fb['predicted_emotion'] == 'joy'

    def test_feedback_filter_by_sentiment(self, client, mock_prediction):
        """Filter by sentiment works."""
        self._add_sample_feedback(client, mock_prediction)
        response = client.get('/api/feedback?sentiment=positive')
        data = json.loads(response.data)
        for fb in data['feedback']:
            assert fb['predicted_sentiment'] == 'positive'

    def test_get_feedback_by_id(self, client, mock_prediction):
        """GET /api/feedback/<id> returns specific record."""
        with patch('routes.feedback.predict_emotion', return_value=mock_prediction):
            post_resp = client.post('/api/analyze', json={
                "feedback_text": "Specific feedback for ID test.",
                "course_name": "Test Course",
                "semester": "Semester 1",
                "academic_category": "Teaching Quality",
            })
        fb_id = json.loads(post_resp.data)['feedback_id']

        response = client.get(f'/api/feedback/{fb_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['feedback']['id'] == fb_id

    def test_get_nonexistent_feedback_returns_404(self, client):
        """GET /api/feedback/999999 returns 404."""
        response = client.get('/api/feedback/999999')
        assert response.status_code == 404


# ============================================================
# 5. Feedback Deletion
# ============================================================
class TestFeedbackDeletion:
    def test_delete_feedback(self, client, mock_prediction):
        """DELETE /api/feedback/<id> removes the record."""
        with patch('routes.feedback.predict_emotion', return_value=mock_prediction):
            post_resp = client.post('/api/analyze', json={
                "feedback_text": "Feedback to be deleted for testing.",
                "course_name": "Test Course",
                "semester": "Semester 2",
                "academic_category": "Assignments",
            })
        fb_id = json.loads(post_resp.data)['feedback_id']

        delete_resp = client.delete(f'/api/feedback/{fb_id}')
        assert delete_resp.status_code == 200

        get_resp = client.get(f'/api/feedback/{fb_id}')
        assert get_resp.status_code == 404


# ============================================================
# 6. Dashboard
# ============================================================
class TestDashboard:
    def test_summary_empty_db(self, client):
        """Dashboard summary returns zeros for empty database."""
        response = client.get('/api/dashboard/summary')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total_feedback'] == 0

    def test_emotion_distribution_all_classes_present(self, client):
        """Emotion distribution includes all 7 classes."""
        response = client.get('/api/dashboard/emotions')
        data = json.loads(response.data)
        assert data['success'] is True
        emotions = {d['emotion'] for d in data['data']}
        expected = {'joy', 'satisfaction', 'anger', 'sadness', 'fear', 'frustration', 'neutral'}
        assert emotions == expected

    def test_sentiment_distribution(self, client):
        """Sentiment distribution includes all 3 sentiments."""
        response = client.get('/api/dashboard/sentiments')
        data = json.loads(response.data)
        sentiments = {d['sentiment'] for d in data['data']}
        assert sentiments == {'positive', 'negative', 'neutral'}

    def test_dashboard_with_data(self, client, mock_prediction):
        """Dashboard summary reflects actual DB records."""
        for i in range(3):
            with patch('routes.feedback.predict_emotion', return_value=mock_prediction):
                client.post('/api/analyze', json={
                    "feedback_text": f"Dashboard test feedback {i} with enough length.",
                    "course_name": "Analytics Course",
                    "semester": "Semester 5",
                    "academic_category": "Teaching Quality",
                })

        response = client.get('/api/dashboard/summary')
        data = json.loads(response.data)
        assert data['total_feedback'] == 3
        assert data['positive_count'] == 3  # joy is positive


# ============================================================
# 7. CSV Export
# ============================================================
class TestCSVExport:
    def test_csv_export_returns_csv(self, client, mock_prediction):
        """CSV export returns correct content type."""
        with patch('routes.feedback.predict_emotion', return_value=mock_prediction):
            client.post('/api/analyze', json={
                "feedback_text": "Export test feedback with enough characters.",
                "course_name": "Export Course",
                "semester": "Semester 1",
                "academic_category": "Teaching Quality",
            })
        response = client.get('/api/export/csv')
        assert response.status_code == 200
        assert 'text/csv' in response.content_type

    def test_csv_has_header_row(self, client, mock_prediction):
        """CSV export contains header row."""
        with patch('routes.feedback.predict_emotion', return_value=mock_prediction):
            client.post('/api/analyze', json={
                "feedback_text": "Another export test with sufficient length.",
                "course_name": "Export Course",
                "semester": "Semester 2",
                "academic_category": "Teaching Quality",
            })
        response = client.get('/api/export/csv')
        content = response.data.decode('utf-8')
        assert 'Feedback ID' in content
        assert 'Predicted Emotion' in content


# ============================================================
# 8. Sentiment Mapping
# ============================================================
class TestSentimentMapping:
    def test_sentiment_mapping_correctness(self):
        """Sentiment is correctly derived from emotion."""
        from ml.label_mapping import get_sentiment
        assert get_sentiment('joy') == 'positive'
        assert get_sentiment('satisfaction') == 'positive'
        assert get_sentiment('anger') == 'negative'
        assert get_sentiment('sadness') == 'negative'
        assert get_sentiment('fear') == 'negative'
        assert get_sentiment('frustration') == 'negative'
        assert get_sentiment('neutral') == 'neutral'


# ============================================================
# 9. Label Mapping
# ============================================================
class TestLabelMapping:
    def test_single_mapped_label(self):
        """Single mapped label returns correct emotion."""
        from ml.label_mapping import map_goemotions_labels
        assert map_goemotions_labels(['joy']) == 'joy'
        assert map_goemotions_labels(['anger']) == 'anger'
        assert map_goemotions_labels(['neutral']) == 'neutral'

    def test_excluded_label_returns_none(self):
        """Excluded labels return None."""
        from ml.label_mapping import map_goemotions_labels
        assert map_goemotions_labels(['curiosity']) is None
        assert map_goemotions_labels(['surprise']) is None

    def test_ambiguous_multilabel_returns_none(self):
        """Multi-label with conflicting target classes returns None."""
        from ml.label_mapping import map_goemotions_labels
        assert map_goemotions_labels(['joy', 'anger']) is None

    def test_multilabel_same_class_returns_class(self):
        """Multi-label all mapping to same class returns that class."""
        from ml.label_mapping import map_goemotions_labels
        # joy + amusement both -> joy
        assert map_goemotions_labels(['joy', 'amusement']) == 'joy'
        # admiration + gratitude both -> satisfaction
        assert map_goemotions_labels(['admiration', 'gratitude']) == 'satisfaction'

    def test_empty_list_returns_none(self):
        """Empty label list returns None."""
        from ml.label_mapping import map_goemotions_labels
        assert map_goemotions_labels([]) is None


# ============================================================
# 10. Missing Model Handling
# ============================================================
class TestMissingModel:
    def test_missing_model_returns_503(self, client):
        """If model is not loaded, /api/analyze returns 503."""
        with patch('ml.predict.is_model_loaded', return_value=False):
            with patch('routes.feedback.predict_emotion', side_effect=RuntimeError("Model not found")):
                response = client.post('/api/analyze', json={
                    "feedback_text": "Testing missing model handling scenario.",
                    "course_name": "Test",
                    "semester": "Semester 1",
                    "academic_category": "Teaching Quality",
                })
        assert response.status_code == 503


# ============================================================
# 11. Text Preprocessing
# ============================================================
class TestTextPreprocessing:
    def test_clean_text_lowercase(self):
        from ml.preprocessing import clean_text
        assert clean_text("HELLO WORLD") == "hello world"

    def test_clean_text_removes_urls(self):
        from ml.preprocessing import clean_text
        result = clean_text("Visit http://example.com for more info")
        assert 'http' not in result

    def test_clean_text_handles_none(self):
        from ml.preprocessing import clean_text
        assert clean_text(None) == ""

    def test_clean_text_strips_whitespace(self):
        from ml.preprocessing import clean_text
        assert clean_text("  hello  world  ") == "hello world"
