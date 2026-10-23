import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { useAuth } from '../context/AuthContext'
import Badge from '../components/Badge'

export default function Dashboard() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [err, setErr] = useState('')

  useEffect(() => {
    api('/api/dashboard').then(setData).catch(e => setErr(e.message))
  }, [])

  return (
    <div className="container page">
      <h1>Welcome, {user?.full_name}</h1>
      {err && <div className="alert alert-error">{err}</div>}
      {!data && !err && <p>Loading dashboard...</p>}
      {data && (
        <>
          <div className="grid-4">
            <Stat label="Articles Analyzed" value={data.total} />
            <Stat label="Likely Fake" value={data.likely_fake} />
            <Stat label="Likely Real" value={data.likely_real} />
            <Stat label="Needs Verification" value={data.needs_verification} />
          </div>
          <div className="dash-cols">
            <div className="card">
              <h3>Recent Analyses</h3>
              {data.recent.length === 0 && <p className="muted">No analyses yet.</p>}
              {data.recent.map(p => (
                <Link key={p.id} to={`/history/${p.id}`} className="recent-row">
                  <span className="recent-headline">{p.headline}</span>
                  <Badge value={p.final_assessment} />
                </Link>
              ))}
            </div>
            <div className="card">
              <h3>Quick Analyze</h3>
              <p className="muted">Check a new article right now.</p>
              <Link to="/analyze" className="btn btn-primary">Analyze News</Link>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

function Stat({ label, value }) {
  return <div className="card stat"><div className="stat-value">{value}</div><div className="muted">{label}</div></div>
}
