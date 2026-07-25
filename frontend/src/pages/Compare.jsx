import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import PropertyComparison from '../components/PropertyComparison'
import Toast from '../components/Toast'
import { useCompare } from '../context/CompareContext'

export default function Compare() {
  const { compareIds, removeFromCompare, clearCompare, message } = useCompare()
  const [properties, setProperties] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (compareIds.length === 0) {
      setProperties([])
      setLoading(false)
      return
    }

    setLoading(true)
    Promise.all(
      compareIds.map((id) =>
        api
          .get(`/properties/${id}`)
          .then((res) => res.data)
          .catch(() => null)
      )
    )
      .then((results) => {
        const valid = results.filter(Boolean)
        setProperties(valid)
      })
      .finally(() => setLoading(false))
  }, [compareIds])

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <h1 className="text-3xl font-bold">Compare Properties</h1>
        {compareIds.length > 0 && (
          <button
            type="button"
            onClick={clearCompare}
            className="text-sm text-red-600 hover:text-red-700 font-medium transition-colors duration-200"
          >
            Clear All
          </button>
        )}
      </div>

      {loading ? (
        <p className="text-slate-500">Loading comparison...</p>
      ) : (
        <PropertyComparison properties={properties} onRemove={removeFromCompare} />
      )}

      {compareIds.length > 0 && properties.length === 0 && !loading && (
        <div className="text-center py-8">
          <p className="text-slate-500 mb-4">Unable to load selected properties.</p>
          <Link to="/properties" className="text-primary-600 font-medium hover:text-primary-700">
            Browse Properties
          </Link>
        </div>
      )}

      <Toast message={message} visible={Boolean(message)} />
    </div>
  )
}
