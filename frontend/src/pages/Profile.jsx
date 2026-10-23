import { useState } from 'react'
import { api } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function Profile() {
  const { user, refresh } = useAuth()
  const [name, setName] = useState(user?.full_name || '')
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  const update = async (e) => {
    e.preventDefault()
    setErr(''); setMsg('')
    if (!name.trim()) { setErr('Please enter your full name.'); return }
    try {
      await api('/api/auth/profile', { method: 'PUT', body: { full_name: name } })
      await refresh()
      setMsg('Profile updated.')
    } catch (ex) { setErr(ex.message) }
  }

  return (
    <div className="container page">
      <h1>Profile</h1>
      {err && <div className="alert alert-error">{err}</div>}
      {msg && <div className="alert alert-ok">{msg}</div>}
      <div className="card">
        <form onSubmit={update}>
          <label>Full Name</label>
          <input value={name} onChange={e => setName(e.target.value)} />
          <label>Email</label>
          <input value={user?.email || ''} disabled />
          <p className="muted">Member since {user?.created_at?.slice(0, 10)} · {user?.analyses ?? 0} analyses</p>
          <button className="btn btn-primary">Save Changes</button>
        </form>
      </div>
    </div>
  )
}
