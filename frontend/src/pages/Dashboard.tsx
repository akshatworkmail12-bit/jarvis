import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Activity,
  Brain,
  Monitor,
  FolderOpen,
  Zap,
  Cpu,
  HardDrive,
  Wifi,
  MessageSquare,
  TrendingUp
} from 'lucide-react'
import { apiService } from '@/services/api'
import type { AppStatus, DiagnosticsData, ActivityLog } from '@/types'

export function Dashboard() {
  const [appStatus, setAppStatus] = useState<AppStatus | null>(null)
  const [diagnostics, setDiagnostics] = useState<DiagnosticsData | null>(null)
  const [recentActivity, setRecentActivity] = useState<ActivityLog[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
    const interval = setInterval(loadDashboardData, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const loadDashboardData = async () => {
    try {
      const [statusResponse] = await Promise.all([
        apiService.getSystemStatus(),
      ])

      if (statusResponse.success) {
        setAppStatus(statusResponse.data)
      }

      // Mock diagnostics data for now
      setDiagnostics({
        cpu: { usage: 45, cores: 8 },
        memory: { total: 16384, used: 8192, available: 8192, percentage: 50 },
        disk: [],
        network: { connected: true },
        services: {
          ai: 'online',
          voice: 'online',
          vision: 'online',
          system: 'online',
          files: 'online',
          media: 'online'
        }
      })

      setLoading(false)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      setLoading(false)
    }
  }

  const StatCard = ({ title, value, icon: Icon, color, trend }: {
    title: string
    value: string | number
    icon: any
    color: string
    trend?: { value: number; isPositive: boolean }
  }) => (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="cyber-card"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{title}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
          {trend && (
            <div className={`flex items-center mt-1 text-sm ${
              trend.isPositive ? 'text-green-400' : 'text-red-400'
            }`}>
              <TrendingUp className="w-4 h-4 mr-1" />
              {trend.value}%
            </div>
          )}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </motion.div>
  )

  const ServiceStatus = ({ name, status }: { name: string; status: string }) => {
    const getStatusColor = (status: string) => {
      switch (status) {
        case 'online': return 'bg-green-400'
        case 'degraded': return 'bg-yellow-400'
        case 'offline': return 'bg-red-400'
        default: return 'bg-gray-400'
      }
    }

    return (
      <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
        <span className="text-sm font-medium">{name}</span>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${getStatusColor(status)}`}></div>
          <span className="text-xs text-gray-400 capitalize">{status}</span>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="loading-spinner"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-4xl font-bold glitch mb-2">JARVIS AI</h1>
        <p className="text-gray-400">Professional Assistant Interface</p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="System Status"
          value="Online"
          icon={Activity}
          color="bg-green-500/20 text-green-400"
        />
        <StatCard
          title="CPU Usage"
          value={`${diagnostics?.cpu.usage || 0}%`}
          icon={Cpu}
          color="bg-blue-500/20 text-blue-400"
          trend={{ value: 5, isPositive: false }}
        />
        <StatCard
          title="Memory"
          value={`${diagnostics?.memory.percentage || 0}%`}
          icon={HardDrive}
          color="bg-purple-500/20 text-purple-400"
        />
        <StatCard
          title="Network"
          value={diagnostics?.network.connected ? "Connected" : "Offline"}
          icon={Wifi}
          color="bg-cyan-500/20 text-cyan-400"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Overview */}
        <div className="lg:col-span-2 space-y-6">
          {/* Capabilities */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="cyber-card"
          >
            <h2 className="text-xl font-bold mb-4 text-cyan-400">System Capabilities</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {[
                { name: 'Screen Analysis', enabled: appStatus?.capabilities?.screen_capture, icon: Monitor },
                { name: 'AI Processing', enabled: appStatus?.capabilities?.ai_analysis, icon: Brain },
                { name: 'File Operations', enabled: appStatus?.capabilities?.file_operations, icon: FolderOpen },
                { name: 'System Control', enabled: appStatus?.capabilities?.typing, icon: Zap },
                { name: 'Voice Control', enabled: true, icon: Mic },
                { name: 'Web Browsing', enabled: true, icon: Wifi },
              ].map((capability, index) => (
                <div
                  key={capability.name}
                  className={`flex flex-col items-center p-4 rounded-lg border ${
                    capability.enabled
                      ? 'border-green-500/50 bg-green-500/10'
                      : 'border-gray-600 bg-gray-800/50'
                  }`}
                >
                  <capability.icon className={`w-8 h-8 mb-2 ${
                    capability.enabled ? 'text-green-400' : 'text-gray-500'
                  }`} />
                  <span className="text-sm text-center">{capability.name}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Recent Activity */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="cyber-card"
          >
            <h2 className="text-xl font-bold mb-4 text-cyan-400">Recent Activity</h2>
            <div className="space-y-3">
              {recentActivity.length === 0 ? (
                <div className="text-center text-gray-400 py-8">
                  <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No recent activity</p>
                </div>
              ) : (
                recentActivity.map((activity, index) => (
                  <div key={activity.id} className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                    <div>
                      <p className="font-medium">{activity.action}</p>
                      <p className="text-xs text-gray-400">{activity.target}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-400">{activity.timestamp.toLocaleTimeString()}</p>
                      <p className={`text-xs ${activity.success ? 'text-green-400' : 'text-red-400'}`}>
                        {activity.success ? 'Success' : 'Failed'}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </motion.div>
        </div>

        {/* Services Status */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-6"
        >
          <div className="cyber-card">
            <h2 className="text-xl font-bold mb-4 text-cyan-400">Service Status</h2>
            <div className="space-y-3">
              {diagnostics?.services && Object.entries(diagnostics.services).map(([name, status]) => (
                <ServiceStatus
                  key={name}
                  name={name.charAt(0).toUpperCase() + name.slice(1)}
                  status={status}
                />
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="cyber-card">
            <h2 className="text-xl font-bold mb-4 text-cyan-400">Quick Actions</h2>
            <div className="space-y-3">
              <button className="cyber-button w-full">
                System Scan
              </button>
              <button className="cyber-button secondary w-full">
                Voice Settings
              </button>
              <button className="cyber-button secondary w-full">
                View Logs
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}