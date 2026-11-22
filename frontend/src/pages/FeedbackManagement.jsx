import { useState, useEffect, useCallback } from 'react'
import { Search, Download, Trash2, Eye, Filter, ChevronDown } from 'lucide-react'
import { getFeedback, deleteFeedback, getExportURL } from '../services/api'
import {
  EmotionBadge, SentimentBadge, LoadingSpinner, ErrorState,
  EmptyState, Pagination, SectionHeader
} from '../components/UI'
import { SEMESTERS, ACADEMIC_CATEGORIES, EMOTIONS, formatDate, formatConfidence, truncate } from '../utils/helpers'
import { useDebounce } from '../hooks/useHooks'

function FeedbackDetailModal({ feedback, onClose }) {
  if (!feedback) return null
  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6"
        onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-lg font-bold text-slate-800">Feedback Details</h3>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-400">✕</button>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div><span className="font-medium text-slate-600">Course:</span> <span className="text-slate-800">{feedback.course_name}</span></div>
            <div><span className="font-medium text-slate-600">Semester:</span> <span className="text-slate-800">{feedback.semester}</span></div>
            <div><span className="font-medium text-slate-600">Category:</span> <span className="text-slate-800">{feedback.academic_category}</span></div>
            <div><span className="font-medium text-slate-600">Date:</span> <span className="text-slate-800">{formatDate(feedback.created_at)}</span></div>
          </div>

          <div className="flex gap-2">
            <EmotionBadge emotion={feedback.predicted_emotion} />
            <SentimentBadge sentiment={feedback.predicted_sentiment} />
            <span className="badge bg-indigo-50 text-indigo-700">
              {formatConfidence(feedback.confidence_score)} confidence
            </span>
          </div>

          <div className="bg-slate-50 rounded-xl p-4">
            <p className="text-sm font-medium text-slate-600 mb-2">Feedback Text</p>
            <p className="text-slate-800 text-sm leading-relaxed whitespace-pre-wrap">{feedback.feedback_text}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

function DeleteConfirmModal({ onConfirm, onClose }) {
  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl max-w-sm w-full p-6" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-bold text-slate-800 mb-2">Delete Feedback?</h3>
        <p className="text-sm text-slate-500 mb-6">This action cannot be undone. The feedback record will be permanently removed.</p>
        <div className="flex gap-3">
          <button onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button onClick={onConfirm} className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold px-4 py-2.5 rounded-xl transition-all">
            Delete
          </button>
        </div>
      </div>
    </div>
  )
}

export default function FeedbackManagement() {
  const [feedbackList, setFeedbackList] = useState([])
  const [pagination, setPagination] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [search, setSearch] = useState('')
  const [filters, setFilters] = useState({ course: '', semester: '', emotion: '', sentiment: '', category: '' })
  const [sort, setSort] = useState('newest')
  const [page, setPage] = useState(1)

  const [viewFeedback, setViewFeedback] = useState(null)
  const [deleteId, setDeleteId] = useState(null)
  const [showFilters, setShowFilters] = useState(false)

  const debouncedSearch = useDebounce(search, 400)

  const loadFeedback = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = { page, per_page: 15, sort, search: debouncedSearch, ...filters }
      const res = await getFeedback(params)
      setFeedbackList(res.data.feedback)
      setPagination(res.data.pagination)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [page, sort, debouncedSearch, filters])

  useEffect(() => {
    setPage(1)
  }, [debouncedSearch, filters, sort])

  useEffect(() => {
    loadFeedback()
  }, [loadFeedback])

  const handleDelete = async () => {
    if (!deleteId) return
    try {
      await deleteFeedback(deleteId)
      setDeleteId(null)
      loadFeedback()
    } catch (e) {
      alert('Delete failed: ' + e.message)
    }
  }

  const handleExport = () => {
    const exportFilters = Object.fromEntries(
      Object.entries(filters).filter(([, v]) => v)
    )
    window.open(getExportURL(exportFilters), '_blank')
  }

  const updateFilter = (key, val) => {
    setFilters(prev => ({ ...prev, [key]: val }))
  }

  if (error) return <ErrorState message={error} onRetry={loadFeedback} />

  return (
    <div className="space-y-6 animate-fade-in">
      <SectionHeader
        title="Feedback Management"
        subtitle="Search, filter, view and manage all submitted feedback"
        action={
          <button onClick={handleExport} id="export-csv-btn" className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" /> Export CSV
          </button>
        }
      />

      {/* Search and filters */}
      <div className="card space-y-4">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              id="feedback-search"
              className="input-field pl-10"
              placeholder="Search feedback text..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <select id="sort-select" className="select-field w-36" value={sort} onChange={e => setSort(e.target.value)}>
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
          </select>
          <button
            className={`btn-secondary flex items-center gap-2 ${showFilters ? 'bg-indigo-50 border-indigo-200' : ''}`}
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="w-4 h-4" />
            Filters
            <ChevronDown className={`w-3 h-3 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
          </button>
        </div>

        {/* Expandable filters */}
        {showFilters && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 pt-2 border-t border-slate-100 animate-fade-in">
            <select id="filter-semester" className="select-field text-sm" value={filters.semester} onChange={e => updateFilter('semester', e.target.value)}>
              <option value="">All Semesters</option>
              {SEMESTERS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <select id="filter-emotion" className="select-field text-sm" value={filters.emotion} onChange={e => updateFilter('emotion', e.target.value)}>
              <option value="">All Emotions</option>
              {EMOTIONS.map(e => <option key={e} value={e}>{e.charAt(0).toUpperCase()+e.slice(1)}</option>)}
            </select>
            <select id="filter-sentiment" className="select-field text-sm" value={filters.sentiment} onChange={e => updateFilter('sentiment', e.target.value)}>
              <option value="">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="negative">Negative</option>
              <option value="neutral">Neutral</option>
            </select>
            <select id="filter-category" className="select-field text-sm" value={filters.category} onChange={e => updateFilter('category', e.target.value)}>
              <option value="">All Categories</option>
              {ACADEMIC_CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
            <button className="btn-secondary text-sm"
              onClick={() => setFilters({ course: '', semester: '', emotion: '', sentiment: '', category: '' })}>
              Clear Filters
            </button>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="card">
        {loading ? (
          <LoadingSpinner text="Loading feedback..." />
        ) : feedbackList.length === 0 ? (
          <EmptyState
            icon="🔍"
            title="No feedback found"
            description="Try adjusting your search terms or filters, or submit some feedback first."
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="table-header">Course</th>
                    <th className="table-header">Semester</th>
                    <th className="table-header">Category</th>
                    <th className="table-header">Feedback</th>
                    <th className="table-header">Emotion</th>
                    <th className="table-header">Sentiment</th>
                    <th className="table-header">Conf.</th>
                    <th className="table-header">Date</th>
                    <th className="table-header">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {feedbackList.map(f => (
                    <tr key={f.id} className="table-row">
                      <td className="table-cell font-medium max-w-[120px] truncate">{f.course_name}</td>
                      <td className="table-cell text-slate-500 whitespace-nowrap">{f.semester}</td>
                      <td className="table-cell text-slate-500 max-w-[100px] truncate">{f.academic_category}</td>
                      <td className="table-cell max-w-[200px]">
                        <span className="text-xs text-slate-600">{truncate(f.feedback_text, 60)}</span>
                      </td>
                      <td className="table-cell"><EmotionBadge emotion={f.predicted_emotion} /></td>
                      <td className="table-cell"><SentimentBadge sentiment={f.predicted_sentiment} /></td>
                      <td className="table-cell text-slate-500">{formatConfidence(f.confidence_score)}</td>
                      <td className="table-cell text-xs text-slate-400 whitespace-nowrap">{formatDate(f.created_at)}</td>
                      <td className="table-cell">
                        <div className="flex gap-1">
                          <button
                            onClick={() => setViewFeedback(f)}
                            className="p-1.5 hover:bg-indigo-50 text-indigo-500 rounded-lg transition-colors"
                            title="View details"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => setDeleteId(f.id)}
                            className="p-1.5 hover:bg-red-50 text-red-400 rounded-lg transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination pagination={pagination} onPageChange={setPage} />
          </>
        )}
      </div>

      {/* Modals */}
      {viewFeedback && <FeedbackDetailModal feedback={viewFeedback} onClose={() => setViewFeedback(null)} />}
      {deleteId && <DeleteConfirmModal onConfirm={handleDelete} onClose={() => setDeleteId(null)} />}
    </div>
  )
}
