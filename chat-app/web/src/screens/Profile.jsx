import { useRef, useState } from 'react'
import { Settings, Share2, Pencil, Link2, Check } from 'lucide-react'
import Avatar from '../components/Avatar.jsx'
import Modal from '../components/Modal.jsx'
import { post, base } from '../api.js'

export default function Profile({ localUser, setLocalUser, posts, toast }) {
  const [edit, setEdit] = useState(false)
  const [conf, setConf] = useState(false)
  const [avatar, setAvatar] = useState(localUser.avatar || '')
  const [username, setUsername] = useState(localUser.username)
  const [name, setName] = useState(localUser.name)
  const [bio, setBio] = useState(localUser.bio)
  const [servidor, setServidor] = useState(localStorage.getItem('wc_servidor') || base())
  const fileRef = useRef(null)

  const meus = posts.filter((p) => p.author === localUser.username)

  const salvarPerfil = async () => {
    const u = username.trim().toLowerCase().replace(/\s+/g, '')
    if (!u) return toast('Informe um username válido', 'erro')
    const perfil = { username: u, name: name.trim() || u, bio: bio.trim(), avatar }
    setLocalUser(perfil)
    localStorage.setItem('wc_user', JSON.stringify(perfil))
    setEdit(false)
    toast('Perfil atualizado ✅')
    try { await post('/api/profile', perfil) } catch (_) {}
  }

  const salvarServidor = () => {
    const v = servidor.trim().replace(/\/+$/, '')
    if (v) localStorage.setItem('wc_servidor', v)
    else localStorage.removeItem('wc_servidor')
    setConf(false)
    toast(v ? 'Servidor salvo: ' + v + ' ✅' : 'Servidor padrão restaurado ✅')
    setTimeout(() => window.location.reload(), 800)
  }

  const compartilhar = async () => {
    const txt = `@${localUser.username} • ${localUser.name} — White Chat 💬`
    try { await navigator.clipboard.writeText(txt); toast('Perfil copiado! 📋') }
    catch (_) { toast('Não foi possível copiar', 'erro') }
  }

  const lerArquivo = (f) => {
    if (!f) return
    const r = new FileReader()
    r.onload = () => setAvatar(String(r.result))
    r.readAsDataURL(f)
  }

  return (
    <div className="h-full overflow-y-auto no-scrollbar pb-28">
      <header className="sticky top-0 z-10 bg-black/80 backdrop-blur flex items-center justify-between px-4 py-3">
        <h1 className="text-lg font-black">Perfil</h1>
        <button onClick={() => setConf(true)} className="p-2 rounded-full hover:bg-white/10 transition-colors"><Settings size={20} /></button>
      </header>

      <div className="flex flex-col items-center px-4 pt-4">
        <div className="p-[3px] rounded-full bg-gradient-to-br from-tpink to-tcyan mb-3">
          <Avatar name={localUser.username} src={localUser.avatar} size={100} />
        </div>
        <p className="font-black text-lg">@{localUser.username}</p>
        <p className="font-semibold text-white/90">{localUser.name}</p>
        <p className="text-[13px] text-white/50 text-center mt-1.5 max-w-xs leading-snug">{localUser.bio}</p>
        <p className="flex items-center gap-1 text-[12px] text-tcyan mt-1.5"><Link2 size={12} /> white-chat.app/{localUser.username}</p>

        <div className="flex gap-8 my-5 text-center">
          {[['Seguindo', localUser.seguindo || 128], ['Seguidores', localUser.seguidores || 4520], ['Curtidas', localUser.curtidas || 12900]].map(([k, v]) => (
            <div key={k}>
              <p className="font-black text-lg">{Number(v).toLocaleString('pt-BR')}</p>
              <p className="text-[11px] text-white/40">{k}</p>
            </div>
          ))}
        </div>

        <div className="w-full grid grid-cols-2 gap-2 max-w-sm">
          <button onClick={() => setEdit(true)} className="btn-base bg-tinput py-3 flex items-center justify-center gap-2 text-sm">
            <Pencil size={15} /> Editar Perfil
          </button>
          <button onClick={compartilhar} className="btn-base bg-tinput py-3 flex items-center justify-center gap-2 text-sm">
            <Share2 size={15} /> Compartilhar
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-[2px] mt-6">
        {(meus.length ? meus : posts.slice(0, 6)).map((p) => (
          <div key={p.id} className="relative aspect-[9/16] overflow-hidden" style={{ background: `linear-gradient(160deg, ${p.gradient[0]}, ${p.gradient[1]})` }}>
            {p.mediaUrl && <img src={p.mediaUrl} alt="" className="absolute inset-0 w-full h-full object-cover" />}
            <span className="absolute inset-0 flex items-center justify-center text-3xl">{p.emoji}</span>
            <span className="absolute bottom-1.5 right-1.5 text-[10px] font-bold bg-black/60 rounded px-1.5 py-0.5">▶ {Number(p.views || p.likes).toLocaleString('pt-BR')}</span>
          </div>
        ))}
      </div>

      <Modal open={edit} onClose={() => setEdit(false)} title="✏️ Editar Perfil">
        <div className="space-y-4">
          <div className="flex flex-col items-center gap-2">
            <Avatar name={username} src={avatar} size={88} ring />
            <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={(e) => lerArquivo(e.target.files?.[0])} />
            <button onClick={() => fileRef.current?.click()} className="btn-base bg-tinput px-4 py-2 text-xs">📷 Enviar avatar</button>
          </div>
          <div>
            <label className="text-[11px] text-white/40 font-bold uppercase tracking-wide">Username</label>
            <input className="input-dark mt-1" value={username} onChange={(e) => setUsername(e.target.value)} />
          </div>
          <div>
            <label className="text-[11px] text-white/40 font-bold uppercase tracking-wide">Nome de exibição</label>
            <input className="input-dark mt-1" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div>
            <label className="text-[11px] text-white/40 font-bold uppercase tracking-wide">Bio</label>
            <textarea className="input-dark mt-1 min-h-[84px] resize-none" maxLength={300} value={bio} onChange={(e) => setBio(e.target.value)} />
          </div>
          <button onClick={salvarPerfil} className="btn-base w-full bg-tpink py-3.5 flex items-center justify-center gap-2">
            <Check size={17} /> SALVAR PERFIL
          </button>
        </div>
      </Modal>

      <Modal open={conf} onClose={() => setConf(false)} title="⚙️ Configurações">
        <div className="space-y-4">
          <div>
            <label className="text-[11px] text-white/40 font-bold uppercase tracking-wide">Servidor (API)</label>
            <input className="input-dark mt-1" value={servidor} onChange={(e) => setServidor(e.target.value)} placeholder="http://IP:8000" />
            <p className="text-[11px] text-white/35 mt-2">Usado pelo app pra buscar vídeos, lives e mensagens. Deixe vazio pra usar o mesmo endereço da página.</p>
          </div>
          <button onClick={salvarServidor} className="btn-base w-full bg-tcyan text-black py-3.5 flex items-center justify-center gap-2">
            <Check size={17} /> SALVAR SERVIDOR
          </button>
        </div>
      </Modal>
    </div>
  )
}
