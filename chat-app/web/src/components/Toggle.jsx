export default function Toggle({ checked, onChange, label }) {
  return (
    <button type="button" onClick={() => onChange(!checked)} className="flex items-center justify-between w-full py-1">
      <span className="text-sm text-white/80">{label}</span>
      <span className={`w-11 h-6 rounded-full p-0.5 transition-colors ${checked ? 'bg-tpink' : 'bg-white/15'}`}>
        <span className={`block w-5 h-5 bg-white rounded-full transition-transform ${checked ? 'translate-x-5' : ''}`} />
      </span>
    </button>
  )
}
