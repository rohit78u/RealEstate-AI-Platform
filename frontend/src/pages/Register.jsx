import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ fullName: '', email: '', password: '' })
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await register(form.email, form.password, form.fullName)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">Register</h1>
      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 p-6 space-y-4">
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <div>
          <label className="text-sm font-medium text-slate-700">Full Name</label>
          <input value={form.fullName} onChange={(e) => setForm({ ...form, fullName: e.target.value })} required
            className="w-full mt-1 border border-slate-300 rounded-lg px-3 py-2" />
        </div>
        <div>
          <label className="text-sm font-medium text-slate-700">Email</label>
          <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required
            className="w-full mt-1 border border-slate-300 rounded-lg px-3 py-2" />
        </div>
        <div>
          <label className="text-sm font-medium text-slate-700">Password</label>
          <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required minLength={6}
            className="w-full mt-1 border border-slate-300 rounded-lg px-3 py-2" />
        </div>
        <button type="submit" className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700">
          Create Account
        </button>
        <p className="text-sm text-center text-slate-500">
          Already have an account? <Link to="/login" className="text-primary-600 font-medium">Login</Link>
        </p>
      </form>
    </div>
  )
}
