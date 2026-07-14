import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await login(email, password)
      navigate('/')
    } catch {
      setError('Invalid email or password')
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">Login</h1>
      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 p-6 space-y-4">
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <div>
          <label className="text-sm font-medium text-slate-700">Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
            className="w-full mt-1 border border-slate-300 rounded-lg px-3 py-2" />
        </div>
        <div>
          <label className="text-sm font-medium text-slate-700">Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required
            className="w-full mt-1 border border-slate-300 rounded-lg px-3 py-2" />
        </div>
        <button type="submit" className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700">
          Login
        </button>
        <p className="text-sm text-center text-slate-500">
          No account? <Link to="/register" className="text-primary-600 font-medium">Register</Link>
        </p>
      </form>
    </div>
  )
}
