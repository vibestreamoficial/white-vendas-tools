import { useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Heart, MessageCircle, Share2, Music2, UserPlus, Check, Play } from 'lucide-react'
import Avatar from '../components/Avatar.jsx'
import { fmtViewers, post } from '../api.js'

function Media({ post }) {
  if (post.mediaUrl) {
    return (
      <video src={post.mediaUrl} autoPlay loop muted playsInline className="absolute inset-0 w-full h-full object-cover" />
    )
  }
  return (
    <div className="absolute inset-0" style={{ background: `linear-gradient(160deg, ${post.gradient[0]}, ${post.gradient[1]})` }}>
      <div className="absolute inset-0 bg-noise" />
      <motion.div
        className="absolute inset-0 flex items-center justify-center text-8xl"
        animate={{ scale: [1, 1.08, 1], rotate: [0, 2, -2, 0] }}
        transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
      >
        {post.emoji}
      </motion.div>
      <div className="absolute bottom-6 left-0 right-0 h-32 bg-gradient-to-t from-black/60 to-transparent" />
    </div>
  )
}

function RightRail({ post, likes, liked, onLike, onFollow, seguindo }) {
  return (
    <div className="absolute right-2 bottom-24 flex flex-col items-center gap-5 z-10">
      <div className="flex flex-col items-center gap-1">
        <div className="relative">
          <Avatar name={post.author} size={48} ring />
          <button
            onClick={onFollow}
            className={`absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-6 h-6 rounded-full flex items-center justify-center border-2 border-black ${seguindo ? 'bg-white text-black' : 'bg-tpink text-white'}`}
          >
            {seguindo ? <Check size={12} strokeWidth={3} /> : <UserPlus size={12} strokeWidth={3} />}
          </button>
        </div>
      </div>

      <button onClick={onLike} className="flex flex-col items-center gap-1">
        <motion.div key={liked ? 'l' : 'n'} animate={{ scale: liked ? [1, 1.4, 1] : 1 }} transition={{ duration: 0.3 }}>
          <Heart size={34} className={liked ? 'text-tpink fill-tpink' : 'text-white'} />
        </motion.div>
        <span className="text-xs font-bold">{fmtViewers(likes)}</span>
      </button>

      <button className="flex flex-col items-center gap-1">
        <MessageCircle size={32} />
        <span className="text-xs font-bold">{fmtViewers(post.comentarios)}</span>
      </button>

      <button className="flex flex-col items-center gap-1">
        <Share2 size={32} />
        <span className="text-xs font-bold">{fmtViewers(post.compartilhamentos)}</span>
      </button>

      <div className="w-12 h-12 rounded-full border-[3px] border-white/80 p-0.5 mt-2">
        <div className="disc w-full h-full rounded-full overflow-hidden" style={{ background: `linear-gradient(135deg, ${post.gradient[0]}, ${post.gradient[1]})` }}>
          <Music2 size={20} className="w-full h-full p-3 text-white" />
        </div>
      </div>
    </div>
  )
}

function PostItem({ post, ativo, localUser }) {
  const [likes, setLikes] = useState(post.likes)
  const [liked, setLiked] = useState(false)
  const [seguindo, setSeguindo] = useState(false)
  const [bigHeart, setBigHeart] = useState(false)
  const lastTap = useRef(0)

  const darLike = (grande) => {
    setLiked(true)
    setLikes((l) => l + 1)
    post('/api/posts/' + post.id + '/like', {}).catch(() => {})
    if (grande) {
      setBigHeart(true)
      setTimeout(() => setBigHeart(false), 900)
    }
  }

  const handleTap = () => {
    const agora = Date.now()
    if (agora - lastTap.current < 300) darLike(true)
    lastTap.current = agora
  }

  const hashtags = (post.legenda || '').match(/#\w+/g) || []

  return (
    <section className="snap-item relative h-full w-full overflow-hidden select-none" onTouchStart={handleTap} onClick={handleTap}>
      <Media post={post} />
      <AnimatePresence>
        {bigHeart && (
          <motion.div
            className="absolute inset-0 z-20 flex items-center justify-center pointer-events-none"
            initial={{ scale: 0, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 1.6, opacity: 0 }}
            transition={{ duration: 0.45 }}
          >
            <Heart size={140} className="text-tpink fill-tpink drop-shadow-2xl" />
          </motion.div>
        )}
      </AnimatePresence>

      <div className="absolute bottom-16 left-4 right-16 z-10">
        <p className="font-extrabold text-[15px] mb-1">@{post.author}</p>
        <p className="text-[13px] text-white/90 leading-snug mb-2">
          {post.legenda?.split(/(#\w+)/g).map((part, i) =>
            part.startsWith('#') ? (
              <span key={i} className="text-white font-bold">{part}</span>
            ) : (
              <span key={i}>{part}</span>
            )
          )}
        </p>
        <div className="flex items-center gap-1 text-[12px] text-white/80 overflow-hidden">
          <Music2 size={13} className="shrink-0" />
          <div className="overflow-hidden whitespace-nowrap">
            <span className="marquee">{post.musica} — {post.musica} —</span>
          </div>
        </div>
      </div>

      <RightRail
        post={post}
        likes={likes}
        liked={liked}
        onLike={() => darLike(false)}
        onFollow={() => setSeguindo((s) => !s)}
        seguindo={seguindo}
      />

      {post.fixado && (
        <span className="absolute top-16 left-4 z-10 flex items-center gap-1 text-[11px] font-bold bg-tpink/90 rounded-full px-2.5 py-1">
          <Play size={10} className="fill-white" /> FIXADO
        </span>
      )}
    </section>
  )
}

export default function Home({ posts, localUser }) {
  const [aba, setAba] = useState('voce')
  const visiveis = aba === 'seguindo' ? posts.filter((p) => ['ana', 'maria'].includes(p.author)) : posts

  return (
    <div className="h-full flex flex-col">
      <header className="fixed top-0 inset-x-0 z-30 bg-gradient-to-b from-black/80 to-transparent pt-4 pb-10">
        <div className="flex justify-center gap-8">
          {[['seguindo', 'Seguindo'], ['voce', 'Para Você']].map(([id, label]) => (
            <button key={id} onClick={() => setAba(id)} className="relative pb-1">
              <span className={`text-[15px] font-bold ${aba === id ? 'text-white' : 'text-white/40'}`}>{label}</span>
              {aba === id && <motion.span layoutId="tab" className="absolute -bottom-0.5 left-0 right-0 h-[3px] rounded-full bg-white" />}
            </button>
          ))}
        </div>
      </header>

      {visiveis.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center gap-3 text-white/40">
          <span className="text-6xl">🎬</span>
          <p className="font-semibold">Nenhum vídeo aqui ainda</p>
          <p className="text-sm">Os posts aprovados aparecem no Para Você</p>
        </div>
      ) : (
        <div className="snap-feed no-scrollbar h-full overflow-y-scroll">
          {visiveis.map((p, i) => (
            <PostItem key={p.id} post={p} ativo={i === 0} localUser={localUser} />
          ))}
        </div>
      )}
    </div>
  )
}
