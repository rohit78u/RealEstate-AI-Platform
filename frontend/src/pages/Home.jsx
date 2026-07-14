import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import PropertyCard from '../components/PropertyCard'
import api from '../services/api'

export default function Home() {
  const [properties, setProperties] = useState([])

  useEffect(() => {
    api.get('/properties', { params: { limit: 6, sort: 'created_desc' } })
      .then((res) => setProperties(res.data.items))
      .catch(() => {})
  }, [])

  return (
    <div>
      <section className="bg-gradient-to-r from-primary-700 to-primary-900 rounded-2xl text-white p-10 mb-10">
        <h1 className="text-4xl font-bold mb-4">AI Real Estate Intelligence Platform</h1>
        <p className="text-primary-100 text-lg max-w-2xl mb-6">
          Browse properties, predict house prices with Machine Learning, and get AI-powered real estate advice.
        </p>
        <div className="flex gap-4">
          <Link to="/properties" className="bg-white text-primary-700 px-6 py-3 rounded-lg font-semibold hover:bg-primary-50">
            Browse Properties
          </Link>
          <Link to="/predict" className="border border-white/40 px-6 py-3 rounded-lg font-semibold hover:bg-white/10">
            Predict Price
          </Link>
        </div>
      </section>

      <section>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Featured Listings</h2>
          <Link to="/properties" className="text-primary-600 font-medium hover:text-primary-700">View all →</Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {properties.map((p) => (
            <Link key={p.id} to={`/properties/${p.id}`}>
              <PropertyCard property={p} />
            </Link>
          ))}
        </div>
        {properties.length === 0 && (
          <p className="text-slate-500 text-center py-12">No properties listed yet. Admin can add properties.</p>
        )}
      </section>
    </div>
  )
}
