import { Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { Dashboard } from '@/pages/Dashboard'
import { Chat } from '@/pages/Chat'
import { SystemInfo } from '@/pages/SystemInfo'
import { FileManager } from '@/pages/FileManager'
import { Settings } from '@/pages/Settings'
import { VoiceControl } from '@/pages/VoiceControl'
import { NotFound } from '@/pages/NotFound'

function App() {
  return (
    <div className="App">
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/system" element={<SystemInfo />} />
          <Route path="/files" element={<FileManager />} />
          <Route path="/voice" element={<VoiceControl />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Layout>
    </div>
  )
}

export default App