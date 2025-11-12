import { useState } from 'react'
import { motion } from 'framer-motion'
import { Search, FolderOpen, File, HardDrive, Upload, Download } from 'lucide-react'

export function FileManager() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedPath, setSelectedPath] = useState('')

  return (
    <div className="space-y-6">
      <motion.h1
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400"
      >
        File Manager
      </motion.h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Search and Actions */}
        <div className="lg:col-span-3">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="cyber-card"
          >
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search files and folders..."
                    className="cyber-input pl-10 w-full"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <button className="cyber-button">
                  <Upload className="w-4 h-4 mr-2" />
                  Upload
                </button>
                <button className="cyber-button secondary">
                  <HardDrive className="w-4 h-4 mr-2" />
                  Disk Usage
                </button>
              </div>
            </div>
          </motion.div>
        </div>

        {/* File Browser */}
        <div className="lg:col-span-2">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="cyber-card h-96"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-cyan-400">File Browser</h3>
              <button className="cyber-button secondary">Refresh</button>
            </div>

            <div className="border border-gray-700 rounded-lg h-80 overflow-auto">
              <div className="p-4 text-center text-gray-400">
                <FolderOpen className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>File browser will be implemented here</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Quick Actions */}
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="cyber-card"
          >
            <h3 className="text-lg font-bold text-cyan-400 mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <button className="cyber-button secondary w-full text-left">
                <FolderOpen className="w-4 h-4 mr-2 inline" />
                Documents Folder
              </button>
              <button className="cyber-button secondary w-full text-left">
                <Download className="w-4 h-4 mr-2 inline" />
                Downloads Folder
              </button>
              <button className="cyber-button secondary w-full text-left">
                <File className="w-4 h-4 mr-2 inline" />
                Recent Files
              </button>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="cyber-card"
          >
            <h3 className="text-lg font-bold text-cyan-400 mb-4">File Types</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Documents:</span>
                <span>0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Images:</span>
                <span>0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Videos:</span>
                <span>0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Audio:</span>
                <span>0</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}