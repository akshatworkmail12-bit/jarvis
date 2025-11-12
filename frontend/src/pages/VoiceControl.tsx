import { useState } from 'react'
import { motion } from 'framer-motion'
import { Mic, MicOff, Volume2, Settings, Play } from 'lucide-react'

export function VoiceControl() {
  const [isEnabled, setIsEnabled] = useState(true)
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [volume, setVolume] = useState(75)
  const [rate, setRate] = useState(1.0)

  return (
    <div className="space-y-6">
      <motion.h1
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400"
      >
        Voice Control
      </motion.h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Voice Control Panel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="cyber-card"
        >
          <h3 className="text-xl font-bold text-cyan-400 mb-6">Voice Control Panel</h3>

          <div className="flex flex-col items-center space-y-6">
            {/* Voice Status Indicator */}
            <div className="relative">
              <div className={`w-32 h-32 rounded-full flex items-center justify-center ${
                isListening
                  ? 'bg-red-500/20 border-4 border-red-500 animate-pulse'
                  : isEnabled
                    ? 'bg-green-500/20 border-4 border-green-500'
                    : 'bg-gray-500/20 border-4 border-gray-500'
              }`}>
                {isListening ? (
                  <MicOff className="w-12 h-12 text-red-400" />
                ) : (
                  <Mic className="w-12 h-12 text-green-400" />
                )}
              </div>
              {isListening && (
                <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
                  <div className="flex space-x-1">
                    <div className="w-1 h-8 bg-red-400 animate-pulse"></div>
                    <div className="w-1 h-12 bg-red-400 animate-pulse" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-1 h-10 bg-red-400 animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-1 h-14 bg-red-400 animate-pulse" style={{ animationDelay: '0.3s' }}></div>
                    <div className="w-1 h-8 bg-red-400 animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              )}
            </div>

            {/* Control Buttons */}
            <div className="flex space-x-4">
              <button
                onClick={() => setIsListening(!isListening)}
                disabled={!isEnabled}
                className={`cyber-button ${isListening ? 'danger' : ''}`}
              >
                {isListening ? (
                  <><MicOff className="w-5 h-5 mr-2" /> Stop Listening</>
                ) : (
                  <><Mic className="w-5 h-5 mr-2" /> Start Listening</>
                )}
              </button>

              <button className="cyber-button secondary">
                <Settings className="w-5 h-5 mr-2" />
                Settings
              </button>
            </div>

            {/* Status Text */}
            <div className="text-center">
              <p className="text-lg font-medium">
                {isListening ? 'Listening...' : isEnabled ? 'Ready' : 'Disabled'}
              </p>
              <p className="text-sm text-gray-400">
                {isListening
                  ? 'Speak your command clearly'
                  : 'Click "Start Listening" to begin voice control'
                }
              </p>
            </div>
          </div>
        </motion.div>

        {/* Voice Settings */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="cyber-card"
        >
          <h3 className="text-xl font-bold text-cyan-400 mb-6">Voice Settings</h3>

          <div className="space-y-6">
            {/* Enable/Disable Voice */}
            <div>
              <label className="flex items-center justify-between">
                <span className="text-sm font-medium">Enable Voice Control</span>
                <button
                  onClick={() => setIsEnabled(!isEnabled)}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    isEnabled ? 'bg-green-500' : 'bg-gray-600'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    isEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`}></div>
                </button>
              </label>
            </div>

            {/* Volume Control */}
            <div>
              <label className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Volume</span>
                <span className="text-sm text-cyan-400">{volume}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={volume}
                onChange={(e) => setVolume(parseInt(e.target.value))}
                className="w-full"
                disabled={!isEnabled}
              />
            </div>

            {/* Speech Rate */}
            <div>
              <label className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Speech Rate</span>
                <span className="text-sm text-cyan-400">{rate}x</span>
              </label>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={rate}
                onChange={(e) => setRate(parseFloat(e.target.value))}
                className="w-full"
                disabled={!isEnabled}
              />
            </div>

            {/* Test Voice */}
            <div>
              <button className="cyber-button secondary w-full">
                <Volume2 className="w-4 h-4 mr-2" />
                Test Voice Output
              </button>
            </div>
          </div>
        </motion.div>

        {/* Voice Commands */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2"
        >
          <div className="cyber-card">
            <h3 className="text-xl font-bold text-cyan-400 mb-6">Voice Commands</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { command: 'Open Chrome', description: 'Opens Chrome browser' },
                { command: 'Play music', description: 'Plays music from YouTube' },
                { command: 'What time is it?', description: 'Tells current time' },
                { command: 'Show desktop', description: 'Minimizes all windows' },
                { command: 'Search files', description: 'Opens file search' },
                { command: 'Take screenshot', description: 'Captures screen' },
              ].map((item, index) => (
                <div key={index} className="p-4 bg-gray-800 rounded-lg border border-gray-700 hover:border-cyan-500/50 transition-colors">
                  <div className="flex items-center space-x-2 mb-2">
                    <Play className="w-4 h-4 text-cyan-400" />
                    <span className="font-mono text-sm">{item.command}</span>
                  </div>
                  <p className="text-xs text-gray-400">{item.description}</p>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Voice History */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="cyber-card"
        >
          <h3 className="text-xl font-bold text-cyan-400 mb-6">Voice History</h3>

          <div className="space-y-3">
            <div className="text-center text-gray-400 py-8">
              <Mic className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>Voice history will appear here</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}