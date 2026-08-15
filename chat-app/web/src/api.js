const saved = () => localStorage.getItem('wc_servidor') || ''
export const base = () => saved() || window.location.origin

async function req(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) }
  const t = localStorage.getItem('wc_admin_token')
  if (t) headers.Authorization = 'Bearer ' + t
  try {
    const r = await fetch(base() + path, { ...opts, headers })
    if (!r.ok) throw new Error(r.statusText)
    return await r.json()
  } catch (e) {
    throw e
  }
}

export const get = (p) => req(p)
export const post = (p, body) => req(p, { method: 'POST', body: JSON.stringify(body || {}) })

export function avatarFor(nome) {
  const cores = ['#FE2C55', '#25F4EE', '#7c3aed', '#f59e0b', '#10b981', '#3b82f6']
  let h = 0
  for (const c of nome || '') h = (h * 31 + c.charCodeAt(0)) >>> 0
  return cores[h % cores.length]
}

export function fmtViewers(n) {
  if (n >= 1000) return (n / 1000).toFixed(1).replace('.0', '') + 'k'
  return String(n)
}
