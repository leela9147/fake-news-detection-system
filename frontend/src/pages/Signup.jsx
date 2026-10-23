import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Signup() {
  const { register } = useAuth()
  const nav = useNavigate()
  const [form, setForm] = useState({ full_name: '', email: '', password: '', confirm: '' })
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const set = k => e => setForm({ ...form, [k]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setErr('')
    if (!form.full_name.trim()) { setErr('Please enter your full name.'); return }
    if (!form.email.trim()) { setErr('Please enter your email.'); return }
    if (form.password.length < 8) { setErr('Password must be at least 8 characters.'); return }
    if (form.password !== form.confirm) { setErr('Passwords do not match.'); return }
    setBusy(true)
    try { await register(form.full_name, form.email, form.password, form.confirm); nav('/dashboard') }
    catch (ex) { setErr(ex.message) }
    finally { setBusy(false) }
  }

  return (
    <div className="container auth-page">
      <form className="card auth-card" onSubmit={submit}>
        <h2>Create your account</h2>
        {err && <div className="alert alert-error">{err}</div>}
        <label>Full Name</label>
        <input value={form.full_name} onChange={set('full_name')} required />
        <label>Email</label>
        <input type="email" value={form.email} onChange={set('email')} required />
        <label>Password</label>
        <input type="password" value={form.password} onChange={set('password')} required />
        <label>Confirm Password</label>
        <input type="password" value={form.confirm} onChange={set('confirm')} required />
        <button className="btn btn-primary btn-block" disabled={busy}>{busy ? 'Creating account...' : 'Sign Up'}</button>
        <div className="auth-links"><Link to="/login">Already have an account? Login</Link></div>
      </form>
    </div>
  )
}
