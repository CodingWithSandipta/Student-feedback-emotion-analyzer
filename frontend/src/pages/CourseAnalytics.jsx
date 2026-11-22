import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { RefreshCw } from 'lucide-react'
import { getCourseAnalysis } from '../services/api'
import { LoadingSpinner, ErrorState, EmptyState, SectionHeader } from '../components/UI'

export default function CourseAnalytics() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await getCourseAnalysis()
      setData(res.data.data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  if (loading) return <LoadingSpinner size="lg" text="Loading course analytics..." />
  if (error) return <ErrorState message={error} onRetry={load} />

  return (
    <div className="space-y-6 animate-fade-in">
      <SectionHeader
        title="Course Analytics"
        subtitle="Sentiment analysis breakdown by course"
        action={
          <button onClick={load} className="btn-secondary flex items-center gap-2">
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
        }
      />

      {data.length === 0 ? (
        <div className="card">
          <EmptyState
            icon="📚"
            title="No course data yet"
            description="Submit feedback for different courses to see course-wise analysis here."
          />
        </div>
      ) : (
        <>
          {/* Chart */}
          <div className="card">
            <h3 className="font-semibold text-slate-700 mb-4">Course-wise Sentiment Comparison</h3>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={data} margin={{ top: 10, right: 20, left: -10, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="course" tick={{ fontSize: 11 }} angle={-30} textAnchor="end" interval={0} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="positive" fill="#10b981" radius={[3,3,0,0]} name="Positive" />
                <Bar dataKey="negative" fill="#ef4444" radius={[3,3,0,0]} name="Negative" />
                <Bar dataKey="neutral" fill="#64748b" radius={[3,3,0,0]} name="Neutral" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Table */}
          <div className="card">
            <h3 className="font-semibold text-slate-700 mb-4">Detailed Course Statistics</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="table-header">Course</th>
                    <th className="table-header text-right">Total</th>
                    <th className="table-header text-right">Positive</th>
                    <th className="table-header text-right">Negative</th>
                    <th className="table-header text-right">Neutral</th>
                    <th className="table-header">Sentiment Ratio</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map(row => {
                    const total = row.total || 1
                    const posW = (row.positive / total * 100).toFixed(0)
                    return (
                      <tr key={row.course} className="table-row">
                        <td className="table-cell font-medium">{row.course}</td>
                        <td className="table-cell text-right font-semibold">{row.total}</td>
                        <td className="table-cell text-right text-emerald-600">{row.positive}</td>
                        <td className="table-cell text-right text-red-500">{row.negative}</td>
                        <td className="table-cell text-right text-slate-500">{row.neutral}</td>
                        <td className="table-cell">
                          <div className="flex gap-0.5 h-5 rounded-full overflow-hidden w-32">
                            {row.positive > 0 && (
                              <div className="bg-emerald-400 h-full" style={{ width: `${row.positive/total*100}%` }} />
                            )}
                            {row.negative > 0 && (
                              <div className="bg-red-400 h-full" style={{ width: `${row.negative/total*100}%` }} />
                            )}
                            {row.neutral > 0 && (
                              <div className="bg-slate-300 h-full" style={{ width: `${row.neutral/total*100}%` }} />
                            )}
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
