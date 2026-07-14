import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Properties from './pages/Properties'
import PropertyDetail from './pages/PropertyDetail'
import Predict from './pages/Predict'
import Chat from './pages/Chat'
import Dashboard from './pages/Dashboard'
import Admin from './pages/Admin'
import Login from './pages/Login'
import Register from './pages/Register'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="properties" element={<Properties />} />
        <Route path="properties/:id" element={<PropertyDetail />} />
        <Route path="predict" element={<Predict />} />
        <Route path="chat" element={<Chat />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="admin" element={<Admin />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
      </Route>
    </Routes>
  )
}
