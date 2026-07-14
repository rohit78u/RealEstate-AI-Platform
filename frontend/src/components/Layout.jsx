import { Link, NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const navLinkClass = ({ isActive }) =>
  `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
    isActive ? 'bg-primary-600 text-white' : 'text-slate-600 hover:bg-slate-100'
  }`

export default function Layout() {
  const { user, logout, isAdmin } = useAuth()

  return (
    <div className="min-h-screen">
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <Link to="/" className="text-xl font-bold text-primary-700">
              RealEstate AI
            </Link>
            <div className="flex items-center gap-1">
              <NavLink to="/" className={navLinkClass} end>Home</NavLink>
              <NavLink to="/properties" className={navLinkClass}>Properties</NavLink>
              <NavLink to="/predict" className={navLinkClass}>Predict</NavLink>
              {user && <NavLink to="/chat" className={navLinkClass}>AI Chat</NavLink>}
              {user && <NavLink to="/dashboard" className={navLinkClass}>Dashboard</NavLink>}
              {isAdmin && <NavLink to="/admin" className={navLinkClass}>Admin</NavLink>}
            </div>
            <div className="flex items-center gap-3">
              {user ? (
                <>
                  <span className="text-sm text-slate-600">{user.full_name}</span>
                  <button onClick={logout} className="text-sm text-red-600 hover:text-red-700 font-medium">
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="text-sm font-medium text-primary-600 hover:text-primary-700">Login</Link>
                  <Link to="/register" className="text-sm font-medium bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700">
                    Register
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}
