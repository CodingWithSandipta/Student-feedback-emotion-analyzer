import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import {
  LayoutDashboard, MessageSquareText, List, BookOpen,
  BarChart3, Brain, Info, Menu, X, Activity, CheckCircle, AlertCircle
} from 'lucide-react'
import { getHealth } from './services/api'

// Pages
import Dashboard from './pages/Dashboard'
import AnalyzeFeedback from './pages/AnalyzeFeedback'
import FeedbackManagement from './pages/FeedbackManagement'
import CourseAnalytics from './pages/CourseAnalytics'
import SemesterAnalytics from './pages/SemesterAnalytics'
import ModelPerformance from './pages/ModelPerformance'
import About from './pages/About'

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard, exact: true },
  { path: '/analyze', label: 'Analyze Feedback', icon: MessageSquareText },
  { path: '/management', label: 'Feedback Management', icon: List },
  { path: '/courses', label: 'Course Analytics', icon: BookOpen },
  { path: '/semesters', label: 'Semester Analytics', icon: BarChart3 },
  { path: '/model', label: 'Model Performance', icon: Brain },
  { path: '/about', label: 'About Project', icon: Info },
]

function Sidebar({ open, onClose }) {
  return (
    <>
      {/* Overlay for mobile */}
      {open && (
        <div
          className="fixed inset-0 bg-black/50 z-20 lg:hidden"
          onClick={onClose}
        />
      )}
      <aside
        className={`
          fixed top-0 left-0 h-full w-64 z-30
          bg-gradient-to-b from-[#1e1b4b] to-[#0f0d2d]
          flex flex-col shadow-2xl
          transition-transform duration-300
          ${open ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 lg:static lg:z-auto
        `}
      >
        {/* Logo */}
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center">
              <Brain className="w-5 h-5 text-indigo-300" />
            </div>
            <div>
              <p className="text-white font-bold text-sm leading-tight">Feedback</p>
              <p className="text-indigo-300 font-bold text-sm leading-tight">Emotion AI</p>
            </div>
          </div>
          <p className="text-slate-400 text-xs mt-2">Bi-LSTM Powered Analytics</p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map(({ path, label, icon: Icon, exact }) => (
            <NavLink
              key={path}
              to={path}
              end={exact}
              onClick={onClose}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? 'active' : ''}`
              }
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-white/10">
          <p className="text-slate-500 text-xs text-center">Academic Project © 2024</p>
          <p className="text-slate-600 text-xs text-center mt-1">GoEmotions + Bi-LSTM</p>
        </div>
      </aside>
    </>
  )
}

function TopNav({ onMenuClick }) {
  const location = useLocation()
  const [health, setHealth] = useState(null)
  const [date, setDate] = useState('')

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await getHealth()
        setHealth(res.data)
      } catch {
        setHealth({ status: 'error', model_loaded: false, database_connected: false })
      }
    }
    checkHealth()
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const updateDate = () => {
      setDate(new Date().toLocaleDateString('en-IN', {
        weekday: 'short', day: 'numeric', month: 'short', year: 'numeric'
      }))
    }
    updateDate()
    const timer = setInterval(updateDate, 60000)
    return () => clearInterval(timer)
  }, [])

  const pageTitle = NAV_ITEMS.find(n => {
    if (n.exact) return location.pathname === n.path
    return location.pathname.startsWith(n.path)
  })?.label || 'Dashboard'

  const isHealthy = health?.status === 'healthy'
  const isModelLoaded = health?.model_loaded

  return (
    <header className="sticky top-0 z-10 bg-white/95 backdrop-blur-sm border-b border-slate-100 px-6 py-4 flex items-center justify-between shadow-sm">
      <div className="flex items-center gap-4">
        <button
          className="lg:hidden p-2 rounded-xl hover:bg-slate-100 transition-colors"
          onClick={onMenuClick}
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-lg font-bold text-slate-800">{pageTitle}</h1>
          <p className="text-xs text-slate-400">Student Feedback Emotion Analyzer</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden md:flex items-center gap-2 text-xs text-slate-500">
          <Activity className="w-3 h-3" />
          <span>{date}</span>
        </div>

        {/* System status */}
        <div className="flex items-center gap-2">
          {health == null ? (
            <span className="text-xs text-slate-400">Checking...</span>
          ) : (
            <div className="flex items-center gap-1.5">
              {isModelLoaded ? (
                <span className="flex items-center gap-1 text-xs text-emerald-600 font-medium">
                  <CheckCircle className="w-3.5 h-3.5" />
                  Model Ready
                </span>
              ) : (
                <span className="flex items-center gap-1 text-xs text-amber-600 font-medium">
                  <AlertCircle className="w-3.5 h-3.5" />
                  Model Not Trained
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex-1 flex flex-col min-w-0 overflow-auto">
        <TopNav onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analyze" element={<AnalyzeFeedback />} />
            <Route path="/management" element={<FeedbackManagement />} />
            <Route path="/courses" element={<CourseAnalytics />} />
            <Route path="/semesters" element={<SemesterAnalytics />} />
            <Route path="/model" element={<ModelPerformance />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout />
    </BrowserRouter>
  )
}
