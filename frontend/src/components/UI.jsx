import { getEmotionConfig, getSentimentConfig, formatConfidence } from '../utils/helpers'

/**
 * Reusable KPI stat card.
 */
export function StatCard({ title, value, subtitle, icon: Icon, color = 'indigo', trend }) {
  const colorMap = {
    indigo: 'bg-indigo-50 text-indigo-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    red: 'bg-red-50 text-red-600',
    slate: 'bg-slate-50 text-slate-600',
    amber: 'bg-amber-50 text-amber-600',
    violet: 'bg-violet-50 text-violet-600',
  }
  return (
    <div className="kpi-card">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-500">{title}</span>
        {Icon && (
          <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${colorMap[color]}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>
      <div className="mt-2">
        <span className="text-3xl font-bold text-slate-800">{value}</span>
        {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
      </div>
    </div>
  )
}

/**
 * Emotion badge chip.
 */
export function EmotionBadge({ emotion }) {
  const config = getEmotionConfig(emotion)
  return (
    <span className={`emotion-chip ${config.bg} ${config.text}`}>
      {config.icon} {config.label}
    </span>
  )
}

/**
 * Sentiment badge.
 */
export function SentimentBadge({ sentiment }) {
  const config = getSentimentConfig(sentiment)
  const cls = {
    positive: 'badge-positive',
    negative: 'badge-negative',
    neutral: 'badge-neutral',
  }[sentiment] || 'badge-neutral'
  return (
    <span className={`badge ${cls}`}>
      {config.icon} {config.label}
    </span>
  )
}

/**
 * Loading spinner.
 */
export function LoadingSpinner({ size = 'md', text }) {
  const sizeMap = { sm: 'w-5 h-5', md: 'w-8 h-8', lg: 'w-12 h-12' }
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8">
      <div className={`${sizeMap[size]} animate-spin rounded-full border-3 border-indigo-200 border-t-indigo-600`}
        style={{ borderWidth: '3px' }}
      />
      {text && <p className="text-sm text-slate-500">{text}</p>}
    </div>
  )
}

/**
 * Error state display.
 */
export function ErrorState({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12 text-center">
      <div className="w-12 h-12 rounded-full bg-red-50 flex items-center justify-center">
        <span className="text-2xl">⚠️</span>
      </div>
      <p className="text-slate-600 font-medium">{message || 'Something went wrong'}</p>
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary text-sm px-4 py-2">
          Try Again
        </button>
      )}
    </div>
  )
}

/**
 * Empty state display.
 */
export function EmptyState({ icon = '📭', title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <span className="text-5xl">{icon}</span>
      <h3 className="text-lg font-semibold text-slate-700">{title}</h3>
      {description && <p className="text-sm text-slate-400 max-w-sm">{description}</p>}
      {action}
    </div>
  )
}

/**
 * Confidence bar visualization.
 */
export function ConfidenceBar({ label, value, color = '#6366f1', maxVal = 1 }) {
  const pct = Math.min(100, (value / maxVal) * 100)
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-slate-600 font-medium capitalize">{label}</span>
        <span className="text-slate-500">{(value * 100).toFixed(1)}%</span>
      </div>
      <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  )
}

/**
 * Section header component.
 */
export function SectionHeader({ title, subtitle, action }) {
  return (
    <div className="flex items-center justify-between mb-6">
      <div>
        <h2 className="text-xl font-bold text-slate-800">{title}</h2>
        {subtitle && <p className="text-sm text-slate-500 mt-0.5">{subtitle}</p>}
      </div>
      {action}
    </div>
  )
}

/**
 * Pagination controls.
 */
export function Pagination({ pagination, onPageChange }) {
  if (!pagination || pagination.pages <= 1) return null
  const { page, pages, has_prev, has_next } = pagination

  return (
    <div className="flex items-center justify-between pt-4 border-t border-slate-100">
      <span className="text-sm text-slate-500">
        Page {page} of {pages} · {pagination.total} records
      </span>
      <div className="flex gap-2">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={!has_prev}
          className="btn-secondary text-sm px-4 py-1.5 disabled:opacity-40"
        >
          Previous
        </button>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={!has_next}
          className="btn-secondary text-sm px-4 py-1.5 disabled:opacity-40"
        >
          Next
        </button>
      </div>
    </div>
  )
}
