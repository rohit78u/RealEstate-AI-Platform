import { useWishlist } from '../context/WishlistContext'

export default function WishlistButton({ propertyId, className = '', showLabel = false }) {
  const { isWishlisted, toggleWishlist } = useWishlist()
  const active = isWishlisted(propertyId)

  const handleClick = (event) => {
    event.preventDefault()
    event.stopPropagation()
    toggleWishlist(propertyId)
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      aria-label={active ? 'Remove from wishlist' : 'Add to wishlist'}
      className={`rounded-full bg-white/90 shadow-md flex items-center justify-center transition-all duration-200 hover:scale-110 ${
        showLabel ? 'px-4 py-2 gap-2 text-sm font-medium rounded-lg' : 'h-9 w-9 text-lg'
      } ${active ? 'text-red-500 ring-2 ring-red-300' : 'text-slate-600'} ${className}`}
    >
      <span>{active ? '♥' : '♡'}</span>
      {showLabel && <span>{active ? 'Saved' : 'Wishlist'}</span>}
    </button>
  )
}
