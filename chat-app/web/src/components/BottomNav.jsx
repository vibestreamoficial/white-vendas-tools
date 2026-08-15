import { Home, Compass, MessageCircle, User } from 'lucide-react'

const tabs = [
  { id: 'feed', icon: Home, label: 'Início' },
  { id: 'explore', icon: Compass, label: 'Explorar' },
  null,
  { id: 'chat', icon: MessageCircle, label: 'Chat' },
  { id: 'profile', icon: User, label: 'Perfil' }
]

export default function BottomNav({ ativa, onNav, onPlus }) {
  return (
    <nav className="fixed bottom-0 inset-x-0 z-40 bg-tcard/95 backdrop-blur border-t border-white/10">
      <div className="max-w-md mx-auto grid grid-cols-5 items-center h-16">
        {tabs.map((t, i) =>
          t === null ? (
            <div key="plus" className="flex justify-center">
              <button
                onClick={onPlus}
                className="glitch w-12 h-12 rounded-2xl bg-gradient-to-br from-tpink to-tcyan flex items-center justify-center text-3xl font-black text-white shadow-lg shadow-tpink/30 -mt-6 active:scale-90 transition-transform"
                aria-label="Criar post"
              >+</button>
            </div>
          ) : (
            <button key={t.id} onClick={() => onNav(t.id)} className="flex flex-col items-center gap-1 py-2">
              <t.icon size={22} className={ativa === t.id ? 'text-white' : 'text-white/40'} strokeWidth={ativa === t.id ? 2.6 : 2} />
              <span className={`text-[10px] font-semibold ${ativa === t.id ? 'text-white' : 'text-white/40'}`}>{t.label}</span>
              {ativa === t.id && <span className="w-1 h-1 rounded-full bg-tcyan" />}
            </button>
          )
        )}
      </div>
    </nav>
  )
}
