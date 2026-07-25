import { getNearbyFacilities } from '../utils/propertyUtils'

export default function NearbyFacilities({ propertyId, city }) {
  const facilities = getNearbyFacilities(propertyId, city)

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <h3 className="text-xl font-bold mb-4">Nearby Facilities</h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {facilities.map((facility) => (
          <div
            key={facility.type}
            className="flex items-center gap-3 bg-slate-50 rounded-lg p-4 transition-all duration-300 hover:shadow-sm"
          >
            <span className="text-2xl">{facility.icon}</span>
            <div>
              <p className="font-medium text-sm">{facility.name}</p>
              <p className="text-xs text-slate-500">
                {facility.type} · {facility.distance}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
