import { useState, useRef } from 'react'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  ResponsiveContainer, Tooltip as RTooltip
} from 'recharts'
import { Send, Loader2, AlertCircle, CheckCircle2, Info } from 'lucide-react'
import { analyzesFeedback } from '../services/api'
import { SEMESTERS, ACADEMIC_CATEGORIES, EMOTION_CONFIG, formatDate, formatConfidence } from '../utils/helpers'
import { EmotionBadge, SentimentBadge, ConfidenceBar, SectionHeader } from '../components/UI'

const MAX_LEN = 2000
const MIN_LEN = 5

const EMOTION_ORDER = ['joy', 'satisfaction', 'anger', 'sadness', 'fear', 'frustration', 'neutral']
const EMOTION_COLORS = { joy:'#f59e0b', satisfaction:'#10b981', anger:'#ef4444', sadness:'#3b82f6', fear:'#8b5cf6', frustration:'#f97316', neutral:'#64748b' }

function ResultCard({ result }) {
  const emoConfig = EMOTION_CONFIG[result.predicted_emotion] || {}
  const probData = EMOTION_ORDER.map(e => ({
    emotion: emoConfig.label || e,
    value: (result.emotion_probabilities?.[e] || 0) * 100,
  }))

  return (
    <div className="card animate-fade-in border-2 border-indigo-100">
      <div className="flex items-center gap-2 mb-6">
        <CheckCircle2 className="w-5 h-5 text-indigo-600" />
        <h2 className="text-lg font-bold text-slate-800">Analysis Result</h2>
      </div>

      {/* Top result */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-slate-50 rounded-xl p-4 text-center">
          <p className="text-xs text-slate-500 mb-2 font-medium uppercase tracking-wide">Predicted Emotion</p>
          <EmotionBadge emotion={result.predicted_emotion} />
          <p className="text-2xl font-bold text-slate-800 mt-2">{emoConfig.icon}</p>
        </div>
        <div className="bg-slate-50 rounded-xl p-4 text-center">
          <p className="text-xs text-slate-500 mb-2 font-medium uppercase tracking-wide">Overall Sentiment</p>
          <SentimentBadge sentiment={result.predicted_sentiment} />
        </div>
        <div className="bg-slate-50 rounded-xl p-4 text-center">
          <p className="text-xs text-slate-500 mb-2 font-medium uppercase tracking-wide">Model Confidence</p>
          <p className="text-3xl font-bold text-indigo-600">{formatConfidence(result.confidence)}</p>
          <p className="text-xs text-slate-400 mt-1">Probability score</p>
        </div>
      </div>

      {/* Confidence disclaimer */}
      <div className="flex items-start gap-2 bg-amber-50 border border-amber-100 rounded-xl p-3 mb-6">
        <Info className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
        <p className="text-xs text-amber-700">
          Confidence represents the model's output probability, not a verified accuracy guarantee.
          Predictions may vary with different phrasings.
        </p>
      </div>

      {/* Emotion probabilities */}
      <div>
        <h3 className="text-sm font-semibold text-slate-700 mb-3">Emotion Probability Distribution</h3>
        <div className="space-y-2">
          {EMOTION_ORDER.map(e => (
            <ConfidenceBar
              key={e}
              label={EMOTION_CONFIG[e]?.label || e}
              value={result.emotion_probabilities?.[e] || 0}
              color={EMOTION_COLORS[e]}
            />
          ))}
        </div>
      </div>

      {/* Submission details */}
      <div className="mt-6 pt-4 border-t border-slate-100 grid grid-cols-2 md:grid-cols-4 gap-3 text-xs text-slate-500">
        <div><span className="font-medium text-slate-600">Course:</span> {result.course_name}</div>
        <div><span className="font-medium text-slate-600">Semester:</span> {result.semester}</div>
        <div><span className="font-medium text-slate-600">Category:</span> {result.academic_category}</div>
        <div><span className="font-medium text-slate-600">Submitted:</span> {formatDate(result.created_at)}</div>
      </div>
    </div>
  )
}

export default function AnalyzeFeedback() {
  const [form, setForm] = useState({
    student_id: '',
    course_name: '',
    semester: '',
    academic_category: '',
    feedback_text: '',
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [apiError, setApiError] = useState(null)
  const submitting = useRef(false)

  const validate = () => {
    const errs = {}
    if (!form.feedback_text.trim()) errs.feedback_text = 'Feedback text is required'
    else if (form.feedback_text.trim().length < MIN_LEN) errs.feedback_text = `Minimum ${MIN_LEN} characters`
    else if (form.feedback_text.trim().length > MAX_LEN) errs.feedback_text = `Maximum ${MAX_LEN} characters`
    if (!form.course_name.trim()) errs.course_name = 'Course name is required'
    if (!form.semester) errs.semester = 'Please select a semester'
    if (!form.academic_category) errs.academic_category = 'Please select a category'
    return errs
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (submitting.current) return
    const errs = validate()
    if (Object.keys(errs).length > 0) { setErrors(errs); return }
    setErrors({})
    setApiError(null)
    setResult(null)
    submitting.current = true
    setLoading(true)
    try {
      const res = await analyzesFeedback(form)
      setResult(res.data)
    } catch (err) {
      setApiError(err.message)
    } finally {
      setLoading(false)
      submitting.current = false
    }
  }

  const handleChange = (field, val) => {
    setForm(prev => ({ ...prev, [field]: val }))
    if (errors[field]) setErrors(prev => { const e = {...prev}; delete e[field]; return e })
  }

  const remaining = MAX_LEN - form.feedback_text.length

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <SectionHeader
        title="Analyze Student Feedback"
        subtitle="Submit feedback text for Bi-LSTM emotion and sentiment classification"
      />

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Form */}
        <div className="lg:col-span-3 card">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Student ID (optional) */}
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">
                Student ID <span className="text-slate-400 font-normal">(optional)</span>
              </label>
              <input
                id="student-id"
                type="text"
                className="input-field"
                placeholder="e.g. STU2024001 or leave blank"
                value={form.student_id}
                onChange={e => handleChange('student_id', e.target.value)}
              />
            </div>

            {/* Course */}
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">
                Course Name <span className="text-red-400">*</span>
              </label>
              <input
                id="course-name"
                type="text"
                className={`input-field ${errors.course_name ? 'border-red-300 ring-1 ring-red-200' : ''}`}
                placeholder="e.g. Machine Learning, DBMS"
                value={form.course_name}
                onChange={e => handleChange('course_name', e.target.value)}
              />
              {errors.course_name && <p className="text-red-500 text-xs mt-1">{errors.course_name}</p>}
            </div>

            {/* Semester + Category row */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1">
                  Semester <span className="text-red-400">*</span>
                </label>
                <select
                  id="semester"
                  className={`select-field ${errors.semester ? 'border-red-300' : ''}`}
                  value={form.semester}
                  onChange={e => handleChange('semester', e.target.value)}
                >
                  <option value="">Select semester</option>
                  {SEMESTERS.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
                {errors.semester && <p className="text-red-500 text-xs mt-1">{errors.semester}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1">
                  Category <span className="text-red-400">*</span>
                </label>
                <select
                  id="academic-category"
                  className={`select-field ${errors.academic_category ? 'border-red-300' : ''}`}
                  value={form.academic_category}
                  onChange={e => handleChange('academic_category', e.target.value)}
                >
                  <option value="">Select category</option>
                  {ACADEMIC_CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
                {errors.academic_category && <p className="text-red-500 text-xs mt-1">{errors.academic_category}</p>}
              </div>
            </div>

            {/* Feedback Text */}
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">
                Feedback Text <span className="text-red-400">*</span>
              </label>
              <textarea
                id="feedback-text"
                className={`textarea-field min-h-[140px] ${errors.feedback_text ? 'border-red-300 ring-1 ring-red-200' : ''}`}
                placeholder="Write your feedback about the course, faculty, facilities, examinations, etc..."
                value={form.feedback_text}
                onChange={e => handleChange('feedback_text', e.target.value)}
                rows={5}
              />
              <div className="flex justify-between mt-1">
                {errors.feedback_text
                  ? <p className="text-red-500 text-xs">{errors.feedback_text}</p>
                  : <span />
                }
                <span className={`text-xs ${remaining < 100 ? 'text-amber-500' : 'text-slate-400'}`}>
                  {remaining} chars remaining
                </span>
              </div>
            </div>

            {/* API error */}
            {apiError && (
              <div className="flex items-start gap-2 bg-red-50 border border-red-200 rounded-xl p-3">
                <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-red-700">{apiError}</p>
              </div>
            )}

            <button
              type="submit"
              id="analyze-btn"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {loading ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing...</>
              ) : (
                <><Send className="w-4 h-4" /> Analyze Feedback</>
              )}
            </button>
          </form>
        </div>

        {/* Info panel */}
        <div className="lg:col-span-2 space-y-4">
          <div className="card bg-indigo-50 border-indigo-100">
            <h3 className="font-semibold text-indigo-800 mb-3 text-sm">About the Model</h3>
            <ul className="space-y-2 text-xs text-indigo-700">
              <li>✦ Bidirectional LSTM architecture</li>
              <li>✦ Trained on GoEmotions dataset</li>
              <li>✦ Classifies 7 emotion categories</li>
              <li>✦ Derives sentiment from emotion</li>
              <li>✦ Shows confidence probabilities</li>
            </ul>
          </div>
          <div className="card">
            <h3 className="font-semibold text-slate-700 mb-3 text-sm">Emotion Categories</h3>
            <div className="space-y-1.5">
              {Object.entries(EMOTION_CONFIG).map(([key, cfg]) => (
                <div key={key} className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${cfg.bg} ${cfg.text}`}>
                    {cfg.icon} {cfg.label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Result card */}
      {result && <ResultCard result={result} />}
    </div>
  )
}
