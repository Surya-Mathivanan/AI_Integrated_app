import { Route, Routes, Link, Navigate } from 'react-router-dom'
import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import Questionnaire from './pages/Questionnaire'
import Pathway from './pages/Pathway'
import Chat from './pages/Chat'
import ExportPage from './pages/Export'
import ThemeToggle from './components/ThemeToggle'
import ProtectedRoute from './components/ProtectedRoute'
import { useAuthStore } from './store/auth'
import GoogleSignIn from './pages/GoogleSignIn'

export default function App() {
  const { user, logout } = useAuthStore()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const closeSidebar = () => setSidebarOpen(false)

  return (
    <div className="app">
      {/* Mobile Sidebar */}
      <div className={`mobile-sidebar-overlay ${sidebarOpen ? 'open' : ''}`} onClick={closeSidebar} />
      <div className={`mobile-sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="mobile-sidebar-content">
          <Link to="/" className="brand" onClick={closeSidebar}>Career Prep AI</Link>
          {user ? (
            <div className="mobile-nav-links">
              <Link to="/dashboard" className="navlink" onClick={closeSidebar}>
                <span>📊</span> Dashboard
              </Link>
              <Link to="/pathway" className="navlink" onClick={closeSidebar}>
                <span>🗺️</span> Pathway
              </Link>
              <Link to="/chat" className="navlink" onClick={closeSidebar}>
                <span>💬</span> Chat
              </Link>
              <div style={{ marginTop: 'auto', paddingTop: '24px' }}>
                <button className="btn" onClick={() => { logout(); closeSidebar(); }} style={{ width: '100%' }}>
                  Logout
                </button>
              </div>
            </div>
          ) : (
            <div className="mobile-nav-links">
              <Link to="/signin" className="navlink" onClick={closeSidebar}>
                <span>🔐</span> Continue with Google
              </Link>
            </div>
          )}
        </div>
      </div>

      <header className="header">
        <nav className="container nav">
          <div className={`hamburger ${sidebarOpen ? 'open' : ''}`} onClick={() => setSidebarOpen(!sidebarOpen)}>
            <span></span>
            <span></span>
            <span></span>
          </div>
          <Link to="/" className="brand">Career Prep AI</Link>
          <div className="spacer" />
          <ThemeToggle />
          {user ? (
            <>
              <Link to="/dashboard" className="navlink">Dashboard</Link>
              <Link to="/pathway" className="navlink">Pathway</Link>
              <Link to="/chat" className="navlink">Chat</Link>
              
              <button className="btn" onClick={() => logout()}>Logout</button>
            </>
          ) : (
            <Link to="/signin" className="navlink mobile-only">Sign In</Link>
          )}
        </nav>
      </header>
      <main className="container main">
        <Routes>
          <Route path="/" element={<Navigate to={user ? '/dashboard' : '/signin'} replace />} />
          <Route path="/signin" element={<GoogleSignIn />} />
          <Route path="/questionnaire" element={<ProtectedRoute><Questionnaire /></ProtectedRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/pathway" element={<ProtectedRoute><Pathway /></ProtectedRoute>} />
          <Route path="/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
          <Route path="/export" element={<ProtectedRoute><ExportPage /></ProtectedRoute>} />
        </Routes>
      </main>
    </div>
  )
}