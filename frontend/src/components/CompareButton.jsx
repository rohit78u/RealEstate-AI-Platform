import { useCompare } from '../context/CompareContext'

export default function CompareButton({ propertyId, className = '', showLabel = false }) {
  const { isInCompare, toggleCompare } = useCompare()
  const active = isInCompare(propertyId)

  const handleClick = (event) => {
    event.preventDefault()
    event.stopPropagation()
    toggleCompare(propertyId)
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      aria-label={active ? 'Remove from compare' : 'Add to compare'}
      className={`rounded-full bg-white/90 shadow-md flex items-center justify-center transition-all duration-200 hover:scale-110 ${
        showLabel ? 'px-4 py-2 gap-2 text-sm font-medium' : 'h-9 w-9 text-sm'
      } ${active ? 'text-primary-700 ring-2 ring-primary-600' : 'text-slate-600'} ${className}`}
    >
      <span>⇄</span>
      {showLabel && <span>{active ? 'In Compare' : 'Compare'}</span>}
    </button>
  )
}
