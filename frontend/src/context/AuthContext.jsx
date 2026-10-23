import { createContext, useContext, useState, useEffect } from 'react'
import { api, getToken } from '../services/api'

const Ctx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (getToken()) {
      api('/api/auth/me').then(setUser).catch(() => localStorage.removeItem('fnds_token')).finally(() => setLoading(false))
    } else setLoading(false)
  }, [])

  const login = async (email, password) => {
    const t = await api('/api/auth/login', { method: 'POST', body: { email, password }, auth: false })
    localStorage.setItem('fnds_token', t.access_token)
    const u = await api('/api/auth/me')
    setUser(u)
  }
  const register = async (full_name, email, password, confirm_password) => {
    await api('/api/auth/register', { method: 'POST', body: { full_name, email, password, confirm_password }, auth: false })
    await login(email, password)
  }
  const logout = () => { localStorage.removeItem('fnds_token'); setUser(null) }
  const refresh = async () => { try { setUser(await api('/api/auth/me')) } catch {} }

  return <Ctx.Provider value={{ user, loading, login, register, logout, refresh, setUser }}>{children}</Ctx.Provider>
}

export const useAuth = () => useContext(Ctx)
