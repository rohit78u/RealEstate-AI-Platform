import { getPropertyBadges } from '../utils/propertyUtils'

export default function PropertyBadges({ property, className = '' }) {
  const badges = getPropertyBadges(property)

  if (badges.length === 0) return null

  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {badges.map((badge) => (
        <span
          key={badge.label}
          className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${badge.className}`}
        >
          {badge.label}
        </span>
      ))}
    </div>
  )
}
