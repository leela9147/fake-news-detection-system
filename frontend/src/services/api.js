
const BASE = 'http://127.0.0.1:8001'

export function getToken() { return localStorage.getItem('fnds_token') }

export async function api(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth && getToken()) headers['Authorization'] = `Bearer ${getToken()}`
  const res = await fetch(BASE + path, {
    method, headers, body: body ? JSON.stringify(body) : undefined,
  })
  let data = null
  try { data = await res.json() } catch { /* ignore */ }
  if (!res.ok) {
    let msg = 'Something went wrong.'
    if (data?.detail) {
      msg = typeof data.detail === 'string' ? data.detail
        : Array.isArray(data.detail) ? data.detail.map(d => d.msg).join(' ') : msg
    }
    throw new Error(msg)
  }
  return data
}
