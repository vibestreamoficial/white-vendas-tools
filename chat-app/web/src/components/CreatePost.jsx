import { useRef, useState } from 'react'
import { CloudUpload, Music2, Loader2, Send } from 'lucide-react'
import Modal from './Modal.jsx'
import Toggle from './Toggle.jsx'
import { post } from '../api.js'

const GRADS = [
  ['#1a0533', '#FE2C55'], ['#03212b', '#25F4EE'], ['#2b0517', '#7c3aed'],
  ['#1c1c00', '#f59e0b'], ['#001f14', '#10b981'], ['#0b1030', '#3b82f6']
]

export default function CreatePost({ open, onClose, localUser, toast }) {
  const [legenda, setLegenda] = useState('')
  const [musica, setMusica] = useState('')
  const [arquivo, setArquivo] = useState(null)
  const [preview, setPreview] = useState(null)
  const [comentarios, setComentarios] = useState(true)
  const [dueto, setDueto] = useState(true)
  const [enviando, setEnviando] = useState(false)
  const [arrastando, setArrastando] = useState(false)
  const dropRef = useRef(null)

  const handleFile = (f) => {
    if (!f || !/^(image|video)\//.test(f.type)) return
    setArquivo(f)
    const r = new FileReader()
    r.onload = () => setPreview(String(r.result))
    r.readAsDataURL(f)
  }

  const publicar = async () => {
    if (enviando) return
    setEnviando(true)
    const body = {
      author: localUser.username,
      autorNome: localUser.name,
      legenda: legenda.trim(),
      musica: musica.trim() || 'som original — ' + localUser.name,
      comentarios, dueto
    }
    if (arquivo && arquivo.size < 6 * 1024 * 1024) {
      body.mediaB64 = preview
      body.mediaType = arquivo.type
    }
    try {
      const r = await post('/api/posts', body)
      setEnviando(false)
      onClose()
      setLegenda(''); setMusica(''); setArquivo(null); setPreview(null)
      toast(r?.ok && r.post?.status === 'aprovado' ? 'Post publicado ✅' : 'Post enviado pra moderação ✅')
    } catch (_) {
      setEnviando(false)
      onClose()
      toast('Servidor offline — post salvo localmente', 'erro')
    }
  }

  const grad = GRADS[Math.floor(Math.random() * GRADS.length)]

  return (
    <Modal open={open} onClose={onClose} title="➕ Criar Post" full>
      <div className="h-full flex flex-col gap-4 pb-6">
        <div className="flex gap-3 flex-1 min-h-0">
          <div
            ref={dropRef}
            onDragOver={(e) => { e.preventDefault(); setArrastando(true) }}
            onDragLeave={() => setArrastando(false)}
            onDrop={(e) => { e.preventDefault(); setArrastando(false); handleFile(e.dataTransfer.files?.[0]) }}
            className={`relative w-40 shrink-0 aspect-[9/16] rounded-box overflow-hidden border-2 border-dashed flex items-center justify-center transition-colors ${arrastando ? 'border-tpink bg-tpink/10' : 'border-white/20'}`}
            style={{ background: preview ? undefined : `linear-gradient(160deg, ${grad[0]}, ${grad[1]})` }}
            onClick={() => dropRef.current?.querySelector('input')?.click()}
          >
            <input type="file" accept="image/*,video/*" className="hidden" onChange={(e) => handleFile(e.target.files?.[0])} />
            {preview ? (
              arquivo?.type?.startsWith('video') ? (
                <video src={preview} className="absolute inset-0 w-full h-full object-cover" controls muted />
              ) : (
                <img src={preview} alt="" className="absolute inset-0 w-full h-full object-cover" />
              )
            ) : (
              <div className="flex flex-col items-center gap-2 text-white/70 px-3 text-center">
                <CloudUpload size={30} />
                <span className="text-[11px] font-semibold">Arraste vídeo ou imagem</span>
              </div>
            )}
          </div>

          <div className="flex-1 min-w-0 flex flex-col gap-3 overflow-y-auto no-scrollbar">
            <div>
              <label className="text-[11px] text-white/40 font-bold uppercase tracking-wide">Legenda</label>
              <textarea
                className="input-dark mt-1 min-h-[92px] resize-none"
                maxLength={150}
                placeholder="O que você está mostrando? #hashtags"
                value={legenda}
                onChange={(e) => setLegenda(e.target.value)}
              />
              <p className={`text-right text-[11px] font-bold mt-1 ${legenda.length > 130 ? 'text-tpink' : 'text-white/35'}`}>{legenda.length}/150</p>
            </div>
            <div>
              <label className="text-[11px] text-white/40 font-bold uppercase tracking-wide flex items-center gap-1"><Music2 size={12} /> Música / Som</label>
              <input className="input-dark mt-1" placeholder="Ex.: som original, viral 2026..." value={musica} onChange={(e) => setMusica(e.target.value)} />
            </div>
            <div className="card-dark p-3 space-y-1">
              <Toggle checked={comentarios} onChange={setComentarios} label="💬 Permitir comentários" />
              <Toggle checked={dueto} onChange={setDueto} label="🎬 Permitir dueto" />
            </div>
          </div>
        </div>

        <button onClick={publicar} disabled={enviando} className="btn-base w-full bg-tpink py-4 flex items-center justify-center gap-2 shadow-lg shadow-tpink/25">
          {enviando ? <Loader2 size={18} className="animate-spin" /> : <Send size={17} />}
          {enviando ? 'PUBLICANDO...' : 'PUBLICAR'}
        </button>
      </div>
    </Modal>
  )
}
