export const MOCK_USERS = [
  { username: 'ana', name: 'Ana Souza', bio: '💖 vida, dança e trend', avatar: null, status: 'ativo', criado: '2026-08-01', seguindo: 128, seguidores: 4520, curtidas: 12900 },
  { username: 'leo_dev', name: 'Leo', bio: '🚀 hacker do bem • dev', avatar: null, status: 'ativo', criado: '2026-08-02', seguindo: 89, seguidores: 2310, curtidas: 8200 },
  { username: 'maria', name: 'Maria Lima', bio: '🎵 música e arte', avatar: null, status: 'ativo', criado: '2026-08-03', seguindo: 210, seguidores: 9810, curtidas: 33100 },
  { username: 'joao', name: 'João Pedro', bio: '🎮 gamer', avatar: null, status: 'ativo', criado: '2026-08-04', seguindo: 45, seguidores: 760, curtidas: 1900 },
  { username: 'bia', name: 'Bia Costa', bio: '✨ lifestyle', avatar: null, status: 'ativo', criado: '2026-08-05', seguindo: 320, seguidores: 15200, curtidas: 56000 },
  { username: 'kaua', name: 'Kauã', bio: '🔥 treinos', avatar: null, status: 'ativo', criado: '2026-08-06', seguindo: 12, seguidores: 540, curtidas: 1300 }
]

const G = [
  ['#1a0533', '#FE2C55'],
  ['#03212b', '#25F4EE'],
  ['#2b0517', '#7c3aed'],
  ['#1c1c00', '#f59e0b'],
  ['#001f14', '#10b981'],
  ['#0b1030', '#3b82f6']
]
const EMOJIS = ['💃', '🔥', '🎵', '⚡', '💥', '👾', '✨', '🎸']

export const MOCK_POSTS = MOCK_USERS.map((u, i) => ({
  id: 'mock' + (i + 1),
  author: u.username,
  autorNome: u.name,
  legenda: i % 2 === 0 ? 'novo vídeo por aqui! 🔥 #fyp #trend' : 'isso ficou muito bom 😂 #viral #whitechat',
  musica: ['som original — ' + u.name, 'viral do momento', 'mix 2026'].join(' | '),
  likes: [1200, 8450, 340, 21100, 930, 70][i],
  comentarios: [45, 320, 12, 890, 41, 3][i],
  compartilhamentos: [12, 89, 3, 240, 9, 0][i],
  gradient: G[i % G.length],
  emoji: EMOJIS[i % EMOJIS.length],
  status: 'aprovado',
  fixado: i === 0,
  data: '2026-08-1' + i,
  views: [2300, 9000, 900, 24000, 1500, 200][i]
}))

export const MOCK_LIVES = [
  { canal: 'canal1', user: 'ana', viewers: 1240, desde: '10:22', emoji: '🎤' },
  { canal: 'live_musica', user: 'maria', viewers: 3800, desde: '09:40', emoji: '🎸' },
  { canal: 'gamer_br', user: 'joao', viewers: 860, desde: '11:05', emoji: '🎮' },
  { canal: 'lifestyle', user: 'bia', viewers: 5100, desde: '08:55', emoji: '✨' }
]

export const MOCK_DMS = [
  { user: 'maria', name: 'Maria Lima', last: 'vem pro meu ao vivo! 🔥', hora: 'agora', unread: 2 },
  { user: 'leo_dev', name: 'Leo', last: 'consegui rodar o bot 👌', hora: '12:40', unread: 0 },
  { user: 'bia', name: 'Bia Costa', last: 'hahaha perfeito 😂', hora: '11:12', unread: 1 },
  { user: 'joao', name: 'João Pedro', last: 'bora jogar depois?', hora: 'ontem', unread: 0 }
]

export const MOCK_REPORTS = [
  { id: 1, post: 'mock2', autor: 'maria', motivo: 'Conteúdo impróprio', data: '2026-08-14', status: 'pendente' },
  { id: 2, post: 'mock5', autor: 'bia', motivo: 'Assédio nos comentários', data: '2026-08-15', status: 'pendente' }
]

export const WEEK = [
  { d: 'Seg', n: 12 }, { d: 'Ter', n: 19 }, { d: 'Qua', n: 15 }, { d: 'Qui', n: 27 },
  { d: 'Sex', n: 34 }, { d: 'Sáb', n: 41 }, { d: 'Dom', n: 29 }
]
