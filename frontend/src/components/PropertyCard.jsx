import { Link } from 'react-router-dom'
import { formatPrice } from '../services/api'
import { getPropertyImage } from '../utils/imageUtils'
import PropertyBadges from './PropertyBadges'
import WishlistButton from './WishlistButton'
import CompareButton from './CompareButton'

export default function PropertyCard({ property }) {
  const primaryImage =
    property.images?.find((img) => img.is_primary) ||
    property.images?.[0]

  return (
    <div className="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
      <div className="relative h-48 overflow-hidden group">
        <Link to={`/properties/${property.id}`} className="block h-full">
          <img
            src={
              primaryImage
                ? primaryImage.image_path
                : getPropertyImage(property.title)
            }
            alt={property.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        </Link>

        <div className="absolute top-3 left-3">
          <PropertyBadges property={property} />
        </div>

        <div className="absolute top-3 right-3 flex gap-2 z-10">
          <WishlistButton propertyId={property.id} />
          <CompareButton propertyId={property.id} />
        </div>

        <div className="absolute bottom-3 left-3">
          <span className="rounded-full bg-slate-900/75 text-white px-2.5 py-1 text-xs font-medium">
            {property.city}
          </span>
        </div>
      </div>

      <Link to={`/properties/${property.id}`} className="block p-5">
        <h3 className="font-semibold text-lg text-slate-900 truncate">
          {property.title}
        </h3>

        <p className="text-sm text-slate-500 mt-1">
          {property.location}, {property.city}
        </p>

        <p className="text-xl font-bold text-primary-700 mt-2">
          {formatPrice(property.price)}
        </p>

        <div className="flex gap-4 mt-3 text-sm text-slate-600">
          <span>🛏 {property.bedrooms} Beds</span>
          <span>🛁 {property.bathrooms} Baths</span>
          <span>📐 {property.area_sqft} sqft</span>
        </div>
      </Link>
    </div>
  )
}
