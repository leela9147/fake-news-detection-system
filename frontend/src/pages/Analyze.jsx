import { useState } from 'react'
import { api } from '../services/api'
import Badge from '../components/Badge'
import SourceCard from '../components/SourceCard'

export default function Analyze() {
  const [headline, setHeadline] = useState('')
  const [article, setArticle] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [showTech, setShowTech] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setErr('')
    if (!headline.trim()) { setErr('Please enter the news headline.'); return }
    if (!article.trim()) { setErr('Please enter the news article content.'); return }
    setBusy(true); setResult(null)
    try {
      const r = await api('/api/predict', { method: 'POST', body: { headline, article_content: article } })
      setResult(r)
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
    } catch (ex) { setErr(ex.message) } finally { setBusy(false) }
  }

  return (
    <div className="container page">
      <h1>Analyze News</h1>
      <form className="card" onSubmit={submit}>
        {err && <div className="alert alert-error">{err}</div>}
        <label>Headline <span className="req">*</span></label>
        <input value={headline} onChange={e => setHeadline(e.target.value)}
               placeholder="Enter the news headline" required />
        <label>Article Content <span className="req">*</span></label>
        <textarea rows={10} value={article} onChange={e => setArticle(e.target.value)}
                  placeholder="Paste the full article text here" required />
        <button className="btn btn-primary" disabled={busy}>
          {busy ? 'Analyzing article...' : 'Analyze News'}
        </button>
        {busy && <p className="muted">Classifying, explaining, and checking current sources. This can take up to a minute.</p>}
      </form>

      {result && (
        <div className="card result-card">
          <h2>News Analysis</h2>
          <div className="result-block">
            <h3>AI Classification</h3>
            <div className="big-badge"><Badge value={result.ml_prediction} /></div>
            <p><strong>{result.ml_confidence}%</strong> model confidence</p>
            <h4>Why did the AI give this result?</h4>
            <p>{result.simple_explanation}</p>
            {result.technical_explanation?.signals?.length > 0 && (
              <>
                <h4>Important signals noticed</h4>
                <ul>{result.technical_explanation.signals.map(s => <li key={s}>“{s}”</li>)}</ul>
              </>
            )}
            <button className="btn btn-ghost" onClick={() => setShowTech(!showTech)}>
              {showTech ? 'Hide Technical Details' : 'View Technical Details'}
            </button>
            {showTech && (
              <pre className="tech-box">{JSON.stringify(result.technical_explanation, null, 2)}</pre>
            )}
          </div>

          <div className="result-block">
            <h3>Real-World Verification</h3>
            <div className="big-badge"><Badge value={result.verification_status} /></div>
            <p>{result.verification_summary}</p>
            {result.sources?.length > 0 && (
              <div>
                <h4>Sources</h4>
                {result.sources.map((s, i) => <SourceCard key={i} s={s} />)}
              </div>
            )}
          </div>

          <div className="result-block">
            <h3>Final Assessment</h3>
            <div className="big-badge"><Badge value={result.final_assessment} /></div>
            <p>{result.technical_explanation?.final_assessment_explanation}</p>
          </div>

          <p className="disclaimer">
            Disclaimer: AI classification is based on learned patterns and available evidence.
            It does not guarantee factual truth.
          </p>
        </div>
      )}
    </div>
  )
}
