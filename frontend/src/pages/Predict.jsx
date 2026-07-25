import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { useAuth } from '../context/AuthContext'
import api, { formatPrice } from '../services/api'

const CITIES = ['Mumbai', 'Delhi', 'Bangalore', 'Pune', 'Hyderabad', 'Chennai']
const LOCATIONS = {
  Mumbai: ['Bandra', 'Andheri', 'Powai', 'Worli'],
  Delhi: ['Dwarka', 'Saket', 'Rohini', 'Connaught Place'],
  Bangalore: ['Koramangala', 'Indiranagar', 'Whitefield', 'HSR Layout'],
  Pune: ['Koregaon Park', 'Hinjewadi', 'Baner', 'Kothrud'],
  Hyderabad: ['Gachibowli', 'Banjara Hills', 'Madhapur', 'Kondapur'],
  Chennai: ['Adyar', 'Velachery', 'OMR', 'T Nagar'],
}

export default function Predict() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    city: 'Mumbai', location: 'Bandra', area_sqft: 1200, bedrooms: 2,
    bathrooms: 2, floors: 1, year_built: 2018, parking: 1,
  })
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!user) { navigate('/login'); return }
    // Client-side validation to match backend business rule
    if (Number(form.bathrooms) >= Number(form.bedrooms)) {
      setError('Bathrooms must be fewer than bedrooms')
      return
    }
    setLoading(true)
    setError('')
    try {
      const res = await api.post('/predictions', form)
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Prediction failed. Ensure ML model is trained.')
    } finally {
      setLoading(false)
    }
  }

  const chartData = result?.shap_contributions?.map((c) => ({
    name: c.feature.split('(')[0].trim(),
    impact: Math.abs(c.impact),
    direction: c.direction,
  })) || []

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-2">House Price Prediction</h1>
      <p className="text-slate-500 mb-8">Enter property details to get an ML-powered price estimate with SHAP explanations.</p>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 p-6 grid grid-cols-2 gap-4 mb-8">
        <div>
          <label className="text-sm font-medium text-slate-700">City</label>
          <select value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value, location: LOCATIONS[e.target.value][0] })}
            className="w-full mt-1 border border-slate-300 rounded-lg px-3 py-2">
            {CITIES.map((c) => <option key={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label className="text-sm font-medium text-slate-700">Location</label>
          <select value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })}
            className="w-full mt-1 border border-slate-300 rounded-lg px-3 py-2">
            {LOCATIONS[form.city].map((l) => <option key={l}>{l}</option>)}
          </select>
        </div>
        {[
          ['area_sqft', 'Area (sqft)', 'number'],
          ['bedrooms', 'Bedrooms', 'number'],
          ['bathrooms', 'Bathrooms', 'number'],
          ['floors', 'Floors', 'number'],
          ['year_built', 'Year Built', 'number'],
          ['parking', 'Parking Spaces', 'number'],
        ].map(([key, label, type]) => (
          <div key={key}>
            <label className="text-sm font-medium text-slate-700">{label}</label>
            <input type={type} value={form[key]} onChange={(e) => setForm({ ...form, [key]: Number(e.target.value) })}
              className="w-full mt-1 border border-slate-300 rounded-lg px-3 py-2" />
          </div>
        ))}
        <div className="col-span-2">
          <button type="submit" disabled={loading}
            className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 disabled:opacity-50">
            {loading ? 'Predicting...' : 'Predict Price'}
          </button>
        </div>
      </form>

      {error && <p className="text-red-600 bg-red-50 rounded-lg p-4 mb-6">{error}</p>}

      {result && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="text-center mb-6">
            <p className="text-sm text-slate-500">Estimated Price</p>
            <p className="text-4xl font-bold text-primary-700">{formatPrice(result.predicted_price)}</p>
            <p className="text-sm text-slate-500 mt-2">Confidence: {(result.confidence_score * 100).toFixed(0)}%</p>
          </div>

          <p className="text-slate-600 mb-6">{result.explanation}</p>

          <h3 className="font-semibold mb-4">SHAP Feature Importance</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData} layout="vertical">
              <XAxis type="number" tickFormatter={(v) => `₹${(v / 100000).toFixed(0)}L`} />
              <YAxis type="category" dataKey="name" width={100} tick={{ fontSize: 12 }} />
              <Tooltip formatter={(v) => formatPrice(v)} />
              <Bar dataKey="impact">
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.direction === 'positive' ? '#2563eb' : '#ef4444'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          <div className="mt-4 space-y-2">
            {result.shap_contributions.map((c, i) => (
              <div key={i} className="flex justify-between text-sm">
                <span>{c.feature}</span>
                <span className={c.direction === 'positive' ? 'text-green-600' : 'text-red-600'}>
                  {c.direction === 'positive' ? '+' : '-'}{formatPrice(Math.abs(c.impact))}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
