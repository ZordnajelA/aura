import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import DailyNotesPage from './pages/DailyNotesPage'
import PARAPage from './pages/PARAPage'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/daily" element={<DailyNotesPage />} />
          <Route path="/para" element={<PARAPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
