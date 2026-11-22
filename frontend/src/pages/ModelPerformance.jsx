import { useEffect, useState } from 'react'
import { getModelMetrics } from '../services/api'
import { LoadingSpinner, ErrorState, SectionHeader } from '../components/UI'
import { AlertCircle, CheckCircle } from 'lucide-react'

const METRIC_COLORS = { joy:'bg-yellow-400', satisfaction:'bg-emerald-400', anger:'bg-red-400', sadness:'bg-blue-400', fear:'bg-purple-400', frustration:'bg-orange-400', neutral:'bg-slate-400' }

function MetricRow({ label, value, max = 1, color = 'bg-indigo-400' }) {
  const pct = Math.min(100, (value || 0) * 100)
  return (
    <div className="flex items-center gap-4">
      <span className="text-sm text-slate-600 w-24 font-medium capitalize">{label}</span>
      <div className="flex-1 h-2.5 bg-slate-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all duration-700`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-sm font-semibold text-slate-700 w-14 text-right">{((value || 0) * 100).toFixed(2)}%</span>
    </div>
  )
}

function PerClassTable({ perClass }) {
  if (!perClass) return null
  const classes = Object.keys(perClass)
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-100">
            <th className="table-header">Emotion</th>
            <th className="table-header text-right">Precision</th>
            <th className="table-header text-right">Recall</th>
            <th className="table-header text-right">F1-Score</th>
            <th className="table-header text-right">Support</th>
          </tr>
        </thead>
        <tbody>
          {classes.map(cls => {
            const m = perClass[cls]
            return (
              <tr key={cls} className="table-row">
                <td className="table-cell">
                  <span className={`badge ${METRIC_COLORS[cls] || 'bg-slate-400'} text-white`}>
                    {cls.charAt(0).toUpperCase() + cls.slice(1)}
                  </span>
                </td>
                <td className="table-cell text-right font-mono text-sm">{(m.precision * 100).toFixed(2)}%</td>
                <td className="table-cell text-right font-mono text-sm">{(m.recall * 100).toFixed(2)}%</td>
                <td className="table-cell text-right font-mono text-sm">{(m.f1_score * 100).toFixed(2)}%</td>
                <td className="table-cell text-right text-slate-500">{m.support}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

function ConfusionMatrixViz({ matrix, classNames }) {
  if (!matrix || !classNames) return null
  const maxVal = Math.max(...matrix.flat())
  return (
    <div className="overflow-x-auto">
      <div className="text-xs text-slate-500 mb-2">Rows: Actual, Columns: Predicted</div>
      <table className="text-xs border-collapse">
        <thead>
          <tr>
            <th className="p-1 text-slate-500"></th>
            {classNames.map(c => (
              <th key={c} className="p-2 text-slate-600 font-medium text-center capitalize" style={{ minWidth: 70 }}>
                {c.slice(0,4)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, i) => (
            <tr key={i}>
              <td className="p-2 text-slate-600 font-medium capitalize text-right pr-3">{classNames[i]}</td>
              {row.map((val, j) => {
                const intensity = maxVal > 0 ? val / maxVal : 0
                const bg = i === j
                  ? `rgba(99,102,241,${0.2 + intensity * 0.6})`
                  : `rgba(239,68,68,${intensity * 0.4})`
                return (
                  <td key={j} className="p-1 text-center font-mono border border-white"
                    style={{ backgroundColor: bg, minWidth: 70, minHeight: 36 }}>
                    <span className={`font-semibold ${val > 0 ? 'text-slate-800' : 'text-slate-300'}`}>{val}</span>
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function ModelPerformance() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await getModelMetrics()
        setData(res.data)
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <LoadingSpinner size="lg" text="Loading model metrics..." />
  if (error) return <ErrorState message={error} />

  const metrics = data?.metrics
  const config = data?.config

  if (!metrics) {
    return (
      <div className="space-y-6 animate-fade-in">
        <SectionHeader title="Model Performance" subtitle="Bi-LSTM evaluation metrics on held-out test data" />
        <div className="card text-center py-16">
          <AlertCircle className="w-12 h-12 text-amber-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-700 mb-2">Model Not Trained Yet</h3>
          <p className="text-slate-500 text-sm mb-4 max-w-md mx-auto">
            The Bi-LSTM model needs to be trained before performance metrics are available.
          </p>
          <div className="bg-slate-900 text-green-400 font-mono text-sm p-4 rounded-xl text-left max-w-md mx-auto">
            <p className="text-slate-400 mb-2"># Navigate to backend and run:</p>
            <p>cd backend</p>
            <p>python train_model.py</p>
          </div>
          <p className="text-xs text-slate-400 mt-4">
            Training requires internet access to download GoEmotions dataset (~10–30 min)
          </p>
        </div>
      </div>
    )
  }

  const { accuracy, macro_f1, weighted_f1, macro_precision, macro_recall,
    per_class_metrics, training_history, confusion_matrix, class_names, disclaimer } = metrics

  return (
    <div className="space-y-6 animate-fade-in">
      <SectionHeader title="Model Performance" subtitle="Bi-LSTM evaluation metrics on held-out GoEmotions test set" />

      {/* Disclaimer */}
      <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-xl p-4">
        <AlertCircle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-amber-800">Domain Limitation Notice</p>
          <p className="text-xs text-amber-700 mt-1">{disclaimer}</p>
        </div>
      </div>

      {/* Overall metrics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          { label: 'Test Accuracy', value: accuracy },
          { label: 'Macro F1', value: macro_f1 },
          { label: 'Weighted F1', value: weighted_f1 },
          { label: 'Macro Precision', value: macro_precision },
          { label: 'Macro Recall', value: macro_recall },
        ].map(m => (
          <div key={m.label} className="card text-center">
            <p className="text-xs text-slate-500 mb-1">{m.label}</p>
            <p className="text-2xl font-bold text-indigo-600">{((m.value||0)*100).toFixed(2)}%</p>
          </div>
        ))}
      </div>

      {/* Per-class metrics */}
      {per_class_metrics && (
        <div className="card">
          <h3 className="font-semibold text-slate-700 mb-4">Per-Class Performance</h3>
          <div className="space-y-3 mb-6">
            {Object.entries(per_class_metrics).map(([cls, m]) => (
              <MetricRow
                key={cls}
                label={cls}
                value={m.f1_score}
                color={METRIC_COLORS[cls] || 'bg-indigo-400'}
              />
            ))}
          </div>
          <PerClassTable perClass={per_class_metrics} />
        </div>
      )}

      {/* Confusion matrix */}
      {confusion_matrix && class_names && (
        <div className="card">
          <h3 className="font-semibold text-slate-700 mb-4">Confusion Matrix</h3>
          <ConfusionMatrixViz matrix={confusion_matrix} classNames={class_names} />
          <p className="text-xs text-slate-400 mt-4">
            Diagonal cells (blue) = correct predictions. Off-diagonal (red) = misclassifications.
            Darker = higher count.
          </p>
        </div>
      )}

      {/* Training history */}
      {training_history?.accuracy?.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-slate-700 mb-4">Training History</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm font-medium text-slate-600 mb-3">Accuracy</p>
              <div className="space-y-1">
                {training_history.accuracy.map((v, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs">
                    <span className="text-slate-400 w-16">Epoch {i+1}</span>
                    <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-indigo-400 rounded-full" style={{ width: `${v*100}%` }} />
                    </div>
                    <span className="text-slate-600 w-12 text-right">{(v*100).toFixed(1)}%</span>
                    {training_history.val_accuracy?.[i] != null && (
                      <>
                        <span className="text-slate-300">|</span>
                        <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div className="h-full bg-orange-400 rounded-full" style={{ width: `${training_history.val_accuracy[i]*100}%` }} />
                        </div>
                        <span className="text-slate-500 w-12 text-right">{(training_history.val_accuracy[i]*100).toFixed(1)}%</span>
                      </>
                    )}
                  </div>
                ))}
                <div className="flex gap-4 mt-2 text-xs text-slate-400">
                  <span className="flex items-center gap-1"><span className="w-3 h-1.5 bg-indigo-400 rounded inline-block"/>Train</span>
                  <span className="flex items-center gap-1"><span className="w-3 h-1.5 bg-orange-400 rounded inline-block"/>Val</span>
                </div>
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-600 mb-2">Model Config</p>
              {config && (
                <div className="bg-slate-50 rounded-xl p-4 text-xs space-y-2 font-mono">
                  <div><span className="text-slate-500">Architecture:</span> <span className="text-slate-800">Bidirectional LSTM</span></div>
                  <div><span className="text-slate-500">Embedding dim:</span> <span className="text-slate-800">{config.embedding_dim}</span></div>
                  <div><span className="text-slate-500">LSTM units:</span> <span className="text-slate-800">{config.lstm_units} (×2 Bi)</span></div>
                  <div><span className="text-slate-500">Dense units:</span> <span className="text-slate-800">{config.dense_units}</span></div>
                  <div><span className="text-slate-500">Dropout:</span> <span className="text-slate-800">{config.dropout_rate}</span></div>
                  <div><span className="text-slate-500">Vocab size:</span> <span className="text-slate-800">{config.vocab_size?.toLocaleString()}</span></div>
                  <div><span className="text-slate-500">Max seq len:</span> <span className="text-slate-800">{config.max_sequence_length}</span></div>
                  <div><span className="text-slate-500">Train samples:</span> <span className="text-slate-800">{config.train_samples?.toLocaleString()}</span></div>
                  <div><span className="text-slate-500">Test samples:</span> <span className="text-slate-800">{config.test_samples?.toLocaleString()}</span></div>
                  <div><span className="text-slate-500">Epochs trained:</span> <span className="text-slate-800">{config.actual_epochs}</span></div>
                  <div><span className="text-slate-500">Dataset:</span> <span className="text-slate-800">GoEmotions</span></div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
