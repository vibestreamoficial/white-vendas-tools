import { useEffect, useState } from 'react'
import BottomNav from './components/BottomNav.jsx'
import Toasts from './components/Toasts.jsx'
import CreatePost from './components/CreatePost.jsx'
import Home from './screens/Home.jsx'
import Explore from './screens/Explore.jsx'
import Chat from './screens/Chat.jsx'
import Profile from './screens/Profile.jsx'
import Admin from './screens/Admin.jsx'
import { get } from './api.js'
import { MOCK_POSTS } from './mock.js'

const userPadrao = {
  username: 'ana',
  name: 'Ana Souza',
  bio: '💖 vida, dança e trend',
  avatar: null,
  seguindo: 128, seguidores: 4520, curtidas: 12900
}

export default function App() {
  const [rota, setRota] = useState('feed')
  const [localUser, setLocalUser] = useState(() => {
    try { return { ...userPadrao, ...JSON.parse(localStorage.getItem('wc_user')) } } catch (_) { return userPadrao }
  })
  const [posts, setPosts] = useState(MOCK_POSTS)
  const [lives, setLives] = useState([])
  const [criar, setCriar] = useState(false)
  const [toasts, setToasts] = useState([])

  const admin = window.location.hash.startsWith('#/admin') || window.location.pathname.startsWith('/admin')

  const toast = (msg, tipo = 'ok') => {
    const id = Date.now() + Math.random()
    setToasts((t) => [...t, { id, msg, tipo }])
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3200)
  }

  useEffect(() => {
    if (admin) return
    let vivo = true
    const load = () => {
      get('/api/posts?status=approved').then((r) => {
        if (vivo && r?.posts?.length) setPosts(r.posts)
      }).catch(() => {})
      get('/api/lives').then((r) => {
        if (vivo && r?.lives?.length) setLives(r.lives)
      }).catch(() => {})
    }
    load()
    const iv = setInterval(load, 5000)
    return () => { vivo = false; clearInterval(iv) }
  }, [admin])

  if (admin) return <Admin toast={toast} />

  const tela = {
    feed: <Home posts={posts} localUser={localUser} />,
    explore: <Explore lives={lives} setLives={setLives} localUser={localUser} toast={toast} />,
    chat: <Chat localUser={localUser} />,
    profile: <Profile localUser={localUser} setLocalUser={setLocalUser} posts={posts} toast={toast} />
  }[rota]

  return (
    <div className="max-w-md mx-auto h-dvh relative overflow-hidden bg-tblack">
      <div className="h-full">{tela}</div>
      <BottomNav ativa={rota} onNav={setRota} onPlus={() => setCriar(true)} />
      <CreatePost open={criar} onClose={() => setCriar(false)} localUser={localUser} toast={toast} />
      <Toasts toasts={toasts} />
    </div>
  )
}
