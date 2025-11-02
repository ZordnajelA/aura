import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Navigation() {
  const { user, logout } = useAuth()
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Aura</h1>
          <p className="text-sm text-gray-500">Universal Capture & PKM Assistant</p>
        </div>

        <div className="flex items-center gap-6">
          {/* Navigation Links */}
          <nav className="flex items-center gap-4">
            <Link
              to="/"
              className={`px-3 py-2 rounded-lg font-medium transition ${
                isActive('/')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Home
            </Link>
            <Link
              to="/daily"
              className={`px-3 py-2 rounded-lg font-medium transition ${
                isActive('/daily')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Daily Notes
            </Link>
            <Link
              to="/para"
              className={`px-3 py-2 rounded-lg font-medium transition ${
                isActive('/para')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              PARA
            </Link>
          </nav>

          {/* User Info & Logout */}
          <div className="flex items-center gap-3 pl-6 border-l border-gray-200">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-700">{user?.email}</p>
              <p className="text-xs text-gray-500">Signed in</p>
            </div>
            <button
              onClick={logout}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-lg transition"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
