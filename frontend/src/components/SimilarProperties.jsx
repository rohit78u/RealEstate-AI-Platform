import { useEffect, useState } from 'react'
import api from '../services/api'
import PropertyCard from './PropertyCard'

export default function SimilarProperties({ property }) {
  const [similar, setSimilar] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!property) return

    setLoading(true)
    api
      .get('/properties', {
        params: {
          city: property.city,
          bedrooms: property.bedrooms,
          limit: 50,
        },
      })
      .then((res) => {
        const filtered = res.data.items
          .filter(
            (item) =>
              item.id !== property.id && item.bedrooms === property.bedrooms
          )
          .sort(
            (a, b) =>
              Math.abs(a.price - property.price) -
              Math.abs(b.price - property.price)
          )
          .slice(0, 4)

        setSimilar(filtered)
      })
      .catch(() => setSimilar([]))
      .finally(() => setLoading(false))
  }, [property])

  if (loading) {
    return (
      <section className="mt-10">
        <h2 className="text-2xl font-bold mb-4">Similar Properties</h2>
        <p className="text-slate-500">Loading similar properties...</p>
      </section>
    )
  }

  if (similar.length === 0) return null

  return (
    <section className="mt-10">
      <h2 className="text-2xl font-bold mb-6">Similar Properties</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {similar.map((item) => (
          <PropertyCard key={item.id} property={item} />
        ))}
      </div>
    </section>
  )
}
