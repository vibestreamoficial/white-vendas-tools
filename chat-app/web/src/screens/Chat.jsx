import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Send, Smile, MessageCircle } from 'lucide-react'
import Avatar from '../components/Avatar.jsx'
import { get, post } from '../api.js'
import { MOCK_DMS } from '../mock.js'

const EMOJIS = ['😂', '❤️', '🔥', '👏', '😍', '👍', '🤣', '💯']

function Convo({ convo, localUser, onBack, toast }) {
  const [texto, setTexto] = useState('')
  const [msgs, setMsgs] = useState([])
  const after = useRef(0)
  const boxRef = useRef(null)
  const room = 'dm:' + [localUser.username, convo.user].sort().join(':')

  const load = async () => {
    try {
      const r = await get('/messages?room=' + encodeURIComponent(room) + '&after=' + after.current)
      if (r && r.length) {
        after.current = Math.max(...r.map((m) => m.id))
        setMsgs((m) => [...m, ...r])
        post('/api/dm/read', { user: localUser.username, room }).catch(() => {})
        setTimeout(() => boxRef.current?.scrollTo(0, boxRef.current.scrollHeight), 60)
      }
    } catch (_) {}
  }

  useEffect(() => {
    load()
    const iv = setInterval(load, 1500)
    return () => clearInterval(iv)
  }, [room])

  const enviar = async () => {
    const t = texto.trim()
    if (!t) return
    setTexto('')
    setMsgs((m) => [...m, { id: Date.now(), user: localUser.username, text: t, ts: 'agora' }])
    try {
      await post('/api/dm', { de: localUser.username, para: convo.user, text: t })
    } catch (_) {
      setTimeout(() => boxRef.current?.scrollTo(0, boxRef.current.scrollHeight), 60)
    }
    setTimeout(() => boxRef.current?.scrollTo(0, boxRef.current.scrollHeight), 60)
  }

  return (
    <motion.div className="h-full flex flex-col" initial={{ x: 40, opacity: 0 }} animate={{ x: 0, opacity: 1 }}>
      <header className="flex items-center gap-3 px-3 py-3 border-b border-white/5 bg-tcard/90 backdrop-blur">
        <button onClick={onBack} className="p-1.5 -ml-1.5"><ArrowLeft size={20} /></button>
        <Avatar name={convo.user} size={34} />
        <div>
          <p className="font-bold text-sm">{convo.name}</p>
          <p className="text-[11px] text-white/40">@{convo.user}</p>
        </div>
      </header>

      <div ref={boxRef} className="flex-1 overflow-y-auto no-scrollbar px-3 py-4 space-y-2">
        {msgs.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-white/30 gap-2">
            <MessageCircle size={40} />
            <p className="text-sm">Diga oi pra {convo.name}! 👋</p>
          </div>
        )}
        {msgs.map((m) => (
          <div key={m.id} className={`flex ${m.user === localUser.username ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[75%] px-4 py-2.5 rounded-2xl text-sm leading-snug ${m.user === localUser.username ? 'bg-tpink rounded-br-md' : 'bg-tinput rounded-bl-md'}`}>
              {m.user !== localUser.username && <p className="text-[10px] font-bold text-tcyan mb-0.5">{m.user}</p>}
              {m.text}
            </div>
          </div>
        ))}
      </div>

      <div className="p-3 border-t border-white/5 bg-tcard/90 backdrop-blur">
        <div className="flex gap-1.5 mb-2 overflow-x-auto no-scrollbar">
          {EMOJIS.map((e) => (
            <button key={e} onClick={() => setTexto((t) => t + e)} className="text-xl hover:scale-125 transition-transform shrink-0">{e}</button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <div className="flex-1 flex items-center gap-2 bg-tinput rounded-full px-4 py-2.5">
            <Smile size={18} className="text-white/40" />
            <input
              className="flex-1 bg-transparent outline-none text-sm placeholder-white/30"
              placeholder="Mensagem..."
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && enviar()}
            />
          </div>
          <button onClick={enviar} className="w-11 h-11 rounded-full bg-tpink flex items-center justify-center active:scale-90 transition-transform">
            <Send size={17} />
          </button>
        </div>
      </div>
    </motion.div>
  )
}

export default function Chat({ localUser }) {
  const [conversas, setConversas] = useState([])
  const [ativa, setAtiva] = useState(null)

  useEffect(() => {
    get('/api/conversas?user=' + encodeURIComponent(localUser.username)).then((r) => {
      if (r && r.conversas && r.conversas.length) setConversas(r.conversas)
    }).catch(() => {})
    const iv = setInterval(() => {
      get('/api/conversas?user=' + encodeURIComponent(localUser.username)).then((r) => {
        if (r && r.conversas && r.conversas.length) setConversas(r.conversas)
      }).catch(() => {})
    }, 4000)
    return () => clearInterval(iv)
  }, [localUser.username])

  const lista = conversas.length ? conversas : MOCK_DMS

  if (ativa) {
    const c = lista.find((x) => x.user === ativa)
    if (c) return <Convo convo={c} localUser={localUser} onBack={() => setAtiva(null)} />
  }

  return (
    <div className="h-full overflow-y-auto no-scrollbar pb-24 pt-4 px-4">
      <h1 className="text-xl font-black mb-1">Mensagens</h1>
      <p className="text-white/40 text-sm mb-4">Suas conversas</p>
      <div className="space-y-1">
        <AnimatePresence>
          {lista.map((c, i) => (
            <motion.button
              key={c.user}
              onClick={() => setAtiva(c.user)}
              className="w-full flex items-center gap-3 p-3 card-dark hover:bg-tinput transition-colors"
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}
            >
              <Avatar name={c.user} size={52} />
              <div className="flex-1 min-w-0 text-left">
                <div className="flex items-center justify-between">
                  <p className="font-bold text-sm truncate">{c.name}</p>
                  <span className="text-[11px] text-white/40 shrink-0 ml-2">{c.hora || 'agora'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <p className="text-xs text-white/50 truncate">{c.last}</p>
                  {(c.unread || 0) > 0 && (
                    <span className="min-w-[18px] h-[18px] px-1 rounded-full bg-tpink text-[10px] font-black flex items-center justify-center shrink-0 ml-2">
                      {c.unread}
                    </span>
                  )}
                </div>
              </div>
            </motion.button>
          ))}
        </AnimatePresence>
      </div>
    </div>
  )
}
