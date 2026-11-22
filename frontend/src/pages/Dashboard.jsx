import { useEffect, useState } from 'react'
import {
  BarChart, Bar, PieChart, Pie, Cell, Tooltip, Legend,
  ResponsiveContainer, XAxis, YAxis, CartesianGrid
} from 'recharts'
import {
  MessageSquare, TrendingUp, TrendingDown, Minus,
  Smile, BookOpen, RefreshCw
} from 'lucide-react'
import {
  getDashboardSummary, getEmotionDistribution,
  getSentimentDistribution, getCategoryAnalysis
} from '../services/api'
import { StatCard, EmotionBadge, SentimentBadge, LoadingSpinner, ErrorState, EmptyState } from '../components/UI'
import { EMOTION_CONFIG, formatDate, truncate } from '../utils/helpers'

const SENTIMENT_COLORS = { positive: '#10b981', negative: '#ef4444', neutral: '#64748b' }
const EMOTION_COLORS = ['#f59e0b', '#10b981', '#ef4444', '#3b82f6', '#8b5cf6', '#f97316', '#64748b']

function SentimentDonut({ data }) {
  const hasData = data?.some(d => d.count > 0)
  if (!hasData) return (
    <div className="flex items-center justify-center h-48 text-slate-400 text-sm">No data yet</div>
  )
  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={data} dataKey="count" nameKey="sentiment" cx="50%" cy="50%"
          innerRadius={55} outerRadius={85} paddingAngle={3}>
          {data.map((entry) => (
            <Cell key={entry.sentiment} fill={SENTIMENT_COLORS[entry.sentiment]} />
          ))}
        </Pie>
        <Tooltip formatter={(val, name) => [`${val} (${data.find(d=>d.sentiment===name)?.percentage}%)`, name]} />
        <Legend formatter={(v) => v.charAt(0).toUpperCase() + v.slice(1)} />
      </PieChart>
    </ResponsiveContainer>
  )
}

function EmotionBarChart({ data }) {
  const hasData = data?.some(d => d.count > 0)
  if (!hasData) return (
    <div className="flex items-center justify-center h-48 text-slate-400 text-sm">No data yet</div>
  )
  const chartData = data.map((d, i) => ({
    ...d,
    fill: EMOTION_COLORS[i % EMOTION_COLORS.length],
    label: EMOTION_CONFIG[d.emotion]?.label || d.emotion
  }))
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis dataKey="label" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {chartData.map((entry, i) => (
            <Cell key={i} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

function RecentFeedbackTable({ feedback }) {
  if (!feedback?.length) {
    return (
      <EmptyState
        icon="📝"
        title="No feedback yet"
        description="Submit some feedback using the Analyze Feedback page to see it here."
      />
    )
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-100">
            <th className="table-header">Course</th>
            <th className="table-header">Semester</th>
            <th className="table-header">Emotion</th>
            <th className="table-header">Sentiment</th>
            <th className="table-header">Date</th>
          </tr>
        </thead>
        <tbody>
          {feedback.map((f) => (
            <tr key={f.id} className="table-row">
              <td className="table-cell font-medium">{truncate(f.course_name, 25)}</td>
              <td className="table-cell text-slate-500">{f.semester}</td>
              <td className="table-cell"><EmotionBadge emotion={f.predicted_emotion} /></td>
              <td className="table-cell"><SentimentBadge sentiment={f.predicted_sentiment} /></td>
              <td className="table-cell text-slate-400 text-xs">{formatDate(f.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [emotions, setEmotions] = useState([])
  const [sentiments, setSentiments] = useState([])
  const [categories, setCategories] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadAll = async () => {
    setLoading(true)
    setError(null)
    try {
      const [sumRes, emoRes, sentRes, catRes] = await Promise.all([
        getDashboardSummary(),
        getEmotionDistribution(),
        getSentimentDistribution(),
        getCategoryAnalysis(),
      ])
      setSummary(sumRes.data)
      setEmotions(emoRes.data.data)
      setSentiments(sentRes.data.data)
      setCategories(catRes.data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadAll() }, [])

  if (loading) return <LoadingSpinner size="lg" text="Loading dashboard..." />
  if (error) return <ErrorState message={error} onRetry={loadAll} />

  return (
    <div className="space-y-6 animate-fade-in">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard title="Total Feedback" value={summary?.total_feedback ?? 0}
          icon={MessageSquare} color="indigo" />
        <StatCard title="Positive" value={`${summary?.positive_pct ?? 0}%`}
          subtitle={`${summary?.positive_count ?? 0} submissions`}
          icon={TrendingUp} color="emerald" />
        <StatCard title="Negative" value={`${summary?.negative_pct ?? 0}%`}
          subtitle={`${summary?.negative_count ?? 0} submissions`}
          icon={TrendingDown} color="red" />
        <StatCard title="Neutral" value={`${summary?.neutral_pct ?? 0}%`}
          subtitle={`${summary?.neutral_count ?? 0} submissions`}
          icon={Minus} color="slate" />
        <StatCard title="Top Emotion" value={EMOTION_CONFIG[summary?.most_common_emotion]?.label || summary?.most_common_emotion || 'N/A'}
          icon={Smile} color="violet" />
        <StatCard title="Courses" value={summary?.courses_analyzed ?? 0}
          icon={BookOpen} color="amber" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-700">Sentiment Distribution</h3>
            <button onClick={loadAll} className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors">
              <RefreshCw className="w-4 h-4 text-slate-400" />
            </button>
          </div>
          <SentimentDonut data={sentiments} />
        </div>
        <div className="card">
          <h3 className="font-semibold text-slate-700 mb-4">Emotion Distribution</h3>
          <EmotionBarChart data={emotions} />
        </div>
      </div>

      {/* Category Analysis */}
      {categories?.categories?.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-slate-700 mb-4">Academic Category Analysis</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={categories.categories} margin={{ top: 5, right: 10, left: -20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="category" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="positive" fill="#10b981" radius={[2,2,0,0]} name="Positive" />
              <Bar dataKey="negative" fill="#ef4444" radius={[2,2,0,0]} name="Negative" />
              <Bar dataKey="neutral" fill="#64748b" radius={[2,2,0,0]} name="Neutral" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Recent Feedback */}
      <div className="card">
        <h3 className="font-semibold text-slate-700 mb-4">Recent Submissions</h3>
        <RecentFeedbackTable feedback={categories?.recent_feedback} />
      </div>
    </div>
  )
}
