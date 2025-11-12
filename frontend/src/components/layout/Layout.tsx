import { ReactNode, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Brain,
  Monitor,
  FolderOpen,
  Mic,
  Settings,
  Menu,
  X,
  Activity,
  Zap
} from 'lucide-react'

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const location = useLocation()

  const navigation = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity, path: '/' },
    { id: 'chat', label: 'AI Assistant', icon: Brain, path: '/chat' },
    { id: 'system', label: 'System', icon: Monitor, path: '/system' },
    { id: 'files', label: 'Files', icon: FolderOpen, path: '/files' },
    { id: 'voice', label: 'Voice', icon: Mic, path: '/voice' },
    { id: 'settings', label: 'Settings', icon: Settings, path: '/settings' },
  ]

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      {/* Sidebar */}
      <motion.aside
        className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-gray-800 border-r border-cyan-500/30 transition-all duration-300 ease-in-out`}
        initial={false}
        animate={{ width: sidebarOpen ? 256 : 64 }}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-cyan-500/30">
            {sidebarOpen && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center space-x-2"
              >
                <Zap className="w-8 h-8 text-cyan-400" />
                <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">
                  JARVIS
                </h1>
              </motion.div>
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.path
              const Icon = item.icon

              return (
                <Link
                  key={item.id}
                  to={item.path}
                  className={`flex items-center ${sidebarOpen ? 'justify-start' : 'justify-center'} p-3 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-500/50 text-cyan-400'
                      : 'hover:bg-gray-700 text-gray-300 hover:text-white'
                  }`}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  {sidebarOpen && (
                    <motion.span
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 }}
                      className="ml-3 font-medium"
                    >
                      {item.label}
                    </motion.span>
                  )}
                </Link>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-cyan-500/30">
            {sidebarOpen && (
              <div className="text-xs text-gray-400 text-center">
                <div className="flex items-center justify-center space-x-2 mb-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span>System Online</span>
                </div>
                <div>v2.0.0</div>
              </div>
            )}
          </div>
        </div>
      </motion.aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="bg-gray-800 border-b border-cyan-500/30 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">
                {navigation.find(item => item.path === location.pathname)?.label || 'JARVIS AI'}
              </h2>
            </div>

            <div className="flex items-center space-x-4">
              {/* Status Indicators */}
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-xs text-gray-400">AI</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-xs text-gray-400">System</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                  <span className="text-xs text-gray-400">Voice</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6 bg-gradient-to-br from-gray-900 to-black">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="h-full"
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  )
}