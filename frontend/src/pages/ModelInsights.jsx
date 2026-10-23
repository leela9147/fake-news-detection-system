import { useEffect, useState } from 'react'
import { api } from '../services/api'

export default function ModelInsights() {
  const [data, setData] = useState(null)
  const [err, setErr] = useState('')

  useEffect(() => {
    api('/api/model-performance').then(setData).catch(e => setErr(e.message))
  }, [])

  if (err) return <div className="container page"><div className="alert alert-error">{err}</div></div>
  if (!data) return <div className="container page">Loading model metrics...</div>

  const models = Object.entries(data.models || {})
  const metrics = ['accuracy', 'precision', 'recall', 'f1', 'false_positive_rate', 'false_negative_rate']
  const labels = { accuracy: 'Accuracy', precision: 'Precision', recall: 'Recall', f1: 'F1', false_positive_rate: 'FPR', false_negative_rate: 'FNR' }

  return (
    <div className="container page">
      <h1>Model Insights</h1>
      <p className="muted">Trained on {data.rows?.toLocaleString()} cleaned articles (FakeNews.csv + TrueNews.csv). Best model: <strong>{data.best_model}</strong>.</p>

      <div className="grid-3">
        {models.map(([name, m]) => (
          <div key={name} className="card">
            <h3>{name}</h3>
            {metrics.map(k => (
              <div key={k} className="metric-row">
                <span>{labels[k]}</span>
                <div className="metric-bar"><div style={{ width: `${(m[k] || 0) * 100}%` }} /></div>
                <strong>{(m[k] * 100).toFixed(1)}%</strong>
              </div>
            ))}
            <p className="muted">CV F1: {(m.cv_f1_mean * 100).toFixed(1)}% ± {(m.cv_f1_std * 100).toFixed(2)}%</p>
          </div>
        ))}
      </div>

      <h2>Confusion Matrices</h2>
      <div className="grid-3">
        {models.map(([name, m]) => {
          const [[tn, fp], [fn, tp]] = m.confusion_matrix
          return (
            <div key={name} className="card">
              <h4>{name}</h4>
              <table className="cm">
                <thead><tr><th></th><th>Predicted Real</th><th>Predicted Fake</th></tr></thead>
                <tbody>
                  <tr><td>Actually Real</td><td className="cm-good">{tn}</td><td className="cm-bad">{fp}</td></tr>
                  <tr><td>Actually Fake</td><td className="cm-bad">{fn}</td><td className="cm-good">{tp}</td></tr>
                </tbody>
              </table>
            </div>
          )
        })}
      </div>

      <h2>Uncertainty Threshold (best model)</h2>
      <div className="table-wrap card">
        <table>
          <thead><tr><th>Threshold</th><th>Coverage</th><th>Accuracy when confident</th></tr></thead>
          <tbody>
            {(data.uncertainty_sweep_best_model || []).map(s => (
              <tr key={s.threshold}>
                <td>{s.threshold}</td><td>{(s.coverage * 100).toFixed(1)}%</td>
                <td>{s.accuracy_when_confident ? (s.accuracy_when_confident * 100).toFixed(2) + '%' : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="muted">Below the confidence threshold, predictions are reported as “Needs Verification” instead of a forced REAL/FAKE answer.</p>
    </div>
  )
}
