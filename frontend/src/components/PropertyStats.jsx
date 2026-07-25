import { formatPrice } from '../services/api'
import { getPropertyAge, isFurnished } from '../utils/propertyUtils'

export default function PropertyStats({ property }) {
  const pricePerSqft = property.area_sqft
    ? Math.round(property.price / property.area_sqft)
    : 0

  const stats = [
    { label: 'Price per sqft', value: formatPrice(pricePerSqft) },
    { label: 'Property Age', value: `${getPropertyAge(property.year_built)} years` },
    { label: 'Parking', value: `${property.parking} spaces` },
    { label: 'Furnished', value: isFurnished(property) },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div key={stat.label} className="bg-slate-50 rounded-lg p-3">
          <p className="text-xs text-slate-500">{stat.label}</p>
          <p className="font-semibold">{stat.value}</p>
        </div>
      ))}
    </div>
  )
}
