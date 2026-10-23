export default function SourceCard({ s }) {
  return (
    <div className="source-card">
      <div className="source-card-head">
        <BadgeInline label={s.label} />
        <strong>{s.source}</strong>
        {s.date && <span className="muted">· {s.date}</span>}
      </div>
      <h4>{s.title}</h4>
      {s.excerpt && <p className="muted">{s.excerpt}{s.excerpt.length >= 280 ? '…' : ''}</p>}
      {s.url && <a href={s.url} target="_blank" rel="noreferrer">View original source →</a>}
    </div>
  )
}

function BadgeInline({ label }) {
  const cls = label === 'SUPPORTING' ? 'badge-real' : label === 'CONTRADICTING' ? 'badge-fake' : 'badge-review'
  const txt = label === 'SUPPORTING' ? 'Supports claim' : label === 'CONTRADICTING' ? 'Contradicts claim' : 'Not conclusive'
  return <span className={`badge ${cls}`}>{txt}</span>
}
