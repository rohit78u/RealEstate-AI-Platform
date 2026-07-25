import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import PropertyCard from '../components/PropertyCard'
import { useWishlist } from '../context/WishlistContext'

export default function Wishlist() {
  const { wishlistIds, removeFromWishlist } = useWishlist()
  const [properties, setProperties] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (wishlistIds.length === 0) {
      setProperties([])
      setLoading(false)
      return
    }

    setLoading(true)
    Promise.all(
      wishlistIds.map((id) =>
        api
          .get(`/properties/${id}`)
          .then((res) => res.data)
          .catch(() => {
            removeFromWishlist(id)
            return null
          })
      )
    )
      .then((results) => setProperties(results.filter(Boolean)))
      .finally(() => setLoading(false))
  }, [wishlistIds, removeFromWishlist])

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">My Wishlist</h1>

      {loading ? (
        <p className="text-slate-500">Loading wishlist...</p>
      ) : properties.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-slate-500 mb-4">No saved properties yet.</p>
          <Link
            to="/properties"
            className="inline-block bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors duration-200"
          >
            Browse Properties
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {properties.map((property) => (
            <PropertyCard key={property.id} property={property} />
          ))}
        </div>
      )}
    </div>
  )
}
