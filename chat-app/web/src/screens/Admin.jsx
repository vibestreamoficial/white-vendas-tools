import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard, Users, Film, Radio, Flag, Server, LogOut, Lock, User as UserIcon,
  Search, Ban, Trash2, Eye, Check, X, Pin, Loader2, ShieldCheck
} from 'lucide-react'
import Avatar from '../components/Avatar.jsx'
import { get, post } from '../api.js'
import { MOCK_USERS, MOCK_POSTS, MOCK_LIVES, MOCK_REPORTS, WEEK } from '../mock.js'

const MENU = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'usuarios', label: 'Usuários', icon: Users },
  { id: 'posts', label: 'Posts', icon: Film },
  { id: 'lives', label: 'Lives', icon: Radio },
  { id: 'denuncias', label: 'Denúncias', icon: Flag },
  { id: 'config', label: 'Config Servidor', icon: Server }
]

function Card({ icon, label, valor, cor }) {
  return (
    <div className="card-dark p-4 flex items-center gap-3">
      <div className="w-11 h-11 rounded-box flex items-center justify-center shrink-0" style={{ background: cor + '22', color: cor }}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-[11px] text-white/45 font-semibold uppercase tracking-wide truncate">{label}</p>
        <p className="font-black text-2xl leading-tight">{valor}</p>
      </div>
    </div>
  )
}

function Chart() {
  const max = Math.max(...WEEK.map((w) => w.n))
  return (
    <div className="card-dark p-4">
      <p className="font-bold text-sm mb-4">📈 Crescimento semanal (posts)</p>
      <div className="flex items-end gap-2 h-36">
        {WEEK.map((w, i) => (
          <div key={w.d} className="flex-1 flex flex-col items-center gap-1.5">
            <motion.div
              className="w-full rounded-t-md"
              style={{ background: i === 5 ? '#FE2C55' : 'linear-gradient(180deg,#25F4EE,#0e7d78)' }}
              initial={{ height: 0 }} animate={{ height: (w.n / max) * 100 + '%' }}
              transition={{ delay: 0.2 + i * 0.07, type: 'spring', damping: 20 }}
            />
            <span className="text-[10px] text-white/40">{w.d}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function Login({ onLogin }) {
  const [u, setU] = useState('')
  const [s, setS] = useState('')
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState('')

  const entrar = async () => {
    setCarregando(true)
    setErro('')
    try {
      const r = await post('/api/admin/login', { user: u, password: s })
      if (r.ok && r.token) {
        localStorage.setItem('wc_admin_token', r.token)
        onLogin()
        return
      }
      setErro(r.erro || 'Credenciais inválidas')
    } catch (_) {
      if (u === 'admin' && s === 'admin123') {
        localStorage.setItem('wc_admin_token', 'demo')
        onLogin()
      } else setErro('Servidor offline ou credenciais inválidas')
    }
    setCarregando(false)
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 bg-tblack">
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="w-full max-w-xs space-y-4">
        <div className="text-center space-y-1 mb-6">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-tpink to-tcyan flex items-center justify-center shadow-xl shadow-tpink/30 mb-3">
            <ShieldCheck size={32} />
          </div>
          <h1 className="font-black text-2xl">Painel Admin</h1>
          <p className="text-white/40 text-sm">White Chat — moderação</p>
        </div>
        <input className="input-dark" placeholder="Usuário" value={u} onChange={(e) => setU(e.target.value)} />
        <input className="input-dark" placeholder="Senha" type="password" value={s} onChange={(e) => setS(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && entrar()} />
        {erro && <p className="text-tpink text-xs font-semibold text-center">{erro}</p>}
        <button onClick={entrar} disabled={carregando} className="btn-base w-full bg-tpink py-3.5 flex items-center justify-center gap-2">
          {carregando ? <Loader2 size={17} className="animate-spin" /> : <Lock size={16} />} ENTRAR
        </button>
      </motion.div>
    </div>
  )
}

export default function Admin({ toast }) {
  const [token, setToken] = useState(localStorage.getItem('wc_admin_token'))
  const [menu, setMenu] = useState('dashboard')
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [posts, setPosts] = useState([])
  const [lives, setLives] = useState([])
  const [reports, setReports] = useState([])
  const [config, setConfig] = useState({ server: 'http://192.168.0.10:8000' })
  const [busca, setBusca] = useState('')
  const [filtroStatus, setFiltroStatus] = useState('todos')
  const [carregando, setCarregando] = useState(true)

  const adminGet = (p) => get(p)
  const adminPost = (p, b) => post(p, b)

  const carregar = async () => {
    setCarregando(true)
    try {
      const [s, u, p, l, r, c] = await Promise.all([
        adminGet('/api/admin/stats'), adminGet('/api/users'), adminGet('/api/posts?status=all'),
        adminGet('/api/lives'), adminGet('/api/reports'), adminGet('/api/config')
      ])
      if (s) setStats(s.stats); if (u) setUsers(u.users); if (p) setPosts(p.posts)
      if (l) setLives(l.lives); if (r) setReports(r.reports); if (c) setConfig(c.config)
    } catch (_) {
      setStats({ usuarios: MOCK_USERS.length, postsHoje: WEEK[5].n, lives: MOCK_LIVES.length, denuncias: MOCK_REPORTS.length })
      setUsers(MOCK_USERS); setPosts(MOCK_POSTS); setLives(MOCK_LIVES); setReports(MOCK_REPORTS)
    }
    setCarregando(false)
  }

  useEffect(() => { if (token) carregar() }, [token])

  if (!token) return <Login onLogin={() => setToken(localStorage.getItem('wc_admin_token'))} />

  const sair = () => { localStorage.removeItem('wc_admin_token'); setToken(null) }

  const filtrados = posts.filter((p) => filtroStatus === 'todos' || p.status === filtroStatus)
  const usuariosFiltrados = users.filter((u) => (u.username + ' ' + u.name).toLowerCase().includes(busca.toLowerCase()))

  const acaoPost = async (id, acao) => {
    const r = await adminPost(`/api/posts/${id}/${acao}`, {}).catch(() => null)
    if (r?.ok) {
      setPosts((ps) => ps.map((p) => p.id === id ? { ...p, ...(r.post || {}) } : p))
      toast(r.msg || 'Ação aplicada ✅')
    } else {
      setPosts((ps) => ps.map((p) => p.id === id ? { ...p, status: acao === 'approve' ? 'aprovado' : acao === 'reject' ? 'reprovado' : p.status, fixado: acao === 'pin' ? !p.fixado : p.fixado, ...(acao === 'delete' ? {} : {}) } : p).filter((p) => acao !== 'delete' || p.id !== id))
      toast('Ação aplicada (modo demo) ✅')
    }
  }

  const acaoUser = async (u, acao) => {
    const r = await adminPost(`/api/users/${u}/${acao}`, {}).catch(() => null)
    setUsers((us) => us.map((x) => x.username === u ? { ...x, status: acao === 'ban' ? 'banido' : acao === 'unban' ? 'ativo' : x.status } : x).filter((x) => acao !== 'delete' || x.username !== u))
    toast(r?.msg || 'Ação aplicada ✅')
  }

  const resolverDenuncia = async (id) => {
    await adminPost(`/api/reports/${id}/resolve`, {}).catch(() => {})
    setReports((rs) => rs.map((r) => r.id === id ? { ...r, status: 'resolvido' } : r))
    toast('Denúncia resolvida ✅')
  }

  return (
    <div className="min-h-screen bg-tblack flex">
      <aside className="hidden sm:flex flex-col w-60 shrink-0 border-r border-white/5 bg-tcard p-4 fixed inset-y-0">
        <div className="flex items-center gap-2.5 mb-6 px-1">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-tpink to-tcyan flex items-center justify-center font-black">W</div>
          <div>
            <p className="font-black leading-none">White Chat</p>
            <p className="text-[10px] text-white/40 mt-0.5">Painel Admin</p>
          </div>
        </div>
        <nav className="space-y-1 flex-1">
          {MENU.map((m) => (
            <button key={m.id} onClick={() => setMenu(m.id)} className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-box text-sm font-semibold transition-colors ${menu === m.id ? 'bg-tpink text-white' : 'text-white/60 hover:bg-white/5'}`}>
              <m.icon size={17} /> {m.label}
            </button>
          ))}
        </nav>
        <button onClick={sair} className="flex items-center gap-3 px-3 py-2.5 rounded-box text-sm font-semibold text-white/50 hover:bg-white/5 transition-colors">
          <LogOut size={17} /> Sair
        </button>
      </aside>

      <div className="flex-1 sm:ml-60">
        <header className="sticky top-0 z-20 bg-black/85 backdrop-blur border-b border-white/5 px-4 py-3 flex items-center justify-between">
          <div className="sm:hidden flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-tpink to-tcyan flex items-center justify-center font-black text-sm">W</div>
            <p className="font-black text-sm">Admin</p>
          </div>
          <p className="hidden sm:block font-black">{MENU.find((m) => m.id === menu)?.label}</p>
          <button onClick={sair} className="flex items-center gap-1.5 text-xs font-bold text-white/50 hover:text-white transition-colors sm:hidden">
            <LogOut size={15} /> Sair
          </button>
        </header>

        <main className="p-4 pb-24 sm:pb-6 space-y-4">
          {carregando && <div className="flex justify-center py-20"><Loader2 size={28} className="animate-spin text-tcyan" /></div>}

          {!carregando && menu === 'dashboard' && (
            <>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <Card icon={<Users size={20} />} label="Total Usuários" valor={stats?.usuarios ?? 0} cor="#25F4EE" />
                <Card icon={<Film size={20} />} label="Posts Hoje" valor={stats?.postsHoje ?? 0} cor="#FE2C55" />
                <Card icon={<Radio size={20} />} label="Lives Ativas" valor={stats?.lives ?? 0} cor="#10b981" />
                <Card icon={<Flag size={20} />} label="Denúncias Pend." valor={stats?.denuncias ?? 0} cor="#f59e0b" />
              </div>
              <Chart />
            </>
          )}

          {!carregando && menu === 'usuarios' && (
            <div className="space-y-3">
              <div className="relative">
                <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-white/30" />
                <input className="input-dark pl-10" placeholder="Buscar por username..." value={busca} onChange={(e) => setBusca(e.target.value)} />
              </div>
              <div className="card-dark overflow-x-auto">
                <table className="w-full text-sm min-w-[640px]">
                  <thead>
                    <tr className="text-left text-[11px] text-white/40 uppercase border-b border-white/5">
                      <th className="p-3">Avatar</th><th className="p-3">Username</th><th className="p-3">Nome</th>
                      <th className="p-3">Bio</th><th className="p-3">Status</th><th className="p-3">Data</th><th className="p-3">Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {usuariosFiltrados.map((u) => (
                      <tr key={u.username} className="border-b border-white/5 last:border-0">
                        <td className="p-3"><Avatar name={u.username} src={u.avatar} size={34} /></td>
                        <td className="p-3 font-bold">@{u.username}</td>
                        <td className="p-3 text-white/70">{u.name}</td>
                        <td className="p-3 text-white/40 text-xs max-w-[180px] truncate">{u.bio || '—'}</td>
                        <td className="p-3">
                          <span className={`text-[10px] font-black uppercase px-2 py-1 rounded-full ${u.status === 'banido' ? 'bg-tpink/20 text-tpink' : 'bg-emerald-500/15 text-emerald-400'}`}>
                            {u.status === 'banido' ? 'Banido' : 'Ativo'}
                          </span>
                        </td>
                        <td className="p-3 text-white/40 text-xs">{u.criado}</td>
                        <td className="p-3">
                          <div className="flex gap-1.5">
                            <button className="p-2 rounded-lg bg-white/5 hover:bg-white/10" title="Ver"><Eye size={14} /></button>
                            <button onClick={() => acaoUser(u.username, u.status === 'banido' ? 'unban' : 'ban')} className="p-2 rounded-lg bg-white/5 hover:bg-tpink/25 text-tpink" title={u.status === 'banido' ? 'Desbanir' : 'Banir'}><Ban size={14} /></button>
                            <button onClick={() => acaoUser(u.username, 'delete')} className="p-2 rounded-lg bg-white/5 hover:bg-red-500/25 text-red-400" title="Deletar"><Trash2 size={14} /></button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {!carregando && menu === 'posts' && (
            <div className="space-y-3">
              <div className="flex gap-2 overflow-x-auto no-scrollbar">
                {[['todos', 'Todos'], ['pendente', '⏳ Pendentes'], ['aprovado', '✅ Aprovados'], ['reprovado', '❌ Reprovados']].map(([id, l]) => (
                  <button key={id} onClick={() => setFiltroStatus(id)} className={`btn-base px-4 py-2 text-xs shrink-0 ${filtroStatus === id ? 'bg-tpink text-white' : 'bg-tinput text-white/60'}`}>{l}</button>
                ))}
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                <AnimatePresence>
                  {filtrados.map((p, i) => (
                    <motion.div key={p.id} layout className="card-dark overflow-hidden" initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.96 }}>
                      <div className="relative aspect-[9/16]" style={{ background: `linear-gradient(160deg, ${p.gradient?.[0] || '#1a0533'}, ${p.gradient?.[1] || '#FE2C55'})` }}>
                        {p.mediaUrl && <img src={p.mediaUrl} alt="" className="absolute inset-0 w-full h-full object-cover" />}
                        <span className="absolute inset-0 flex items-center justify-center text-4xl">{p.emoji || '🎬'}</span>
                        <span className={`absolute top-2 left-2 text-[10px] font-black uppercase px-2 py-1 rounded-full ${p.status === 'aprovado' ? 'bg-emerald-500 text-black' : p.status === 'pendente' ? 'bg-amber-400 text-black' : 'bg-tpink text-white'}`}>
                          {p.status === 'pendente' ? 'Pendente' : p.status === 'aprovado' ? 'Aprovado' : 'Reprovado'}
                        </span>
                        {p.fixado && <span className="absolute top-2 right-2 text-[10px] font-black bg-tcyan text-black px-2 py-1 rounded-full">📌 Fixado</span>}
                      </div>
                      <div className="p-3 space-y-2">
                        <div className="flex items-center justify-between">
                          <p className="text-xs font-bold truncate">@{p.author}</p>
                          <p className="text-[10px] text-white/35">{p.data}</p>
                        </div>
                        <p className="text-[11px] text-white/60 leading-snug line-clamp-2">{p.legenda || 'Sem legenda'}</p>
                        <p className="text-[10px] text-white/35">❤️ {Number(p.likes || 0).toLocaleString('pt-BR')}</p>
                        <div className="flex gap-1.5 flex-wrap">
                          <button onClick={() => acaoPost(p.id, 'approve')} className="p-1.5 rounded-lg bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/30" title="Aprovar"><Check size={14} /></button>
                          <button onClick={() => acaoPost(p.id, 'reject')} className="p-1.5 rounded-lg bg-white/5 text-white/50 hover:bg-white/15" title="Reprovar"><X size={14} /></button>
                          <button onClick={() => acaoPost(p.id, 'pin')} className={`p-1.5 rounded-lg ${p.fixado ? 'bg-tcyan/25 text-tcyan' : 'bg-white/5 text-white/50'}`} title="Fixar"><Pin size={14} /></button>
                          <button onClick={() => acaoPost(p.id, 'delete')} className="p-1.5 rounded-lg bg-red-500/15 text-red-400 hover:bg-red-500/30" title="Excluir"><Trash2 size={14} /></button>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
              {filtrados.length === 0 && (
                <div className="card-dark p-10 text-center text-white/40 space-y-2">
                  <p className="text-5xl">🗂️</p>
                  <p className="font-semibold">Nenhum post com esse status</p>
                </div>
              )}
            </div>
          )}

          {!carregando && menu === 'lives' && (
            <div className="card-dark overflow-x-auto">
              <table className="w-full text-sm min-w-[520px]">
                <thead>
                  <tr className="text-left text-[11px] text-white/40 uppercase border-b border-white/5">
                    <th className="p-3">Canal</th><th className="p-3">Streamer</th><th className="p-3">Viewers</th><th className="p-3">Desde</th><th className="p-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {(lives.length ? lives : MOCK_LIVES).map((l) => (
                    <tr key={l.canal} className="border-b border-white/5 last:border-0">
                      <td className="p-3 font-bold">📡 {l.canal}</td>
                      <td className="p-3"><div className="flex items-center gap-2"><Avatar name={l.user} size={26} />{l.user}</div></td>
                      <td className="p-3 text-white/60">{Number(l.viewers || 0).toLocaleString('pt-BR')}</td>
                      <td className="p-3 text-white/40 text-xs">{l.desde || l.inicio || '—'}</td>
                      <td className="p-3"><span className="flex items-center gap-1.5 text-[10px] font-black uppercase px-2 py-1 rounded-full bg-tpink/20 text-tpink w-fit"><span className="w-1.5 h-1.5 rounded-full bg-tpink pulse-live" /> AO VIVO</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {!carregando && menu === 'denuncias' && (
            <div className="space-y-2.5">
              {reports.length === 0 && (
                <div className="card-dark p-10 text-center text-white/40 space-y-2">
                  <p className="text-5xl">🕊️</p>
                  <p className="font-semibold">Nenhuma denúncia pendente</p>
                </div>
              )}
              {reports.map((r) => (
                <div key={r.id} className="card-dark p-4 flex flex-col sm:flex-row sm:items-center gap-3">
                  <div className="w-10 h-10 rounded-box bg-tpink/20 text-tpink flex items-center justify-center shrink-0"><Flag size={18} /></div>
                  <div className="flex-1 min-w-0">
                    <p className="font-bold text-sm">Post de @{r.autor}</p>
                    <p className="text-xs text-white/50">{r.motivo} • {r.data}</p>
                    <p className="text-[11px] text-white/35 mt-1 truncate">Post: {r.post}</p>
                  </div>
                  <span className={`text-[10px] font-black uppercase px-2.5 py-1 rounded-full w-fit ${r.status === 'resolvido' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-amber-400/15 text-amber-400'}`}>{r.status === 'resolvido' ? 'Resolvida' : 'Pendente'}</span>
                  {r.status !== 'resolvido' && (
                    <button onClick={() => resolverDenuncia(r.id)} className="btn-base bg-tpink px-4 py-2 text-xs shrink-0">RESOLVER</button>
                  )}
                </div>
              ))}
            </div>
          )}

          {!carregando && menu === 'config' && (
            <div className="card-dark p-5 max-w-md space-y-4">
              <div>
                <label className="text-[11px] text-white/40 font-bold uppercase tracking-wide">Endereço do servidor</label>
                <input className="input-dark mt-1" value={config.server} onChange={(e) => setConfig({ ...config, server: e.target.value })} />
                <p className="text-[11px] text-white/35 mt-2">Usado pelo app Android (Config.kt) e pela web pra apontar pra este servidor.</p>
              </div>
              <button onClick={async () => {
                const r = await adminPost('/api/config', config).catch(() => null)
                toast(r?.ok ? 'Configuração salva ✅' : 'Salvo (modo demo) ✅')
              }} className="btn-base w-full bg-tcyan text-black py-3.5">SALVAR CONFIGURAÇÃO</button>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
