import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import PropertySection from '../components/PropertySection'
import api from '../services/api'
import { getRecommendationScore } from '../utils/propertyUtils'

export default function Home() {
  const [trending, setTrending] = useState([])
  const [latest, setLatest] = useState([])
  const [luxury, setLuxury] = useState([])
  const [recommended, setRecommended] = useState([])

  useEffect(() => {
    Promise.all([
      api.get('/properties', { params: { limit: 4, sort: 'price_desc' } }),
      api.get('/properties', { params: { limit: 4, sort: 'created_desc' } }),
      api.get('/properties', { params: { limit: 20, sort: 'price_desc' } }),
      api.get('/properties', { params: { limit: 20, sort: 'created_desc' } }),
    ])
      .then(([trendingRes, latestRes, luxuryRes, recommendedRes]) => {
        setTrending(trendingRes.data.items)
        setLatest(latestRes.data.items)
        setLuxury(
          luxuryRes.data.items.filter((item) => item.price >= 15000000).slice(0, 4)
        )
        setRecommended(
          [...recommendedRes.data.items]
            .sort((a, b) => getRecommendationScore(b) - getRecommendationScore(a))
            .slice(0, 4)
        )
      })
      .catch(() => {})
  }, [])

  const viewAllLink = (
    <Link to="/properties" className="text-primary-600 font-medium hover:text-primary-700">
      View all →
    </Link>
  )

  return (
    <div>
      <section className="bg-gradient-to-r from-primary-700 to-primary-900 rounded-2xl text-white p-10 mb-10">
        <h1 className="text-4xl font-bold mb-4">AI Real Estate Intelligence Platform</h1>
        <p className="text-primary-100 text-lg max-w-2xl mb-6">
          Browse properties, predict house prices with Machine Learning, and get AI-powered real estate advice.
        </p>
        <div className="flex gap-4">
          <Link
            to="/properties"
            className="bg-white text-primary-700 px-6 py-3 rounded-lg font-semibold hover:bg-primary-50 transition-colors duration-200"
          >
            Browse Properties
          </Link>
          <Link
            to="/predict"
            className="border border-white/40 px-6 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors duration-200"
          >
            Predict Price
          </Link>
        </div>
      </section>

      <PropertySection
        title="Trending Properties"
        properties={trending}
        viewAllLink={viewAllLink}
      />

      <PropertySection
        title="Latest Listings"
        properties={latest}
        viewAllLink={viewAllLink}
      />

      <PropertySection
        title="Luxury Collection"
        properties={luxury}
        viewAllLink={viewAllLink}
      />

      <PropertySection
        title="AI Recommended Properties"
        properties={recommended}
        viewAllLink={viewAllLink}
      />

      {trending.length === 0 &&
        latest.length === 0 &&
        luxury.length === 0 &&
        recommended.length === 0 && (
          <p className="text-slate-500 text-center py-12">
            No properties listed yet. Admin can add properties.
          </p>
        )}
    </div>
  )
}
