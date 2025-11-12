// JARVIS AI Frontend API Service
// Handles all communication with the backend API

import axios, { AxiosInstance, AxiosResponse } from 'axios'
import type {
  ApiResponse,
  CommandRequest,
  CommandResponse,
  SystemInfo,
  ScreenInfo,
  VoiceStatus,
  SearchResult,
  YouTubeVideo,
  MediaStatus,
  AppStatus,
  HealthCheck
} from '@/types'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('API Request Error:', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse<ApiResponse>) => {
        console.log(`API Response: ${response.status} ${response.config.url}`)
        return response
      },
      (error) => {
        console.error('API Response Error:', error.response?.data || error.message)
        return Promise.reject(error)
      }
    )
  }

  // Generic request method
  private async request<T>(
    method: string,
    url: string,
    data?: any,
    params?: any
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.request<ApiResponse<T>>({
        method,
        url,
        data,
        params,
      })
      return response.data
    } catch (error: any) {
      if (error.response?.data) {
        return error.response.data
      }
      throw error
    }
  }

  // Health and Status Endpoints
  async getHealth(): Promise<ApiResponse<HealthCheck>> {
    return this.request('GET', '/health')
  }

  async getApiDocs(): Promise<ApiResponse<any>> {
    return this.request('GET', '/api/docs')
  }

  // Command Endpoints
  async executeCommand(request: CommandRequest): Promise<ApiResponse<CommandResponse>> {
    return this.request('POST', '/api/v1/commands/execute', request)
  }

  async interpretCommand(command: string): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/commands/interpret', { command })
  }

  async getCommandHistory(): Promise<ApiResponse<any>> {
    return this.request('GET', '/api/v1/commands/history')
  }

  async getCommandSuggestions(partialCommand: string): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/commands/suggest', { partial_command: partialCommand })
  }

  // System Endpoints
  async getSystemInfo(): Promise<ApiResponse<SystemInfo>> {
    return this.request('GET', '/api/v1/system/info')
  }

  async getInstalledApplications(): Promise<ApiResponse<{ applications: Array<{ name: string; path: string }>, count: number }>> {
    return this.request('GET', '/api/v1/system/applications')
  }

  async openApplication(appName: string, executableHints?: string[]): Promise<ApiResponse<any>> {
    return this.request('POST', `/api/v1/system/applications/${encodeURIComponent(appName)}/open`, {
      executable_hints: executableHints || [],
    })
  }

  async openFolder(folderName: string, folderPaths?: string[]): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/system/folders/open', {
      folder_name: folderName,
      folder_paths: folderPaths || [],
    })
  }

  async captureScreen(region?: { x: number; y: number; width: number; height: number }): Promise<ApiResponse<{ screenshot: string; region?: any; timestamp: string }>> {
    return this.request('GET', '/api/v1/system/screen/capture', undefined, region)
  }

  async analyzeScreen(query: string, region?: { x: number; y: number; width: number; height: number }): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/system/screen/analyze', { query, region })
  }

  async clickScreen(x: number, y: number, duration?: number): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/system/screen/click', { x, y, duration })
  }

  async scrollScreen(direction: string, amount: number, x?: number, y?: number): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/system/screen/scroll', { direction, amount, x, y })
  }

  async typeText(text: string, interval?: number): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/system/keyboard/type', { text, interval })
  }

  async pressKey(key: string): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/system/keyboard/press', { key })
  }

  async executeSystemCommand(command: string): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/system/execute', { command })
  }

  async getSystemStatus(): Promise<ApiResponse<AppStatus>> {
    return this.request('GET', '/api/v1/system/status')
  }

  async testSystemFunctionality(): Promise<ApiResponse<any>> {
    return this.request('GET', '/api/v1/system/test')
  }

  // File Endpoints
  async searchFiles(query: string, fileType?: string, maxResults?: number, searchLocations?: string[]): Promise<ApiResponse<SearchResult>> {
    return this.request('POST', '/api/v1/files/search', {
      query,
      file_type: fileType,
      max_results: maxResults,
      search_locations: searchLocations,
    })
  }

  async getFileInfo(filePath: string): Promise<ApiResponse<any>> {
    return this.request('GET', `/api/v1/files/${encodeURIComponent(filePath)}/info`)
  }

  async openFile(filePath: string): Promise<ApiResponse<any>> {
    return this.request('POST', `/api/v1/files/${encodeURIComponent(filePath)}/open`)
  }

  async readFile(filePath: string, encoding?: string, maxSize?: number): Promise<ApiResponse<any>> {
    return this.request('GET', `/api/v1/files/${encodeURIComponent(filePath)}/read`, undefined, {
      encoding,
      max_size: maxSize,
    })
  }

  async writeFile(filePath: string, content: string, encoding?: string, backup?: boolean): Promise<ApiResponse<any>> {
    return this.request('POST', `/api/v1/files/${encodeURIComponent(filePath)}/write`, {
      content,
      encoding,
      backup,
    })
  }

  async listDirectory(dirPath: string, showHidden?: boolean): Promise<ApiResponse<any>> {
    return this.request('GET', `/api/v1/files/${encodeURIComponent(dirPath)}/list`, undefined, {
      show_hidden: showHidden,
    })
  }

  async createDirectory(dirPath: string): Promise<ApiResponse<any>> {
    return this.request('POST', `/api/v1/files/${encodeURIComponent(dirPath)}/create`)
  }

  async copyFile(filePath: string, destination: string): Promise<ApiResponse<any>> {
    return this.request('POST', `/api/v1/files/${encodeURIComponent(filePath)}/copy`, { destination })
  }

  async moveFile(filePath: string, destination: string): Promise<ApiResponse<any>> {
    return this.request('POST', `/api/v1/files/${encodeURIComponent(filePath)}/move`, { destination })
  }

  async deleteFile(filePath: string, permanent?: boolean): Promise<ApiResponse<any>> {
    return this.request('DELETE', `/api/v1/files/${encodeURIComponent(filePath)}/delete`, undefined, {
      permanent,
    })
  }

  async getDiskUsage(path?: string): Promise<ApiResponse<any>> {
    return this.request('GET', '/api/v1/files/disk-usage', undefined, { path })
  }

  async findDuplicates(directory: string, minSize?: number): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/files/duplicates', { directory, min_size: minSize })
  }

  async cleanupTempFiles(tempDirs?: string[]): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/files/cleanup', { temp_dirs: tempDirs })
  }

  async getFileServiceStatus(): Promise<ApiResponse<any>> {
    return this.request('GET', '/api/v1/files/status')
  }

  // Media Endpoints
  async searchWeb(query: string): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/media/web/search', { query })
  }

  async openWebsite(site: string): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/media/website/open', { site })
  }

  async browseUrl(url: string): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/media/browse', { url })
  }

  async searchYouTube(query: string, maxResults?: number): Promise<ApiResponse<{ videos: YouTubeVideo[] }>> {
    return this.request('POST', '/api/v1/media/youtube/search', { query, max_results: maxResults })
  }

  async searchYouTubeDirect(query: string): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/media/youtube/search-direct', { query })
  }

  async playYouTubeVideo(query: string): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/media/youtube/play', { query })
  }

  async playMusic(songName: string, artist?: string): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/media/youtube/music', { song_name: songName, artist })
  }

  async searchTutorials(topic: string, maxResults?: number): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/media/youtube/tutorials', { topic, max_results: maxResults })
  }

  async getVideoInfo(url: string): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/media/youtube/video-info', { url })
  }

  async createPlaylist(videos: YouTubeVideo[], name: string): Promise<ApiResponse<any>> {
    return this.request('POST', '/api/v1/media/youtube/playlist', { videos, name })
  }

  async getTrendingVideos(region?: string, category?: string): Promise<ApiResponse<any>> {
    return this.request('GET', '/api/v1/media/youtube/trending', undefined, { region, category })
  }

  async getMediaServiceStatus(): Promise<ApiResponse<MediaStatus>> {
    return this.request('GET', '/api/v1/media/status')
  }

  async constructUrl(websiteInput: string): Promise<ApiResponse<{ url: string }>> {
    return this.request('POST', '/api/v1/media/url/construct', { website_input: websiteInput })
  }
}

// Create and export singleton instance
export const apiService = new ApiService()
export default apiService