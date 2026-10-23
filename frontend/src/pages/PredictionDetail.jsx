import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import Badge from '../components/Badge'
import SourceCard from '../components/SourceCard'

export default function PredictionDetail() {
  const { id } = useParams()
  const nav = useNavigate()
  const [p, setP] = useState(null)
  const [err, setErr] = useState('')
  const [showTech, setShowTech] = useState(false)

  useEffect(() => {
    api(`/api/predictions/${id}`).then(setP).catch(e => setErr(e.message))
  }, [id])

  const del = async () => {
    if (!confirm('Delete this analysis?')) return
    await api(`/api/predictions/${id}`, { method: 'DELETE' })
    nav('/history')
  }

  if (err) return <div className="container page"><div className="alert alert-error">{err}</div></div>
  if (!p) return <div className="container page">Loading...</div>

  return (
    <div className="container page">
      <button className="btn btn-ghost" onClick={() => nav(-1)}>← Back</button>
      <h1>{p.headline}</h1>
      <p className="muted">{p.created_at?.replace('T', ' ').slice(0, 19)}</p>

      <div className="card">
        <h3>AI Classification</h3>
        <Badge value={p.ml_prediction} /> <strong>{p.ml_confidence}% model confidence</strong>
        <p>{p.simple_explanation}</p>
        {p.technical_explanation?.signals?.length > 0 && (
          <ul>{p.technical_explanation.signals.map(s => <li key={s}>“{s}”</li>)}</ul>
        )}
        <button className="btn btn-ghost" onClick={() => setShowTech(!showTech)}>
          {showTech ? 'Hide Technical Details' : 'View Technical Details'}
        </button>
        {showTech && <pre className="tech-box">{JSON.stringify(p.technical_explanation, null, 2)}</pre>}
      </div>

      <div className="card">
        <h3>Real-World Verification</h3>
        <Badge value={p.verification_status} />
        <p>{p.verification_summary}</p>
        {p.sources?.map((s, i) => <SourceCard key={i} s={s} />)}
      </div>

      <div className="card">
        <h3>Final Assessment</h3>
        <Badge value={p.final_assessment} />
        <p>{p.technical_explanation?.final_assessment_explanation}</p>
      </div>

      <details className="card">
        <summary><strong>Original article</strong></summary>
        <p style={{ whiteSpace: 'pre-wrap' }}>{p.article_content}</p>
      </details>

      <button className="btn btn-danger" onClick={del}>Delete Analysis</button>
      <p className="disclaimer">AI classification is based on learned patterns and available evidence. It does not guarantee factual truth.</p>
    </div>
  )
}
