import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const { theme, toggle } = useTheme()
  const nav = useNavigate()
  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="brand">📰 FNDS</Link>
        <div className="nav-links">
          {user ? (
            <>
              <NavLink to="/dashboard">Dashboard</NavLink>
              <NavLink to="/analyze">Analyze</NavLink>
              <NavLink to="/history">History</NavLink>
              <NavLink to="/insights">Model Insights</NavLink>
              <NavLink to="/how-it-works">How It Works</NavLink>
              <NavLink to="/profile">Profile</NavLink>
              <button className="btn btn-ghost" onClick={() => { logout(); nav('/') }}>Logout</button>
            </>
          ) : (
            <>
              <NavLink to="/how-it-works">How It Works</NavLink>
              <NavLink to="/login">Login</NavLink>
              <Link to="/signup" className="btn btn-primary">Get Started</Link>
            </>
          )}
          <button className="btn btn-ghost" onClick={toggle} title="Toggle dark mode">
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>
      </div>
    </nav>
  )
}
