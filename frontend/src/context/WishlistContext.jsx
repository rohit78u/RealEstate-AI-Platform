import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { loadJSON, saveJSON } from '../utils/storageUtils'

const STORAGE_KEY = 'wishlist'
const WishlistContext = createContext(null)

export function WishlistProvider({ children }) {
  const [wishlistIds, setWishlistIds] = useState(() => loadJSON(STORAGE_KEY, []))

  useEffect(() => {
    saveJSON(STORAGE_KEY, wishlistIds)
  }, [wishlistIds])

  const isWishlisted = useCallback(
    (id) => wishlistIds.includes(Number(id)),
    [wishlistIds]
  )

  const toggleWishlist = useCallback((id) => {
    const numericId = Number(id)
    setWishlistIds((prev) =>
      prev.includes(numericId)
        ? prev.filter((item) => item !== numericId)
        : [...prev, numericId]
    )
  }, [])

  const removeFromWishlist = useCallback((id) => {
    const numericId = Number(id)
    setWishlistIds((prev) => prev.filter((item) => item !== numericId))
  }, [])

  const value = useMemo(
    () => ({ wishlistIds, isWishlisted, toggleWishlist, removeFromWishlist }),
    [wishlistIds, isWishlisted, toggleWishlist, removeFromWishlist]
  )

  return (
    <WishlistContext.Provider value={value}>
      {children}
    </WishlistContext.Provider>
  )
}

export function useWishlist() {
  const context = useContext(WishlistContext)
  if (!context) {
    throw new Error('useWishlist must be used within WishlistProvider')
  }
  return context
}
