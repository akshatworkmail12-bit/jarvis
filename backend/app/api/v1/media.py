"""
Media API endpoints for JARVIS AI
Handles YouTube operations, web browsing, and media management
"""

from flask import Blueprint, request, jsonify
from ...services.media_service import media_service
from ...services.ai_service import ai_service
from ...core.logging import get_logger
from ...core.exceptions import ValidationError, SystemError
from ...core.security import input_validator
from ..middleware import rate_limit, validate_json_input

logger = get_logger(__name__)

# Create blueprint
media_bp = Blueprint('media', __name__, url_prefix='/api/v1/media')


@media_bp.route('/web/search', methods=['POST'])
@rate_limit()
@validate_json_input(['query'])
def search_web():
    """Search the web"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            raise ValidationError("Search query is required", field="query")

        success = media_service.search_web(query)

        return jsonify({
            'success': success,
            'data': {
                'query': query,
                'searched': success,
                'search_url': f"https://www.google.com/search?q={query}"
            }
        })
    except Exception as e:
        logger.error(f"Web search failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'WEB_SEARCH_ERROR',
                'message': 'Failed to search web'
            }
        }), 500


@media_bp.route('/website/open', methods=['POST'])
@rate_limit()
@validate_json_input(['site'])
def open_website():
    """Open website with intelligent URL construction"""
    try:
        data = request.get_json()
        site = data.get('site', '').strip()

        if not site:
            raise ValidationError("Website name is required", field="site")

        url = media_service.open_website(site)

        return jsonify({
            'success': True,
            'data': {
                'site': site,
                'url': url,
                'opened': True
            }
        })
    except Exception as e:
        logger.error(f"Failed to open website: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'WEBSITE_OPEN_ERROR',
                'message': 'Failed to open website'
            }
        }), 500


@media_bp.route('/browse', methods=['POST'])
@rate_limit()
@validate_json_input(['url'])
def browse_url():
    """Open specific URL"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()

        if not url:
            raise ValidationError("URL is required", field="url")

        # Validate URL format
        validated_url = input_validator.validate_url(url)

        success = media_service.browse_url(validated_url)

        return jsonify({
            'success': success,
            'data': {
                'url': validated_url,
                'browsed': success
            }
        })
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 400
    except Exception as e:
        logger.error(f"Failed to browse URL: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'BROWSE_URL_ERROR',
                'message': 'Failed to browse URL'
            }
        }), 500


@media_bp.route('/youtube/search', methods=['POST'])
@rate_limit()
@validate_json_input(['query'])
def search_youtube():
    """Search YouTube via API and return results"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        max_results = int(data.get('max_results', 5))

        if not query:
            raise ValidationError("Search query is required", field="query")

        if max_results < 1 or max_results > 50:
            raise ValidationError("max_results must be between 1 and 50")

        result = media_service.search_youtube_api(query, max_results)

        return jsonify({
            'success': result['success'],
            'data': result
        })
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 400
    except Exception as e:
        logger.error(f"YouTube search failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'YOUTUBE_SEARCH_ERROR',
                'message': 'Failed to search YouTube'
            }
        }), 500


@media_bp.route('/youtube/search-direct', methods=['POST'])
@rate_limit()
@validate_json_input(['query'])
def search_youtube_direct():
    """Search YouTube directly in browser"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            raise ValidationError("Search query is required", field="query")

        success = media_service.search_youtube(query)

        return jsonify({
            'success': success,
            'data': {
                'query': query,
                'searched': success,
                'search_url': f"https://www.youtube.com/results?search_query={query}"
            }
        })
    except Exception as e:
        logger.error(f"YouTube direct search failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'YOUTUBE_SEARCH_DIRECT_ERROR',
                'message': 'Failed to search YouTube directly'
            }
        }), 500


@media_bp.route('/youtube/play', methods=['POST'])
@rate_limit()
@validate_json_input(['query'])
def play_youtube_video():
    """Play YouTube video directly"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            raise ValidationError("Video query is required", field="query")

        success = media_service.play_youtube_video(query)

        return jsonify({
            'success': success,
            'data': {
                'query': query,
                'played': success
            }
        })
    except Exception as e:
        logger.error(f"YouTube video play failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'YOUTUBE_PLAY_ERROR',
                'message': 'Failed to play YouTube video'
            }
        }), 500


@media_bp.route('/youtube/music', methods=['POST'])
@rate_limit()
@validate_json_input(['song_name'])
def play_music():
    """Play music video"""
    try:
        data = request.get_json()
        song_name = data.get('song_name', '').strip()
        artist = data.get('artist', '').strip()

        if not song_name:
            raise ValidationError("Song name is required", field="song_name")

        success = media_service.play_music_video(song_name, artist)

        return jsonify({
            'success': success,
            'data': {
                'song_name': song_name,
                'artist': artist,
                'played': success
            }
        })
    except Exception as e:
        logger.error(f"Music play failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'MUSIC_PLAY_ERROR',
                'message': 'Failed to play music'
            }
        }), 500


@media_bp.route('/youtube/tutorials', methods=['POST'])
@rate_limit()
@validate_json_input(['topic'])
def search_tutorials():
    """Search for tutorials"""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        max_results = int(data.get('max_results', 10))

        if not topic:
            raise ValidationError("Topic is required", field="topic")

        result = media_service.search_tutorials(topic)
        if 'max_results' in data:
            result['videos'] = result['videos'][:max_results]

        return jsonify({
            'success': result['success'],
            'data': result
        })
    except Exception as e:
        logger.error(f"Tutorial search failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'TUTORIAL_SEARCH_ERROR',
                'message': 'Failed to search tutorials'
            }
        }), 500


@media_bp.route('/youtube/video-info', methods=['POST'])
@rate_limit()
@validate_json_input(['url'])
def get_video_info():
    """Get detailed information about a YouTube video"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()

        if not url:
            raise ValidationError("Video URL is required", field="url")

        video_info = media_service.get_video_info(url)

        return jsonify({
            'success': video_info is not None,
            'data': {
                'url': url,
                'info': video_info
            }
        })
    except Exception as e:
        logger.error(f"Video info retrieval failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'VIDEO_INFO_ERROR',
                'message': 'Failed to get video information'
            }
        }), 500


@media_bp.route('/youtube/playlist', methods=['POST'])
@rate_limit()
@validate_json_input(['videos', 'name'])
def create_playlist():
    """Create a YouTube playlist from videos"""
    try:
        data = request.get_json()
        videos = data.get('videos', [])
        name = data.get('name', 'JARVIS Playlist').strip()

        if not videos:
            raise ValidationError("Videos list is required", field="videos")

        if not name:
            raise ValidationError("Playlist name is required", field="name")

        playlist_url = media_service.create_playlist(videos, name)

        return jsonify({
            'success': bool(playlist_url),
            'data': {
                'name': name,
                'videos': videos,
                'video_count': len(videos),
                'playlist_url': playlist_url
            }
        })
    except Exception as e:
        logger.error(f"Playlist creation failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'PLAYLIST_CREATE_ERROR',
                'message': 'Failed to create playlist'
            }
        }), 500


@media_bp.route('/youtube/trending', methods=['GET'])
@rate_limit()
def get_trending_videos():
    """Get trending YouTube videos"""
    try:
        region = request.args.get('region', 'US')
        category = request.args.get('category', '0')

        result = media_service.get_trending_videos(region, category)

        return jsonify({
            'success': result['success'],
            'data': result
        })
    except Exception as e:
        logger.error(f"Trending videos failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'TRENDING_VIDEOS_ERROR',
                'message': 'Failed to get trending videos'
            }
        }), 500


@media_bp.route('/status', methods=['GET'])
@rate_limit()
def get_media_service_status():
    """Get media service status and capabilities"""
    try:
        status = media_service.get_media_status()

        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logger.error(f"Failed to get media service status: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'MEDIA_SERVICE_STATUS_ERROR',
                'message': 'Failed to get media service status'
            }
        }), 500


@media_bp.route('/url/construct', methods=['POST'])
@rate_limit()
@validate_json_input(['website_input'])
def construct_url():
    """Use AI to construct proper URL"""
    try:
        data = request.get_json()
        website_input = data.get('website_input', '').strip()

        if not website_input:
            raise ValidationError("Website input is required", field="website_input")

        url = ai_service.construct_url(website_input)

        return jsonify({
            'success': True,
            'data': {
                'input': website_input,
                'url': url
            }
        })
    except Exception as e:
        logger.error(f"URL construction failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'URL_CONSTRUCT_ERROR',
                'message': 'Failed to construct URL'
            }
        }), 500