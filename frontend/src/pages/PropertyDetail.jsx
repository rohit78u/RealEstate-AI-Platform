import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api, { formatPrice } from '../services/api'

export default function PropertyDetail() {
  const { id } = useParams()
  const [property, setProperty] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get(`/properties/${id}`)
      .then((res) => setProperty(res.data))
      .catch(() => setError('Property not found'))
  }, [id])

  if (error) return <p className="text-red-600">{error}</p>
  if (!property) return <p className="text-slate-500">Loading...</p>

  return (
    <div>
      <Link to="/properties" className="text-primary-600 text-sm font-medium mb-4 inline-block">← Back to listings</Link>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <div className="bg-gradient-to-br from-primary-100 to-primary-200 rounded-xl h-80 flex items-center justify-center mb-4">
            {property.images?.length > 0 ? (
              <img src={property.images[0].image_path} alt={property.title} className="w-full h-full object-cover rounded-xl" />
            ) : (
              <span className="text-6xl">🏠</span>
            )}
          </div>
          {property.images?.length > 1 && (
            <div className="grid grid-cols-4 gap-2">
              {property.images.slice(1).map((img) => (
                <img key={img.id} src={img.image_path} alt="" className="h-20 w-full object-cover rounded-lg" />
              ))}
            </div>
          )}
        </div>

        <div>
          <h1 className="text-3xl font-bold">{property.title}</h1>
          <p className="text-slate-500 mt-1">{property.location}, {property.city}</p>
          <p className="text-3xl font-bold text-primary-700 mt-4">{formatPrice(property.price)}</p>

          <div className="grid grid-cols-2 gap-4 mt-6">
            {[
              ['Bedrooms', property.bedrooms],
              ['Bathrooms', property.bathrooms],
              ['Area', `${property.area_sqft} sqft`],
              ['Floors', property.floors],
              ['Year Built', property.year_built],
              ['Parking', property.parking],
            ].map(([label, value]) => (
              <div key={label} className="bg-slate-50 rounded-lg p-3">
                <p className="text-xs text-slate-500">{label}</p>
                <p className="font-semibold">{value}</p>
              </div>
            ))}
          </div>

          {property.description && (
            <div className="mt-6">
              <h3 className="font-semibold mb-2">Description</h3>
              <p className="text-slate-600">{property.description}</p>
            </div>
          )}

          <Link to="/chat" className="inline-block mt-6 bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700">
            Ask AI about this property
          </Link>
        </div>
      </div>
    </div>
  )
}
