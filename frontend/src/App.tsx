import { Navigate, Route, Routes } from 'react-router-dom'

import { Home } from './pages/Home'
import { Report } from './pages/Report'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/report/:id" element={<Report />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
