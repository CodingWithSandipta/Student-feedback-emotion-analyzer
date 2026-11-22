/**
 * Utility helpers for the Student Feedback Emotion Analyzer.
 */

// Emotion display config
export const EMOTION_CONFIG = {
  joy: { label: 'Joy', color: '#f59e0b', bg: 'bg-yellow-100', text: 'text-yellow-800', icon: '😊' },
  satisfaction: { label: 'Satisfaction', color: '#10b981', bg: 'bg-emerald-100', text: 'text-emerald-800', icon: '😌' },
  anger: { label: 'Anger', color: '#ef4444', bg: 'bg-red-100', text: 'text-red-800', icon: '😠' },
  sadness: { label: 'Sadness', color: '#3b82f6', bg: 'bg-blue-100', text: 'text-blue-800', icon: '😢' },
  fear: { label: 'Fear', color: '#8b5cf6', bg: 'bg-purple-100', text: 'text-purple-800', icon: '😨' },
  frustration: { label: 'Frustration', color: '#f97316', bg: 'bg-orange-100', text: 'text-orange-800', icon: '😤' },
  neutral: { label: 'Neutral', color: '#64748b', bg: 'bg-slate-100', text: 'text-slate-700', icon: '😐' },
}

export const SENTIMENT_CONFIG = {
  positive: { label: 'Positive', color: '#10b981', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', icon: '👍' },
  negative: { label: 'Negative', color: '#ef4444', bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', icon: '👎' },
  neutral: { label: 'Neutral', color: '#64748b', bg: 'bg-slate-50', text: 'text-slate-600', border: 'border-slate-200', icon: '➡️' },
}

export const EMOTION_CHART_COLORS = [
  '#f59e0b', '#10b981', '#ef4444', '#3b82f6', '#8b5cf6', '#f97316', '#64748b'
]

export const SEMESTERS = Array.from({ length: 8 }, (_, i) => `Semester ${i + 1}`)

export const ACADEMIC_CATEGORIES = [
  'Teaching Quality',
  'Faculty Behavior',
  'Course Curriculum',
  'Examination',
  'Assignments',
  'Infrastructure',
  'Laboratory',
  'General Feedback',
]

export const EMOTIONS = ['joy', 'satisfaction', 'anger', 'sadness', 'fear', 'frustration', 'neutral']

/**
 * Format a date string to a readable format.
 */
export function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Format confidence as percentage string.
 */
export function formatConfidence(value) {
  if (value == null) return 'N/A'
  return `${(value * 100).toFixed(1)}%`
}

/**
 * Get emotion display config.
 */
export function getEmotionConfig(emotion) {
  return EMOTION_CONFIG[emotion?.toLowerCase()] || EMOTION_CONFIG.neutral
}

/**
 * Get sentiment display config.
 */
export function getSentimentConfig(sentiment) {
  return SENTIMENT_CONFIG[sentiment?.toLowerCase()] || SENTIMENT_CONFIG.neutral
}

/**
 * Truncate text to maxLen characters.
 */
export function truncate(text, maxLen = 80) {
  if (!text) return ''
  return text.length > maxLen ? text.slice(0, maxLen) + '…' : text
}

/**
 * Capitalize first letter of a string.
 */
export function capitalize(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}
