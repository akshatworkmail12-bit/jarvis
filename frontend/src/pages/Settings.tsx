import { useState } from 'react'
import { motion } from 'framer-motion'
import { Settings, Brain, Volume2, Monitor, Save, RotateCcw } from 'lucide-react'

export function Settings() {
  const [activeTab, setActiveTab] = useState('general')
  const [settings, setSettings] = useState({
    theme: 'cyberpunk',
    apiKey: '',
    apiBase: 'https://openrouter.ai/api/v1',
    model: 'openai/gpt-oss-20b:free',
    voiceEnabled: true,
    voiceRate: 230,
    voiceVolume: 1.0,
  })

  const tabs = [
    { id: 'general', label: 'General', icon: Settings },
    { id: 'ai', label: 'AI Settings', icon: Brain },
    { id: 'voice', label: 'Voice', icon: Volume2 },
    { id: 'system', label: 'System', icon: Monitor },
  ]

  return (
    <div className="space-y-6">
      <motion.h1
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400"
      >
        Settings
      </motion.h1>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Settings Navigation */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-1"
        >
          <div className="cyber-card">
            <nav className="space-y-2">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-cyan-500/20 border border-cyan-500/50 text-cyan-400'
                        : 'hover:bg-gray-700 text-gray-300'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{tab.label}</span>
                  </button>
                )
              })}
            </nav>
          </div>
        </motion.div>

        {/* Settings Content */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-3"
        >
          <div className="cyber-card">
            {/* General Settings */}
            {activeTab === 'general' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-cyan-400">General Settings</h3>

                <div>
                  <label className="block text-sm font-medium mb-2">Theme</label>
                  <select
                    value={settings.theme}
                    onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
                    className="cyber-input w-full"
                  >
                    <option value="cyberpunk">Cyberpunk</option>
                    <option value="dark">Dark</option>
                    <option value="light">Light</option>
                  </select>
                </div>

                <div>
                  <label className="flex items-center justify-between">
                    <span className="text-sm font-medium">Enable Notifications</span>
                    <button className="w-12 h-6 bg-green-500 rounded-full">
                      <div className="w-5 h-5 bg-white rounded-full translate-x-6"></div>
                    </button>
                  </label>
                </div>

                <div>
                  <label className="flex items-center justify-between">
                    <span className="text-sm font-medium">Enable Animations</span>
                    <button className="w-12 h-6 bg-green-500 rounded-full">
                      <div className="w-5 h-5 bg-white rounded-full translate-x-6"></div>
                    </button>
                  </label>
                </div>
              </div>
            )}

            {/* AI Settings */}
            {activeTab === 'ai' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-cyan-400">AI Configuration</h3>

                <div>
                  <label className="block text-sm font-medium mb-2">API Provider</label>
                  <select
                    value={settings.apiBase}
                    onChange={(e) => setSettings({ ...settings, apiBase: e.target.value })}
                    className="cyber-input w-full"
                  >
                    <option value="https://openrouter.ai/api/v1">OpenRouter</option>
                    <option value="https://api.openai.com/v1">OpenAI</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">API Key</label>
                  <input
                    type="password"
                    value={settings.apiKey}
                    onChange={(e) => setSettings({ ...settings, apiKey: e.target.value })}
                    placeholder="Enter your API key"
                    className="cyber-input w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Model</label>
                  <select
                    value={settings.model}
                    onChange={(e) => setSettings({ ...settings, model: e.target.value })}
                    className="cyber-input w-full"
                  >
                    <option value="openai/gpt-oss-20b:free">GPT-4O Mini (Free)</option>
                    <option value="openai/gpt-4o">GPT-4O</option>
                    <option value="anthropic/claude-3-haiku">Claude 3 Haiku</option>
                  </select>
                </div>

                <div className="p-4 bg-yellow-500/10 border border-yellow-500/50 rounded-lg">
                  <p className="text-sm text-yellow-400">
                    ⚠️ API keys are sensitive information. Keep them secure and never share them.
                  </p>
                </div>
              </div>
            )}

            {/* Voice Settings */}
            {activeTab === 'voice' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-cyan-400">Voice Configuration</h3>

                <div>
                  <label className="flex items-center justify-between">
                    <span className="text-sm font-medium">Enable Voice</span>
                    <button
                      onClick={() => setSettings({ ...settings, voiceEnabled: !settings.voiceEnabled })}
                      className={`w-12 h-6 rounded-full transition-colors ${
                        settings.voiceEnabled ? 'bg-green-500' : 'bg-gray-600'
                      }`}
                    >
                      <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                        settings.voiceEnabled ? 'translate-x-6' : 'translate-x-1'
                      }`}></div>
                    </button>
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Speech Rate: {settings.voiceRate}
                  </label>
                  <input
                    type="range"
                    min="100"
                    max="400"
                    value={settings.voiceRate}
                    onChange={(e) => setSettings({ ...settings, voiceRate: parseInt(e.target.value) })}
                    className="w-full"
                    disabled={!settings.voiceEnabled}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Volume: {Math.round(settings.voiceVolume * 100)}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={settings.voiceVolume * 100}
                    onChange={(e) => setSettings({ ...settings, voiceVolume: parseInt(e.target.value) / 100 })}
                    className="w-full"
                    disabled={!settings.voiceEnabled}
                  />
                </div>
              </div>
            )}

            {/* System Settings */}
            {activeTab === 'system' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-cyan-400">System Configuration</h3>

                <div>
                  <label className="flex items-center justify-between">
                    <span className="text-sm font-medium">Enable Auto-Start</span>
                    <button className="w-12 h-6 bg-gray-600 rounded-full">
                      <div className="w-5 h-5 bg-white rounded-full translate-x-1"></div>
                    </button>
                  </label>
                </div>

                <div>
                  <label className="flex items-center justify-between">
                    <span className="text-sm font-medium">Enable System Tray</span>
                    <button className="w-12 h-6 bg-green-500 rounded-full">
                      <div className="w-5 h-5 bg-white rounded-full translate-x-6"></div>
                    </button>
                  </label>
                </div>

                <div>
                  <label className="flex items-center justify-between">
                    <span className="text-sm font-medium">Enable Background Processing</span>
                    <button className="w-12 h-6 bg-green-500 rounded-full">
                      <div className="w-5 h-5 bg-white rounded-full translate-x-6"></div>
                    </button>
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Log Level</label>
                  <select className="cyber-input w-full">
                    <option value="debug">Debug</option>
                    <option value="info">Info</option>
                    <option value="warning">Warning</option>
                    <option value="error">Error</option>
                  </select>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex justify-between pt-6 border-t border-gray-700">
              <button className="cyber-button danger">
                <RotateCcw className="w-4 h-4 mr-2" />
                Reset to Defaults
              </button>
              <button className="cyber-button">
                <Save className="w-4 h-4 mr-2" />
                Save Settings
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}