"""
Media Service for JARVIS AI
Handles YouTube operations and web browsing
"""

import webbrowser
from urllib.parse import quote
from typing import Dict, Any, List, Optional
from youtubesearchpython import VideosSearch
from ..core.logging import get_logger
from ..core.exceptions import ApplicationError, SystemError

logger = get_logger(__name__)


class MediaService:
    """Service for media operations and web browsing"""

    def __init__(self):
        logger.info("Media service initialized")

    def search_web(self, query: str) -> bool:
        """Search the web using Google"""
        try:
            search_url = f"https://www.google.com/search?q={quote(query)}"
            webbrowser.open(search_url)
            logger.info(f"Performed web search: {query}")
            return True

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            raise SystemError(f"Web search failed: {str(e)}",
                            operation="search_web", target=query)

    def search_youtube(self, query: str) -> bool:
        """Search YouTube"""
        try:
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
            webbrowser.open(search_url)
            logger.info(f"Searched YouTube: {query}")
            return True

        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            raise SystemError(f"YouTube search failed: {str(e)}",
                            operation="search_youtube", target=query)

    def search_youtube_api(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search YouTube and return video information via API"""
        try:
            logger.info(f"YouTube API search: {query}")
            videos_search = VideosSearch(query, limit=max_results)
            results = videos_search.result()

            videos = []
            if results and 'result' in results:
                for video in results['result']:
                    videos.append({
                        'title': video.get('title', ''),
                        'link': video.get('link', ''),
                        'duration': video.get('duration', ''),
                        'views': video.get('viewCount', {}).get('short', ''),
                        'channel': video.get('channel', {}).get('name', ''),
                        'thumbnail': video.get('thumbnails', [{}])[0].get('url', ''),
                        'description': video.get('description', ''),
                        'published_time': video.get('publishedTime', '')
                    })

            logger.info(f"Found {len(videos)} YouTube videos")
            return {
                'success': True,
                'videos': videos,
                'query': query,
                'total_results': len(videos)
            }

        except Exception as e:
            logger.error(f"YouTube API search failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'videos': []
            }

    def play_youtube_video(self, query: str) -> bool:
        """Play YouTube video directly using yt-dlp"""
        logger.info(f"Playing YouTube video: {query}")

        try:
            from yt_dlp import YoutubeDL

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'default_search': 'ytsearch1',
            }

            search_query = f"ytsearch1:{query}"
            logger.debug(f"Using search query: {search_query}")

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=False)

            if not info:
                logger.error("No information returned by yt-dlp")
                raise ApplicationError("No video information found")

            entries = None
            if isinstance(info, dict):
                entries = info.get('entries') or [info]

            if not entries:
                logger.error("No entries found in yt-dlp results")
                raise ApplicationError("No video entries found")

            first = entries[0] if entries else None
            if not first:
                logger.error("First result missing")
                raise ApplicationError("First video result missing")

            video_id = first.get('id')
            title = first.get('title') or query

            if not video_id:
                logger.error("Could not extract video ID")
                raise ApplicationError("Could not extract video ID")

            video_url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"Found YouTube video: {title}")
            logger.info(f"Opening: {video_url}")

            webbrowser.open(video_url)
            return True

        except ImportError:
            logger.warning("yt-dlp not available, falling back to YouTube search")
            return self.search_youtube(query)

        except Exception as e:
            logger.error(f"YouTube video playback failed: {e}")
            logger.info("Falling back to YouTube search...")
            return self.search_youtube(query)

    def get_video_info(self, video_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a YouTube video"""
        try:
            from yt_dlp import YoutubeDL

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

            if info:
                return {
                    'title': info.get('title', ''),
                    'description': info.get('description', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'uploader': info.get('uploader', ''),
                    'upload_date': info.get('upload_date', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'webpage_url': info.get('webpage_url', ''),
                    'duration_string': info.get('duration_string', ''),
                    'filesize': info.get('filesize', 0)
                }

        except ImportError:
            logger.warning("yt-dlp not available for video info extraction")
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")

        return None

    def create_playlist(self, videos: List[Dict[str, Any]], name: str = "JARVIS Playlist") -> str:
        """Create a playlist from YouTube videos"""
        try:
            if not videos:
                raise ApplicationError("No videos provided for playlist")

            # Generate playlist URL (this is a simplified implementation)
            # In a real implementation, you might use YouTube API
            video_ids = []
            for video in videos:
                if 'link' in video:
                    # Extract video ID from URL
                    if 'watch?v=' in video['link']:
                        video_id = video['link'].split('watch?v=')[1].split('&')[0]
                        video_ids.append(video_id)

            if video_ids:
                playlist_url = f"https://www.youtube.com/watch_videos?video_ids={','.join(video_ids)}"
                logger.info(f"Created playlist with {len(video_ids)} videos: {name}")
                return playlist_url
            else:
                raise ApplicationError("No valid video IDs found for playlist")

        except Exception as e:
            logger.error(f"Failed to create playlist: {e}")
            raise ApplicationError(f"Failed to create playlist: {str(e)}")

    def open_website(self, site_name: str) -> str:
        """Open website with intelligent URL construction"""
        logger.info(f"Opening website: {site_name}")

        try:
            # Import here to avoid circular import
            from .ai_service import ai_service

            # Use AI service to construct proper URL
            url = ai_service.construct_url(site_name)
            webbrowser.open(url)
            logger.info(f"Opened website: {url}")
            return url

        except Exception as e:
            logger.error(f"Failed to open website {site_name}: {e}")
            # Fallback to simple URL construction
            fallback_url = f"https://www.{site_name}.com" if not site_name.startswith('http') else site_name
            try:
                webbrowser.open(fallback_url)
                return fallback_url
            except Exception as e2:
                raise SystemError(f"Failed to open website: {str(e2)}",
                                operation="open_website", target=site_name)

    def browse_url(self, url: str) -> bool:
        """Open specific URL"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            webbrowser.open(url)
            logger.info(f"Opened URL: {url}")
            return True

        except Exception as e:
            logger.error(f"Failed to open URL {url}: {e}")
            raise SystemError(f"Failed to open URL {url}: {str(e)}",
                            operation="browse_url", target=url)

    def get_trending_videos(self, region: str = "US", category: str = "0") -> Dict[str, Any]:
        """Get trending YouTube videos"""
        try:
            # This is a simplified implementation
            # In a real implementation, you would use YouTube API
            search_url = f"https://www.youtube.com/feed/trending?gl={region}"
            webbrowser.open(search_url)
            logger.info(f"Opened trending videos for region {region}")
            return {'success': True, 'url': search_url}

        except Exception as e:
            logger.error(f"Failed to get trending videos: {e}")
            return {'success': False, 'error': str(e)}

    def search_music(self, query: str) -> Dict[str, Any]:
        """Search for music on YouTube"""
        music_query = f"{query} music official"
        return self.search_youtube_api(music_query)

    def search_tutorials(self, query: str) -> Dict[str, Any]:
        """Search for tutorials on YouTube"""
        tutorial_query = f"{query} tutorial"
        return self.search_youtube_api(tutorial_query)

    def play_music_video(self, song_name: str, artist: str = None) -> bool:
        """Play a specific music video"""
        query = song_name
        if artist:
            query = f"{artist} {song_name}"
        return self.play_youtube_video(query)

    def get_media_status(self) -> Dict[str, Any]:
        """Get media service status"""
        try:
            # Check if yt-dlp is available
            ytdlp_available = True
            try:
                import yt_dlp
                ytdlp_version = yt_dlp.__version__
            except ImportError:
                ytdlp_available = False
                ytdlp_version = None

            # Check if youtube-search-python is available
            ytsp_available = True
            try:
                from youtubesearchpython import VideosSearch
                ytsp_version = "1.6.0"  # Approximate version
            except ImportError:
                ytsp_available = False
                ytsp_version = None

            return {
                "yt_dlp_available": ytdlp_available,
                "yt_dlp_version": ytdlp_version,
                "youtube_search_python_available": ytsp_available,
                "youtube_search_python_version": ytsp_version,
                "web_browser_available": True,  # webbrowser is part of stdlib
                "features": {
                    "youtube_search": ytsp_available,
                    "youtube_direct_play": ytdlp_available,
                    "video_info_extraction": ytdlp_available,
                    "web_browsing": True
                }
            }

        except Exception as e:
            logger.error(f"Failed to get media service status: {e}")
            return {"error": str(e)}


# Global media service instance
media_service = MediaService()