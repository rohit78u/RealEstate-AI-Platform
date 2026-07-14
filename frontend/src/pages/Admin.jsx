import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api, { formatPrice } from '../services/api'

const emptyForm = {
  title: '', description: '', price: '', bedrooms: 2, bathrooms: 2,
  area_sqft: '', floors: 1, year_built: 2020, parking: 1, city: 'Mumbai', location: '',
}

export default function Admin() {
  const { isAdmin } = useAuth()
  const navigate = useNavigate()
  const [properties, setProperties] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState(null)
  const [message, setMessage] = useState('')

  const fetchProperties = () => {
    api.get('/properties', { params: { limit: 100 } }).then((res) => setProperties(res.data.items))
  }

  useEffect(() => {
    if (!isAdmin) { navigate('/'); return }
    fetchProperties()
  }, [isAdmin, navigate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    const payload = { ...form, price: Number(form.price), area_sqft: Number(form.area_sqft) }
    try {
      if (editingId) {
        await api.put(`/properties/${editingId}`, payload)
        setMessage('Property updated!')
      } else {
        await api.post('/properties', payload)
        setMessage('Property created!')
      }
      setForm(emptyForm)
      setEditingId(null)
      fetchProperties()
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Operation failed')
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this property?')) return
    await api.delete(`/properties/${id}`)
    fetchProperties()
  }

  const handleImageUpload = async (id, files) => {
    const formData = new FormData()
    Array.from(files).forEach((f) => formData.append('files', f))
    await api.post(`/properties/${id}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    fetchProperties()
    setMessage('Images uploaded!')
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Admin Panel</h1>
      {message && <p className="bg-green-50 text-green-700 rounded-lg p-3 mb-4">{message}</p>}

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 p-6 grid grid-cols-2 gap-4 mb-8">
        <h2 className="col-span-2 font-semibold text-lg">{editingId ? 'Edit Property' : 'Add Property'}</h2>
        {[
          ['title', 'Title', 'text'],
          ['description', 'Description', 'text'],
          ['price', 'Price (₹)', 'number'],
          ['area_sqft', 'Area (sqft)', 'number'],
          ['city', 'City', 'text'],
          ['location', 'Location', 'text'],
          ['bedrooms', 'Bedrooms', 'number'],
          ['bathrooms', 'Bathrooms', 'number'],
          ['floors', 'Floors', 'number'],
          ['year_built', 'Year Built', 'number'],
          ['parking', 'Parking', 'number'],
        ].map(([key, label, type]) => (
          <div key={key}>
            <label className="text-sm font-medium text-slate-700">{label}</label>
            <input type={type} value={form[key]} required={key !== 'description'}
              onChange={(e) => setForm({ ...form, [key]: type === 'number' ? Number(e.target.value) : e.target.value })}
              className="w-full mt-1 border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </div>
        ))}
        <div className="col-span-2 flex gap-3">
          <button type="submit" className="bg-primary-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-primary-700">
            {editingId ? 'Update' : 'Create'}
          </button>
          {editingId && (
            <button type="button" onClick={() => { setEditingId(null); setForm(emptyForm) }}
              className="border border-slate-300 px-6 py-2 rounded-lg text-sm">Cancel</button>
          )}
        </div>
      </form>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="text-left p-4">Title</th>
              <th className="text-left p-4">City</th>
              <th className="text-left p-4">Price</th>
              <th className="text-left p-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {properties.map((p) => (
              <tr key={p.id} className="border-t border-slate-100">
                <td className="p-4 font-medium">{p.title}</td>
                <td className="p-4">{p.city}</td>
                <td className="p-4">{formatPrice(p.price)}</td>
                <td className="p-4 flex gap-2 items-center">
                  <button onClick={() => { setEditingId(p.id); setForm({ ...p, price: p.price }) }}
                    className="text-primary-600 text-xs font-medium">Edit</button>
                  <button onClick={() => handleDelete(p.id)}
                    className="text-red-600 text-xs font-medium">Delete</button>
                  <label className="text-xs text-slate-500 cursor-pointer">
                    Upload Images
                    <input type="file" multiple accept="image/*" className="hidden"
                      onChange={(e) => handleImageUpload(p.id, e.target.files)} />
                  </label>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
