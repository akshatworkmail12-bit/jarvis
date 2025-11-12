import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Monitor,
  Processor,
  HardDrive,
  Zap,
  RefreshCw,
  Camera,
  Eye,
  MousePointer,
  Keyboard,
  Download
} from 'lucide-react'
import { apiService } from '@/services/api'
import type { SystemInfo, AppStatus, ScreenInfo } from '@/types'

export function SystemInfo() {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null)
  const [appStatus, setAppStatus] = useState<AppStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    loadSystemInfo()
  }, [])

  const loadSystemInfo = async () => {
    try {
      setRefreshing(true)
      const [systemResponse, statusResponse] = await Promise.all([
        apiService.getSystemInfo(),
        apiService.getSystemStatus(),
      ])

      if (systemResponse.success) {
        setSystemInfo(systemResponse.data)
      }

      if (statusResponse.success) {
        setAppStatus(statusResponse.data)
      }
    } catch (error) {
      console.error('Failed to load system info:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const InfoCard = ({ title, icon: Icon, children, color = "cyber-card" }: {
    title: string
    icon: any
    children: React.ReactNode
    color?: string
  }) => (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className={color}
    >
      <div className="flex items-center mb-4">
        <Icon className="w-6 h-6 text-cyan-400 mr-2" />
        <h3 className="text-lg font-bold">{title}</h3>
      </div>
      {children}
    </motion.div>
  )

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
      <div className="flex items-center justify-between">
        <motion.h1
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400"
        >
          System Information
        </motion.h1>
        <button
          onClick={loadSystemInfo}
          disabled={refreshing}
          className="cyber-button"
        >
          <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Operating System Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <InfoCard title="Operating System" icon={Monitor}>
            {systemInfo && (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">System:</span>
                  <span>{systemInfo.os}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Platform:</span>
                  <span>{systemInfo.platform}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Architecture:</span>
                  <span>{systemInfo.architecture.join(', ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Processor:</span>
                  <span>{systemInfo.processor}</span>
                </div>
                {systemInfo.computer_name && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Computer:</span>
                    <span>{systemInfo.computer_name}</span>
                  </div>
                )}
                {systemInfo.user_name && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">User:</span>
                    <span>{systemInfo.user_name}</span>
                  </div>
                )}
              </div>
            )}
          </InfoCard>
        </motion.div>

        {/* Screen Information */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <InfoCard title="Screen Information" icon={Monitor}>
            {appStatus?.screen && (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Resolution:</span>
                  <span>{appStatus.screen.resolution}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Width:</span>
                  <span>{appStatus.screen.width}px</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Height:</span>
                  <span>{appStatus.screen.height}px</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Failsafe:</span>
                  <span className={appStatus.screen.failsafe_enabled ? 'text-green-400' : 'text-red-400'}>
                    {appStatus.screen.failsafe_enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Pause Duration:</span>
                  <span>{appStatus.screen.pause_duration}s</span>
                </div>
              </div>
            )}
          </InfoCard>
        </motion.div>

        {/* Capabilities */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <InfoCard title="System Capabilities" icon={Zap}>
            {appStatus?.capabilities && (
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(appStatus.capabilities).map(([key, enabled]) => (
                  <div
                    key={key}
                    className={`p-3 rounded-lg border text-center ${
                      enabled
                        ? 'border-green-500/50 bg-green-500/10'
                        : 'border-gray-600 bg-gray-800/50'
                    }`}
                  >
                    <div className={`text-sm font-medium capitalize ${
                      enabled ? 'text-green-400' : 'text-gray-500'
                    }`}>
                      {key.replace(/_/g, ' ')}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </InfoCard>
        </motion.div>

        {/* Vision Capabilities */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <InfoCard title="Vision Capabilities" icon={Eye}>
            {appStatus?.vision && (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className={`p-3 rounded-lg text-center ${
                    appStatus.vision.screen_capture
                      ? 'border border-green-500/50 bg-green-500/10'
                      : 'border border-gray-600 bg-gray-800/50'
                  }`}>
                    <Camera className="w-6 h-6 mx-auto mb-1 text-cyan-400" />
                    <div className="text-sm">Screen Capture</div>
                    <div className={`text-xs ${
                      appStatus.vision.screen_capture ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {appStatus.vision.screen_capture ? 'Working' : 'Disabled'}
                    </div>
                  </div>

                  <div className={`p-3 rounded-lg text-center ${
                    appStatus.vision.ai_analysis
                      ? 'border border-green-500/50 bg-green-500/10'
                      : 'border border-gray-600 bg-gray-800/50'
                  }`}>
                    <Eye className="w-6 h-6 mx-auto mb-1 text-purple-400" />
                    <div className="text-sm">AI Analysis</div>
                    <div className={`text-xs ${
                      appStatus.vision.ai_analysis ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {appStatus.vision.ai_analysis ? 'Working' : 'Disabled'}
                    </div>
                  </div>

                  <div className={`p-3 rounded-lg text-center ${
                    appStatus.vision.clicking
                      ? 'border border-green-500/50 bg-green-500/10'
                      : 'border border-gray-600 bg-gray-800/50'
                  }`}>
                    <MousePointer className="w-6 h-6 mx-auto mb-1 text-pink-400" />
                    <div className="text-sm">Click Control</div>
                    <div className={`text-xs ${
                      appStatus.vision.clicking ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {appStatus.vision.clicking ? 'Working' : 'Disabled'}
                    </div>
                  </div>

                  <div className={`p-3 rounded-lg text-center ${
                    appStatus.vision.scrolling
                      ? 'border border-green-500/50 bg-green-500/10'
                      : 'border border-gray-600 bg-gray-800/50'
                  }`}>
                    <RefreshCw className="w-6 h-6 mx-auto mb-1 text-yellow-400" />
                    <div className="text-sm">Scrolling</div>
                    <div className={`text-xs ${
                      appStatus.vision.scrolling ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {appStatus.vision.scrolling ? 'Working' : 'Disabled'}
                    </div>
                  </div>
                </div>

                {appStatus.vision.errors.length > 0 && (
                  <div className="mt-4 p-3 bg-red-500/10 border border-red-500/50 rounded-lg">
                    <div className="text-sm text-red-400 font-medium mb-1">Errors:</div>
                    {appStatus.vision.errors.map((error, index) => (
                      <div key={index} className="text-xs text-red-300">• {error}</div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </InfoCard>
        </motion.div>

        {/* Search Locations */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="lg:col-span-2"
        >
          <InfoCard title="Search Locations" icon={FolderOpen}>
            {systemInfo?.search_locations && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {systemInfo.search_locations.map((location, index) => (
                  <div
                    key={index}
                    className="p-3 bg-gray-800 rounded-lg border border-gray-700 hover:border-cyan-500/50 transition-colors"
                  >
                    <div className="flex items-center space-x-2">
                      <FolderOpen className="w-4 h-4 text-cyan-400" />
                      <span className="text-sm font-mono truncate">{location}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </InfoCard>
        </motion.div>

        {/* Test Functionality */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="lg:col-span-2"
        >
          <InfoCard title="System Tests" icon={Zap}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              <button className="cyber-button">
                <Camera className="w-4 h-4 mr-2" />
                Test Capture
              </button>
              <button className="cyber-button">
                <MousePointer className="w-4 h-4 mr-2" />
                Test Click
              </button>
              <button className="cyber-button">
                <Keyboard className="w-4 h-4 mr-2" />
                Test Type
              </button>
              <button className="cyber-button">
                <Download className="w-4 h-4 mr-2" />
                Run All Tests
              </button>
            </div>
          </InfoCard>
        </motion.div>
      </div>
    </div>
  )
}