"""
Label mapping for GoEmotions to 7-class emotion taxonomy.
Documents the mapping decisions for academic reproducibility.
"""

# Original GoEmotions labels (28 classes including neutral)
GOEMOTIONS_LABELS = [
    "admiration", "amusement", "anger", "annoyance", "approval",
    "caring", "confusion", "curiosity", "desire", "disappointment",
    "disapproval", "disgust", "embarrassment", "excitement", "fear",
    "gratitude", "grief", "joy", "love", "nervousness",
    "neutral", "optimism", "pride", "realization", "relief",
    "remorse", "sadness", "surprise",
]

# Target 7-class taxonomy
TARGET_EMOTIONS = ["joy", "satisfaction", "anger", "sadness", "fear", "frustration", "neutral"]

# Mapping: GoEmotions label -> our 7-class label
# Unmapped labels are explicitly excluded (not silently assigned)
LABEL_MAPPING = {
    # Joy cluster
    "joy": "joy",
    "amusement": "joy",
    "excitement": "joy",

    # Satisfaction cluster
    "approval": "satisfaction",
    "admiration": "satisfaction",
    "gratitude": "satisfaction",
    "love": "satisfaction",
    "optimism": "satisfaction",
    "relief": "satisfaction",
    "pride": "satisfaction",

    # Anger cluster
    "anger": "anger",
    "disgust": "anger",

    # Sadness cluster
    "sadness": "sadness",
    "grief": "sadness",
    "disappointment": "sadness",
    "remorse": "sadness",

    # Fear cluster
    "fear": "fear",
    "nervousness": "fear",

    # Frustration cluster
    "annoyance": "frustration",

    # Neutral
    "neutral": "neutral",

    # EXPLICITLY EXCLUDED (ambiguous or not fitting our taxonomy):
    # "caring" -> excluded (more behavioral, not a feedback emotion)
    # "confusion" -> excluded (cognitive state, not emotional)
    # "curiosity" -> excluded (cognitive, not emotional feedback tone)
    # "desire" -> excluded (not relevant to academic feedback)
    # "disapproval" -> excluded (overlaps with anger/frustration, ambiguous)
    # "embarrassment" -> excluded (rare, ambiguous in academic feedback)
    # "realization" -> excluded (cognitive state)
    # "surprise" -> excluded (ambiguous valence)
}

EXCLUDED_LABELS = {
    "caring", "confusion", "curiosity", "desire",
    "disapproval", "embarrassment", "realization", "surprise"
}

# Sentiment mapping derived from emotion predictions
SENTIMENT_FROM_EMOTION = {
    "joy": "positive",
    "satisfaction": "positive",
    "anger": "negative",
    "sadness": "negative",
    "fear": "negative",
    "frustration": "negative",
    "neutral": "neutral",
}


def map_goemotions_labels(label_list: list) -> str | None:
    """
    Map a list of GoEmotions labels to our 7-class taxonomy.

    Strategy for multi-label samples:
    1. If only one label and it's in our mapping -> use it.
    2. If multiple labels all map to the same target class -> use that class.
    3. If multiple labels map to different target classes -> exclude (ambiguous).
    4. If any label is in EXCLUDED_LABELS and it's the only label -> exclude.

    Returns:
        The target emotion string, or None if the sample should be excluded.
    """
    if not label_list:
        return None

    mapped = set()
    for label in label_list:
        if label in LABEL_MAPPING:
            mapped.add(LABEL_MAPPING[label])
        elif label in EXCLUDED_LABELS:
            # If this is the only label and it's excluded, skip
            if len(label_list) == 1:
                return None
            # Otherwise ignore this label and check remaining
        else:
            # Unknown label -> exclude
            return None

    if len(mapped) == 1:
        return mapped.pop()
    elif len(mapped) == 0:
        return None
    else:
        # Multiple conflicting target classes -> exclude
        return None


def get_sentiment(emotion: str) -> str:
    """Derive sentiment from predicted emotion."""
    return SENTIMENT_FROM_EMOTION.get(emotion.lower(), "neutral")
