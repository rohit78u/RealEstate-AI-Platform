import { formatPrice } from '../services/api'

export default function PropertyCard({ property }) {
  const primaryImage = property.images?.find((img) => img.is_primary) || property.images?.[0]

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition-shadow">
      <div className="h-48 bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center">
        {primaryImage ? (
          <img src={primaryImage.image_path} alt={property.title} className="w-full h-full object-cover" />
        ) : (
          <span className="text-4xl">🏠</span>
        )}
      </div>
      <div className="p-5">
        <h3 className="font-semibold text-lg text-slate-900 truncate">{property.title}</h3>
        <p className="text-sm text-slate-500 mt-1">{property.location}, {property.city}</p>
        <p className="text-xl font-bold text-primary-700 mt-2">{formatPrice(property.price)}</p>
        <div className="flex gap-4 mt-3 text-sm text-slate-600">
          <span>{property.bedrooms} Beds</span>
          <span>{property.bathrooms} Baths</span>
          <span>{property.area_sqft} sqft</span>
        </div>
      </div>
    </div>
  )
}
