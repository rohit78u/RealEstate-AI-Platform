import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api, { formatPrice } from '../services/api'
import PropertyGallery from '../components/PropertyGallery'
import PropertyStats from '../components/PropertyStats'
import PropertyBadges from '../components/PropertyBadges'
import EMICalculator from '../components/EMICalculator'
import AgentCard from '../components/AgentCard'
import NearbyFacilities from '../components/NearbyFacilities'
import SimilarProperties from '../components/SimilarProperties'
import WishlistButton from '../components/WishlistButton'
import CompareButton from '../components/CompareButton'
import ShareButton from '../components/ShareButton'
import Toast from '../components/Toast'
import { useCompare } from '../context/CompareContext'
import { getPropertyFeatures } from '../utils/propertyUtils'

export default function PropertyDetail() {
  const { id } = useParams()
  const { message: compareMessage } = useCompare()

  const [property, setProperty] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .get(`/properties/${id}`)
      .then((res) => setProperty(res.data))
      .catch(() => setError('Property not found'))
  }, [id])

  if (error) {
    return <p className="text-red-600">{error}</p>
  }

  if (!property) {
    return <p className="text-slate-500">Loading...</p>
  }

  return (
    <div>
      <Link
        to="/properties"
        className="text-primary-600 text-sm font-medium mb-4 inline-block"
      >
        ← Back to listings
      </Link>

      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <PropertyBadges property={property} />
        <div className="flex flex-wrap items-center gap-3">
          <WishlistButton propertyId={property.id} showLabel />
          <CompareButton propertyId={property.id} showLabel />
          <ShareButton />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <PropertyGallery property={property} />

        <div>
          <h1 className="text-3xl font-bold">{property.title}</h1>

          <p className="text-slate-500 mt-1">
            {property.location}, {property.city}
          </p>

          <p className="text-3xl font-bold text-primary-700 mt-4">
            {formatPrice(property.price)}
          </p>

          <div className="mt-6">
            <PropertyStats property={property} />
          </div>

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

          {getPropertyFeatures(property).length > 0 && (
            <div className="mt-6">
              <h3 className="font-semibold mb-4">Amenities & Features</h3>
              <div className="grid grid-cols-2 gap-3">
                {getPropertyFeatures(property).map((feature) => (
                  <div
                    key={feature.label}
                    className="flex items-center gap-3 rounded-lg border border-slate-200 bg-slate-50 p-3"
                  >
                    <span className="text-2xl">{feature.icon}</span>
                    <div>
                      <p className="text-sm font-semibold">{feature.label}</p>
                      <p className="text-xs text-slate-500">{feature.value}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <Link
            to="/chat"
            className="inline-block mt-6 bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors duration-200"
          >
            Ask AI about this property
          </Link>
        </div>
      </div>

      <div className="mt-10 space-y-8">
        <EMICalculator defaultLoanAmount={property.price} />
        <AgentCard propertyId={property.id} />
        <NearbyFacilities propertyId={property.id} city={property.city} />
        <SimilarProperties property={property} />
      </div>

      <Toast message={compareMessage} visible={Boolean(compareMessage)} />
    </div>
  )
}
