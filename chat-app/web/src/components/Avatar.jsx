import { avatarFor } from '../api.js'

export default function Avatar({ name, src, size = 40, ring = false }) {
  return (
    <div
      className="rounded-full overflow-hidden flex items-center justify-center font-extrabold shrink-0"
      style={{
        width: size, height: size,
        background: src ? 'transparent' : avatarFor(name),
        boxShadow: ring ? '0 0 0 2px #fff, 0 0 0 5px #FE2C55' : undefined,
        fontSize: Math.max(14, size * 0.42)
      }}
    >
      {src ? <img src={src} alt={name} className="w-full h-full object-cover" /> : (name || '?').slice(0, 2).toUpperCase()}
    </div>
  )
}
