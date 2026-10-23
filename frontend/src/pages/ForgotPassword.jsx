import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    if (!email.trim()) { setErr('Please enter your email.'); return }
    setBusy(true); setErr(''); setMsg('')
    try {
      const r = await api('/api/auth/forgot-password', { method: 'POST', body: { email }, auth: false })
      setMsg(r.message + ' (In local development, check the backend console for the reset URL.)')
    } catch (ex) { setErr(ex.message) } finally { setBusy(false) }
  }

  return (
    <div className="container auth-page">
      <form className="card auth-card" onSubmit={submit}>
        <h2>Forgot Password</h2>
        {err && <div className="alert alert-error">{err}</div>}
        {msg && <div className="alert alert-ok">{msg}</div>}
        <label>Email</label>
        <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        <button className="btn btn-primary btn-block" disabled={busy}>{busy ? 'Sending...' : 'Send reset link'}</button>
        <div className="auth-links"><Link to="/login">Back to Login</Link></div>
      </form>
    </div>
  )
}
