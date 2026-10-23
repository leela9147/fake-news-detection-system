import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import Badge from '../components/Badge'

export default function History() {
  const [rows, setRows] = useState(null)
  const [err, setErr] = useState('')
  const [q, setQ] = useState('')
  const [assessment, setAssessment] = useState('')
  const [sort, setSort] = useState('new')

  const load = () => {
    const params = new URLSearchParams()
    if (q) params.set('q', q)
    if (assessment) params.set('assessment', assessment)
    if (sort) params.set('sort', sort)
    api('/api/predictions?' + params.toString()).then(setRows).catch(e => setErr(e.message))
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { load() }, [q, assessment, sort])

  return (
    <div className="container page">
      <h1>Prediction History</h1>
      <div className="filters card">
        <input placeholder="Search headline or result..." value={q} onChange={e => setQ(e.target.value)} />
        <select value={assessment} onChange={e => setAssessment(e.target.value)}>
          <option value="">All assessments</option>
          <option value="LIKELY REAL">Likely Real</option>
          <option value="LIKELY FAKE">Likely Fake</option>
          <option value="NEEDS VERIFICATION">Needs Verification</option>
        </select>
        <select value={sort} onChange={e => setSort(e.target.value)}>
          <option value="new">Newest first</option>
          <option value="old">Oldest first</option>
        </select>
      </div>
      {err && <div className="alert alert-error">{err}</div>}
      {rows && rows.length === 0 && (
        <div className="card empty-state">
          <h3>You haven't analyzed any news yet.</h3>
          <Link to="/analyze" className="btn btn-primary">Analyze Your First Article</Link>
        </div>
      )}
      {rows && rows.length > 0 && (
        <div className="table-wrap card">
          <table>
            <thead><tr><th>Headline</th><th>Result</th><th>Confidence</th><th>Final Assessment</th><th>Date</th><th></th></tr></thead>
            <tbody>
              {rows.map(r => (
                <tr key={r.id}>
                  <td data-label="Headline">{r.headline.slice(0, 80)}{r.headline.length > 80 ? '…' : ''}</td>
                  <td data-label="Result"><Badge value={r.ml_prediction} /></td>
                  <td data-label="Confidence">{r.ml_confidence}%</td>
                  <td data-label="Assessment"><Badge value={r.final_assessment} /></td>
                  <td data-label="Date">{r.created_at?.slice(0, 10)}</td>
                  <td><Link to={`/history/${r.id}`}>Open</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
