import { Link } from 'react-router-dom'
import { formatPrice } from '../services/api'
import { getPropertyImage } from '../utils/imageUtils'

export default function PropertyComparison({ properties, onRemove }) {
  if (properties.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500 mb-4">No properties selected for comparison.</p>
        <Link
          to="/properties"
          className="inline-block bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors duration-200"
        >
          Browse Properties
        </Link>
      </div>
    )
  }

  const rows = [
    { label: 'Image', render: (property) => {
      const image =
        property.images?.find((img) => img.is_primary)?.image_path ||
        property.images?.[0]?.image_path ||
        getPropertyImage(property.title)

      return (
        <img
          src={image}
          alt={property.title}
          className="h-32 w-full object-cover rounded-lg"
        />
      )
    }},
    { label: 'Price', render: (property) => formatPrice(property.price) },
    { label: 'Area', render: (property) => `${property.area_sqft} sqft` },
    { label: 'Bedrooms', render: (property) => property.bedrooms },
    { label: 'Bathrooms', render: (property) => property.bathrooms },
    { label: 'Parking', render: (property) => property.parking },
    { label: 'Year Built', render: (property) => property.year_built },
    { label: 'City', render: (property) => property.city },
    { label: 'Location', render: (property) => property.location },
  ]

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[720px] border-collapse">
        <thead>
          <tr>
            <th className="text-left p-4 bg-slate-50 border border-slate-200 rounded-tl-xl">
              Feature
            </th>
            {properties.map((property) => (
              <th
                key={property.id}
                className="p-4 bg-slate-50 border border-slate-200 text-left min-w-[220px]"
              >
                <div className="flex items-start justify-between gap-2">
                  <Link
                    to={`/properties/${property.id}`}
                    className="font-semibold text-primary-700 hover:text-primary-800"
                  >
                    {property.title}
                  </Link>
                  <button
                    type="button"
                    onClick={() => onRemove(property.id)}
                    className="text-xs text-red-600 hover:text-red-700 transition-colors duration-200"
                  >
                    Remove
                  </button>
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label}>
              <td className="p-4 border border-slate-200 font-medium bg-white">
                {row.label}
              </td>
              {properties.map((property) => (
                <td key={`${property.id}-${row.label}`} className="p-4 border border-slate-200 bg-white">
                  {row.render(property)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
