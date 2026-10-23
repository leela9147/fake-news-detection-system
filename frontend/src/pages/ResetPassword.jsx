import { useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { api } from '../services/api'

export default function ResetPassword() {
  const [params] = useSearchParams()
  const nav = useNavigate()
  const [pw, setPw] = useState('')
  const [pw2, setPw2] = useState('')
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    if (pw.length < 8) { setErr('Password must be at least 8 characters.'); return }
    if (pw !== pw2) { setErr('Passwords do not match.'); return }
    setBusy(true); setErr('')
    try {
      const r = await api('/api/auth/reset-password', { method: 'POST', body: { token: params.get('token') || '', new_password: pw, confirm_password: pw2 }, auth: false })
      setMsg(r.message)
      setTimeout(() => nav('/login'), 1500)
    } catch (ex) { setErr(ex.message) } finally { setBusy(false) }
  }

  return (
    <div className="container auth-page">
      <form className="card auth-card" onSubmit={submit}>
        <h2>Reset Password</h2>
        {err && <div className="alert alert-error">{err}</div>}
        {msg && <div className="alert alert-ok">{msg}</div>}
        <label>New Password</label>
        <input type="password" value={pw} onChange={e => setPw(e.target.value)} required />
        <label>Confirm New Password</label>
        <input type="password" value={pw2} onChange={e => setPw2(e.target.value)} required />
        <button className="btn btn-primary btn-block" disabled={busy}>{busy ? 'Updating...' : 'Reset Password'}</button>
      </form>
    </div>
  )
}
