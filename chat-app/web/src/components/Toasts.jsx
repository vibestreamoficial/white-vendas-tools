import { AnimatePresence, motion } from 'framer-motion'
import { CheckCircle2, AlertCircle } from 'lucide-react'

export default function Toasts({ toasts }) {
  return (
    <div className="fixed top-4 inset-x-0 z-[60] flex flex-col items-center gap-2 px-4">
      <AnimatePresence>
        {toasts.map((t) => (
          <motion.div
            key={t.id}
            className="flex items-center gap-2 px-4 py-2.5 rounded-box bg-tcard border border-white/10 text-sm font-semibold shadow-xl"
            initial={{ y: -24, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: -24, opacity: 0 }}
          >
            {t.tipo === 'erro' ? <AlertCircle size={16} className="text-tpink" /> : <CheckCircle2 size={16} className="text-tcyan" />}
            {t.msg}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
