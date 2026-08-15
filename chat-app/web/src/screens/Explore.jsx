import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Radio, Video, Eye, Square, Users, Mic } from 'lucide-react'
import Avatar from '../components/Avatar.jsx'
import { fmtViewers, get, post } from '../api.js'
import { MOCK_LIVES } from '../mock.js'

const STUN = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] }

export default function Explore({ lives, setLives, localUser, toast }) {
  const [canal, setCanal] = useState('canal1')
  const [nome, setNome] = useState(localUser.name || 'Visitante')
  const [modo, setModo] = useState('none') // none | streamer | viewer
  const [status, setStatus] = useState('Escolha um canal e toque em transmitir ou assistir.')
  const [online, setOnline] = useState(false)

  const streamRef = useRef(null)
  const pcRef = useRef(null)
  const pcsRef = useRef({})
  const meuId = useRef(Math.random().toString(36).slice(2, 10))
  const sinalId = useRef(0)
  const vRef = useRef(null)
  const vRemoto = useRef(null)

  const sinal = async (tipo, payload) =>
    post('/api/signal', { room: 'live:' + canal, from: nome || 'anonimo', type: tipo, payload }).catch(() => {})

  useEffect(() => {
    if (modo === 'none') return
    const iv = setInterval(async () => {
      try {
        const lista = await get('/api/signal?room=' + encodeURIComponent('live:' + canal) + '&after=' + sinalId.current)
        for (const s of lista || []) {
          sinalId.current = Math.max(sinalId.current, s.id)
          tratarSinal(s)
        }
      } catch (_) {}
    }, 1400)
    return () => clearInterval(iv)
  }, [modo, canal])

  function tratarSinal(s) {
    const t = s.tipo, p = s.payload || {}
    if (t === 'live' && p.on && modo === 'viewer') setStatus('📺 Live encontrada no canal! Conectando...')
    if (t === 'join' && modo === 'streamer') atenderViewer(p.v)
    if (t === 'offer' && modo === 'viewer' && p.v === meuId.current) responder(p.i, p.o)
    if (t === 'answer' && modo === 'streamer') finalizar(p.i, p.o)
    if (t === 'stop') parar(true)
  }

  async function transmitir() {
    if (modo === 'streamer') return
    setModo('streamer')
    setStatus('Solicitando câmera...')
    try {
      const st = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      streamRef.current = st
      if (vRef.current) { vRef.current.srcObject = st; vRef.current.style.display = 'block' }
      setOnline(true)
      setStatus(`📡 Live NO AR no canal ${canal}. Compartilhe para assistirem!`)
      await sinal('live', { on: true, u: nome })
      post('/api/lives', { canal, user: nome, on: true }).catch(() => {})
    } catch (e) {
      setModo('none')
      setStatus('❌ Câmera negada: ' + e.message)
    }
  }

  async function atenderViewer(v) {
    const vp = new RTCPeerConnection(STUN)
    streamRef.current?.getTracks().forEach((t) => vp.addTrack(t, streamRef.current))
    const offerId = Math.random().toString(36).slice(2, 10)
    const desc = await vp.createOffer()
    await vp.setLocalDescription(desc)
    await new Promise((r) => setTimeout(r, 900))
    pcsRef.current[offerId] = vp
    await sinal('offer', { v, i: offerId, o: btoa(vp.localDescription.sdp) })
  }

  async function finalizar(i, o) {
    const vp = pcsRef.current[i]
    if (!vp) return
    try { await vp.setRemoteDescription({ type: 'answer', sdp: atob(o) }) } catch (e) { setStatus('Erro de conexão: ' + e.message) }
  }

  async function assistir() {
    setModo('viewer')
    setStatus('Procurando live no canal ' + canal + '...')
    await sinal('join', { v: meuId.current, u: nome })
  }

  async function responder(i, o) {
    try {
      const pc = new RTCPeerConnection(STUN)
      pc.ontrack = (e) => { if (vRemoto.current) { vRemoto.current.srcObject = e.streams[0]; vRemoto.current.style.display = 'block' } }
      pcRef.current = pc
      await pc.setRemoteDescription({ type: 'offer', sdp: atob(o) })
      const desc = await pc.createAnswer()
      await pc.setLocalDescription(desc)
      await new Promise((r) => setTimeout(r, 900))
      await sinal('answer', { i, o: btoa(desc.sdp) })
      setStatus('📺 Conectado à live!')
    } catch (e) {
      setStatus('❌ Não foi possível entrar: ' + e.message)
    }
  }

  async function parar(porSinal) {
    if (modo === 'streamer' && !porSinal) { await sinal('stop', {}) ; post('/api/lives', { canal, user: nome, on: false }).catch(() => {}) }
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
    Object.values(pcsRef.current).forEach((p) => { try { p.close() } catch (_) {} })
    pcsRef.current = {}
    if (pcRef.current) { try { pcRef.current.close() } catch (_) {} pcRef.current = null }
    if (vRef.current) { vRef.current.srcObject = null; vRef.current.style.display = 'none' }
    if (vRemoto.current) { vRemoto.current.srcObject = null; vRemoto.current.style.display = 'none' }
    setOnline(false)
    setModo('none')
    setStatus('Live encerrada.')
  }

  useEffect(() => () => parar(true), [])

  return (
    <div className="h-full overflow-y-auto no-scrollbar pb-28 pt-4 px-4">
      <h1 className="text-xl font-black mb-1">Explorar</h1>
      <p className="text-white/40 text-sm mb-4">Lives ao vivo agora</p>

      <div className="card-dark p-4 mb-5 space-y-3">
        <input className="input-dark" placeholder="Canal (ex.: canal1)" value={canal} onChange={(e) => setCanal(e.target.value)} />
        <input className="input-dark" placeholder="Seu nome" value={nome} onChange={(e) => setNome(e.target.value)} />
        <div className="grid grid-cols-3 gap-2 pt-1">
          <button onClick={transmitir} className="btn-base bg-tpink text-white py-3 flex items-center justify-center gap-1.5">
            <Radio size={16} /> TRANSMITIR
          </button>
          <button onClick={assistir} className="btn-base bg-white text-black py-3 flex items-center justify-center gap-1.5">
            <Eye size={16} /> ASSISTIR
          </button>
          <button onClick={() => parar(false)} className="btn-base bg-white/10 text-white/80 py-3 flex items-center justify-center gap-1.5">
            <Square size={15} /> PARAR
          </button>
        </div>
      </div>

      <div className="card-dark p-4 mb-5">
        <div className="flex items-center gap-2 text-sm font-bold mb-2">
          <Mic size={15} className={online ? 'text-tpink' : 'text-white/40'} />
          <span className={online ? 'text-tpink' : 'text-white/60'}>{online ? 'AO VIVO — transmitindo' : 'Status'}</span>
        </div>
        <p className="text-xs text-white/60 leading-relaxed">{status}</p>
        <video ref={vRef} autoPlay muted playsInline className="hidden w-full max-h-52 bg-black rounded-box mt-3 object-cover" />
        <video ref={vRemoto} autoPlay playsInline className="hidden w-full max-h-52 bg-black rounded-box mt-3 object-cover" />
      </div>

      <div className="grid grid-cols-2 gap-3">
        {(lives.length ? lives : MOCK_LIVES).map((lv, i) => (
          <motion.button
            key={lv.canal + i}
            onClick={() => { setCanal(lv.canal); setNome(localUser.name || lv.user); assistir() }}
            className="relative aspect-[9/16] rounded-box overflow-hidden text-left"
            initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
            style={{ background: `linear-gradient(150deg, ${['#1a0533', '#03212b', '#2b0517', '#1c1c00'][i % 4]}, ${['#FE2C55', '#25F4EE', '#7c3aed', '#f59e0b'][i % 4]})` }}
          >
            <div className="absolute inset-0 bg-noise" />
            <span className="absolute text-6xl right-2 top-8">{lv.emoji || '🎥'}</span>
            <span className="absolute top-2 left-2 flex items-center gap-1.5 px-2 py-1 rounded-md bg-tpink text-white text-[10px] font-black pulse-live">
              <span className="w-1.5 h-1.5 rounded-full bg-white" /> AO VIVO
            </span>
            <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/85 to-transparent p-2.5 pt-8">
              <p className="text-[11px] text-white/60 truncate">📡 {lv.canal}</p>
              <div className="flex items-center gap-1.5 mt-0.5">
                <Avatar name={lv.user} size={18} />
                <p className="text-xs font-bold truncate">{lv.user}</p>
              </div>
              <p className="flex items-center gap-1 text-[11px] text-white/70 mt-1">
                <Users size={11} /> {fmtViewers(lv.viewers)} assistindo
              </p>
            </div>
            <Video size={16} className="absolute top-2 right-2 text-white/70" />
          </motion.button>
        ))}
      </div>
    </div>
  )
}
