import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from 'recharts'
import { useAuth } from '../context/AuthContext'
import api, { formatPrice } from '../services/api'

function StatCard({ label, value }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  )
}

function formatArea(value) {
  return `${Math.round(value).toLocaleString()} sqft`
}

function formatPerSqft(value) {
  return `₹${Math.round(value).toLocaleString()} / sqft`
}

export default function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [summary, setSummary] = useState(null)
  const [charts, setCharts] = useState(null)

  useEffect(() => {
    if (!user) { navigate('/login'); return }
    Promise.all([
      api.get('/dashboard/summary'),
      api.get('/dashboard/charts'),
    ]).then(([s, c]) => {
      setSummary(s.data)
      setCharts(c.data)
    })
  }, [user, navigate])

  if (!summary) return <p className="text-slate-500">Loading dashboard...</p>

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        <StatCard label="Total Properties" value={summary.total_properties} />
        <StatCard label="Total Area" value={formatArea(summary.total_area)} />
        <StatCard label="Average Area" value={formatArea(summary.average_area)} />
        <StatCard label="Average Price" value={formatPrice(summary.average_price)} />
        <StatCard label="Average Price / sqft" value={formatPrice(summary.average_price_per_sqft)} />
        <StatCard label="Highest Price" value={formatPrice(summary.highest_price)} />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Lowest Price" value={formatPrice(summary.lowest_price)} />
        <StatCard label="Median Price" value={formatPrice(summary.median_price)} />
        <StatCard label="Median Price / sqft" value={formatPerSqft(summary.median_price_per_sqft)} />
        <StatCard label="Total Predictions" value={summary.total_predictions} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold mb-4">Properties by City</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={charts?.properties_by_city || []}>
              <XAxis dataKey="city" tick={{ fontSize: 12 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold mb-4">Bedroom Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={charts?.property_bedroom_distribution || []}>
              <XAxis dataKey="bedrooms" tick={{ fontSize: 12 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold mb-4">Price Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={charts?.price_distribution || []}>
              <XAxis dataKey="range_label" tick={{ fontSize: 11 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold mb-4">Price / sqft by City</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={charts?.price_per_sqft_by_city || []}>
              <XAxis dataKey="city" tick={{ fontSize: 12 }} />
              <YAxis tickFormatter={(v) => `₹${Math.round(v)}`} />
              <Tooltip formatter={(v) => formatPerSqft(v)} />
              <Bar dataKey="average_price_per_sqft" fill="#f97316" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold mb-4">Prediction Trend (30 days)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={charts.prediction_trend || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold mb-4">Recent Listings</h3>
          <div className="space-y-3">
            {charts?.recent_listings?.map((p) => (
              <div key={p.id} className="flex justify-between items-center py-2 border-b border-slate-100 last:border-0">
                <div>
                  <p className="font-medium">{p.title}</p>
                  <p className="text-sm text-slate-500">{p.city}</p>
                </div>
                <p className="font-semibold text-primary-700">{formatPrice(p.price)}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold mb-4">Top 5 Most Expensive</h3>
          <div className="space-y-3">
            {charts?.top_expensive?.map((p) => (
              <div key={p.id} className="flex justify-between items-center py-2 border-b border-slate-100 last:border-0">
                <div>
                  <p className="font-medium">{p.title}</p>
                  <p className="text-sm text-slate-500">{p.city}</p>
                </div>
                <p className="font-semibold text-primary-700">{formatPrice(p.price)}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
