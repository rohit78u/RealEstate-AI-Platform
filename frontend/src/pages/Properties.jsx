import { useEffect, useState } from 'react'
import PropertyCard from '../components/PropertyCard'
import api from '../services/api'

export default function Properties() {
  const [data, setData] = useState({ items: [], total: 0, page: 1, pages: 0 })
  const [filters, setFilters] = useState({
    city: '', min_price: '', max_price: '', bedrooms: '', sort: 'created_desc', page: 1,
  })
  const [loading, setLoading] = useState(true)

  const fetchProperties = () => {
    setLoading(true)
    const params = { page: filters.page, limit: 12, sort: filters.sort }
    if (filters.city) params.city = filters.city
    if (filters.min_price) params.min_price = filters.min_price
    if (filters.max_price) params.max_price = filters.max_price
    if (filters.bedrooms) params.bedrooms = filters.bedrooms

    api.get('/properties', { params })
      .then((res) => setData(res.data))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchProperties() }, [filters])

  const updateFilter = (key, value) => setFilters((f) => ({ ...f, [key]: value, page: 1 }))

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Property Listings</h1>

      <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6 grid grid-cols-2 md:grid-cols-5 gap-4">
        <input placeholder="City" value={filters.city} onChange={(e) => updateFilter('city', e.target.value)}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        <input placeholder="Min Price" type="number" value={filters.min_price} onChange={(e) => updateFilter('min_price', e.target.value)}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        <input placeholder="Max Price" type="number" value={filters.max_price} onChange={(e) => updateFilter('max_price', e.target.value)}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        <input placeholder="Min Bedrooms" type="number" value={filters.bedrooms} onChange={(e) => updateFilter('bedrooms', e.target.value)}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        <select value={filters.sort} onChange={(e) => updateFilter('sort', e.target.value)}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm">
          <option value="created_desc">Newest</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
          <option value="area_desc">Largest Area</option>
        </select>
      </div>

      {loading ? (
        <p className="text-center text-slate-500 py-12">Loading...</p>
      ) : (
        <>
          <p className="text-sm text-slate-500 mb-4">{data.total} properties found</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.items.map((p) => (
              <PropertyCard key={p.id} property={p} />
            ))}
          </div>
          {data.pages > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              {Array.from({ length: data.pages }, (_, i) => i + 1).map((page) => (
                <button key={page} onClick={() => setFilters((f) => ({ ...f, page }))}
                  className={`px-4 py-2 rounded-lg text-sm font-medium ${page === data.page ? 'bg-primary-600 text-white' : 'bg-white border border-slate-200 text-slate-600'}`}>
                  {page}
                </button>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
