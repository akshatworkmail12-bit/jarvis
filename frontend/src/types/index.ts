// JARVIS AI Frontend TypeScript Type Definitions

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: {
    error_code: string
    message: string
    details?: Record<string, any>
  }
}

export interface CommandRequest {
  command: string
  user_id?: string
  last_actions?: string[]
}

export interface CommandResponse {
  success: boolean
  response: string
  action: string
  execution_time: number
  data?: {
    [key: string]: any
  }
}

export interface SystemInfo {
  os: string
  platform: string
  architecture: string[]
  processor: string
  python_version: string
  search_locations: string[]
  installed_apps_count: number
  screen_size: [number, number]
  windows_version?: string
  computer_name?: string
  user_name?: string
}

export interface ScreenInfo {
  width: number
  height: number
  resolution: string
  failsafe_enabled: boolean
  pause_duration: number
  primary_monitor: boolean
}

export interface VoiceStatus {
  enabled: boolean
  listening: boolean
  speaking: boolean
  tts_available: boolean
  stt_available: boolean
  current_voice: {
    available: boolean
    id?: string
    name?: string
  }
  speech_rate: number
  volume: number
  energy_threshold: number
}

export interface FileInfo {
  path: string
  name: string
  parent: string
  size: number
  size_human: string
  created: string
  modified: string
  accessed: string
  type: 'file' | 'folder'
  extension?: string
  category?: string
  item_count?: number
}

export interface SearchResult {
  query: string
  file_type?: string
  results: FileInfo[]
  count: number
  searched_locations: string[]
}

export interface YouTubeVideo {
  title: string
  link: string
  duration: string
  views: string
  channel: string
  thumbnail: string
  description: string
  published_time: string
}

export interface MediaStatus {
  yt_dlp_available: boolean
  yt_dlp_version?: string
  youtube_search_python_available: boolean
  youtube_search_python_version?: string
  web_browser_available: boolean
  features: {
    youtube_search: boolean
    youtube_direct_play: boolean
    video_info_extraction: boolean
    web_browsing: boolean
  }
}

export interface AppStatus {
  system: SystemInfo
  screen: ScreenInfo
  vision: {
    screen_capture: boolean
    ai_analysis: boolean
    clicking: boolean
    scrolling: boolean
    errors: string[]
    success: boolean
  }
  capabilities: {
    screen_capture: boolean
    ai_analysis: boolean
    clicking: boolean
    scrolling: boolean
    typing: boolean
    keyboard: boolean
    app_management: boolean
    file_operations: boolean
  }
  status: 'operational' | 'degraded' | 'offline'
}

export interface ChatMessage {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  action?: string
  data?: any
}

export interface Application {
  name: string
  path: string
}

export interface DiskUsage {
  path: string
  total_bytes: number
  used_bytes: number
  free_bytes: number
  total_human: string
  used_human: string
  free_human: string
  usage_percent: number
}

export interface NavigationItem {
  id: string
  label: string
  icon: string
  path: string
  badge?: string | number
}

export interface ThemeConfig {
  primary: string
  secondary: string
  accent: string
  background: string
  text: string
}

export interface UserSettings {
  theme: 'cyberpunk' | 'dark' | 'light'
  voiceSettings: {
    enabled: boolean
    rate: number
    volume: number
    pitch: number
  }
  apiSettings: {
    apiKey: string
    apiBase: string
    model: string
    provider: string
  }
  uiSettings: {
    compactMode: boolean
    animationsEnabled: boolean
    notificationsEnabled: boolean
  }
}

export interface ActivityLog {
  id: string
  timestamp: Date
  action: string
  target: string
  success: boolean
  duration: number
  details?: Record<string, any>
}

export interface DiagnosticsData {
  cpu: {
    usage: number
    cores: number
    temperature?: number
  }
  memory: {
    total: number
    used: number
    available: number
    percentage: number
  }
  disk: DiskUsage[]
  network: {
    connected: boolean
    download_speed?: number
    upload_speed?: number
  }
  services: {
    ai: 'online' | 'offline' | 'error'
    voice: 'online' | 'offline' | 'error'
    vision: 'online' | 'offline' | 'error'
    system: 'online' | 'offline' | 'error'
    files: 'online' | 'offline' | 'error'
    media: 'online' | 'offline' | 'error'
  }
}

export interface VoiceCommand {
  id: string
  command: string
  confidence: number
  timestamp: Date
  processed: boolean
}

export interface ScreenAnalysis {
  action: 'CLICK' | 'INFORMATION' | 'NOT_FOUND'
  target_description: string
  approximate_position: {
    x: number
    y: number
  }
  confidence: 'high' | 'medium' | 'low'
  reasoning: string
  response: string
}

export interface Extension {
  id: string
  name: string
  version: string
  description: string
  author: string
  enabled: boolean
  installed: boolean
  config?: Record<string, any>
  dependencies?: string[]
}

export interface ApiEndpoint {
  path: string
  method: string
  description: string
  parameters?: Record<string, any>
}

export interface HealthCheck {
  status: 'healthy' | 'unhealthy'
  services: Record<string, 'operational' | 'degraded' | 'offline'>
  timestamp: string
  uptime?: number
}

// Utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

export type RequiredBy<T, K extends keyof T> = T & Required<Pick<T, K>>