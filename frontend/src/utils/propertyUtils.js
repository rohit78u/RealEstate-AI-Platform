const AGENTS = [
  { name: 'Rajesh Kumar', phone: '+91 98765 43210', email: 'rajesh.kumar@realestate.com' },
  { name: 'Priya Sharma', phone: '+91 98765 43211', email: 'priya.sharma@realestate.com' },
  { name: 'Amit Patel', phone: '+91 98765 43212', email: 'amit.patel@realestate.com' },
  { name: 'Sneha Reddy', phone: '+91 98765 43213', email: 'sneha.reddy@realestate.com' },
  { name: 'Vikram Singh', phone: '+91 98765 43214', email: 'vikram.singh@realestate.com' },
]

const BADGE_STYLES = {
  Featured: 'bg-amber-100 text-amber-800',
  Luxury: 'bg-purple-100 text-purple-800',
  New: 'bg-green-100 text-green-800',
  'Best Value': 'bg-blue-100 text-blue-800',
}

export function calculateEMI(loan, annualRate, years) {
  const principal = Number(loan) || 0
  const rate = Number(annualRate) || 0
  const tenure = Number(years) || 0

  if (principal <= 0 || tenure <= 0) {
    return { emi: 0, totalInterest: 0, totalPayment: 0 }
  }

  const monthlyRate = rate / 12 / 100
  const months = tenure * 12

  if (monthlyRate === 0) {
    const emi = principal / months
    return {
      emi,
      totalInterest: 0,
      totalPayment: principal,
    }
  }

  const factor = Math.pow(1 + monthlyRate, months)
  const emi = (principal * monthlyRate * factor) / (factor - 1)
  const totalPayment = emi * months
  const totalInterest = totalPayment - principal

  return { emi, totalInterest, totalPayment }
}

export function getPropertyBadges(property) {
  if (!property) return []

  const badges = []
  const title = (property.title || '').toLowerCase()
  const features = property.features || {}
  const currentYear = new Date().getFullYear()
  const pricePerSqft = property.area_sqft ? property.price / property.area_sqft : Infinity

  if (features.featured === true || /premium|luxury/.test(title)) {
    badges.push({ label: 'Featured', className: BADGE_STYLES.Featured })
  }

  if (property.price >= 15000000 || /villa|luxury|premium/.test(title)) {
    badges.push({ label: 'Luxury', className: BADGE_STYLES.Luxury })
  }

  if (property.year_built >= currentYear - 3) {
    badges.push({ label: 'New', className: BADGE_STYLES.New })
  }

  if (pricePerSqft <= 8000) {
    badges.push({ label: 'Best Value', className: BADGE_STYLES['Best Value'] })
  }

  return badges
}

export function getRecommendationScore(property) {
  const badges = getPropertyBadges(property)
  let score = 0

  badges.forEach((badge) => {
    if (badge.label === 'New') score += 2
    if (badge.label === 'Best Value') score += 2
    if (badge.label === 'Featured') score += 1
  })

  return score
}

export function getAgentForProperty(propertyId) {
  return AGENTS[propertyId % AGENTS.length]
}

export function getNearbyFacilities(propertyId, city) {
  const base = propertyId * 0.3
  const cityLabel = city || 'City'
  const landmarks = [
    { icon: '🏫', name: `${cityLabel} International School`, type: 'School' },
    { icon: '🏥', name: `${cityLabel} General Hospital`, type: 'Hospital' },
    { icon: '🚇', name: `${cityLabel} Metro Station`, type: 'Metro' },
    { icon: '🛍️', name: `${cityLabel} Central Mall`, type: 'Mall' },
    { icon: '🌳', name: `${cityLabel} Riverside Park`, type: 'Park' },
  ]

  return landmarks.map((facility, index) => ({
    ...facility,
    distance: `${(0.4 + ((base + index) % 15) * 0.2).toFixed(1)} km`,
  }))
}

export function getPropertyFeatures(property) {
  if (!property?.features) return []

  const features = []
  if (property.features.furnished) features.push({ label: 'Furnished', value: 'Yes', icon: '🛋️' })
  if (property.features.balcony) features.push({ label: 'Balcony', value: 'Yes', icon: '🌅' })
  if (property.features.gym) features.push({ label: 'Gym', value: 'Available', icon: '🏋️' })
  if (property.features.pool) features.push({ label: 'Pool', value: 'Available', icon: '🏊' })
  if (property.features.garden) features.push({ label: 'Garden', value: 'Available', icon: '🌿' })
  if (property.features.security) features.push({ label: 'Security', value: '24/7', icon: '🛡️' })
  if (property.parking > 0) features.push({ label: 'Parking', value: `${property.parking} space${property.parking > 1 ? 's' : ''}`, icon: '🚗' })

  return features
}

export function getPropertyAge(yearBuilt) {
  return new Date().getFullYear() - yearBuilt
}

export function isFurnished(property) {
  return property?.features?.furnished === true ? 'Yes' : 'No'
}
