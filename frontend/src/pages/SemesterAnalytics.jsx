import { useEffect, useState } from 'react'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { RefreshCw } from 'lucide-react'
import { getSemesterTrends } from '../services/api'
import { LoadingSpinner, ErrorState, EmptyState, SectionHeader } from '../components/UI'

export default function SemesterAnalytics() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await getSemesterTrends()
      setData(res.data.data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  if (loading) return <LoadingSpinner size="lg" text="Loading semester data..." />
  if (error) return <ErrorState message={error} onRetry={load} />

  const hasData = data.some(d => d.total > 0)

  return (
    <div className="space-y-6 animate-fade-in">
      <SectionHeader
        title="Semester Analytics"
        subtitle="Feedback volume and sentiment trends by semester"
        action={
          <button onClick={load} className="btn-secondary flex items-center gap-2">
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
        }
      />

      {!hasData ? (
        <div className="card">
          <EmptyState
            icon="📅"
            title="No semester data yet"
            description="Submit feedback across different semesters to see trends here."
          />
        </div>
      ) : (
        <>
          {/* Volume trend */}
          <div className="card">
            <h3 className="font-semibold text-slate-700 mb-4">Feedback Volume by Semester</h3>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={data} margin={{ top: 5, right: 20, left: -15, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="semester" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="total" fill="#6366f1" radius={[4,4,0,0]} name="Total Feedback" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Sentiment trend */}
          <div className="card">
            <h3 className="font-semibold text-slate-700 mb-4">Sentiment Trends by Semester</h3>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={data} margin={{ top: 5, right: 20, left: -15, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="semester" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="positive" stroke="#10b981" strokeWidth={2}
                  dot={{ fill: '#10b981', r: 4 }} name="Positive" />
                <Line type="monotone" dataKey="negative" stroke="#ef4444" strokeWidth={2}
                  dot={{ fill: '#ef4444', r: 4 }} name="Negative" />
                <Line type="monotone" dataKey="neutral" stroke="#64748b" strokeWidth={2}
                  dot={{ fill: '#64748b', r: 4 }} name="Neutral" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Summary table */}
          <div className="card">
            <h3 className="font-semibold text-slate-700 mb-4">Semester Summary</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="table-header">Semester</th>
                    <th className="table-header text-right">Total</th>
                    <th className="table-header text-right">Positive</th>
                    <th className="table-header text-right">Negative</th>
                    <th className="table-header text-right">Neutral</th>
                    <th className="table-header text-right">Pos%</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map(row => (
                    <tr key={row.semester} className="table-row">
                      <td className="table-cell font-medium">{row.semester}</td>
                      <td className="table-cell text-right font-semibold">{row.total}</td>
                      <td className="table-cell text-right text-emerald-600">{row.positive}</td>
                      <td className="table-cell text-right text-red-500">{row.negative}</td>
                      <td className="table-cell text-right text-slate-500">{row.neutral}</td>
                      <td className="table-cell text-right">
                        {row.total > 0 ? `${(row.positive/row.total*100).toFixed(0)}%` : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
