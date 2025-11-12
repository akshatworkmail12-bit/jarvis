"""
Vision Service for JARVIS AI
Handles screen capture, analysis, and interaction
"""

import time
import pyautogui
from PIL import Image
from io import BytesIO
import base64
from typing import Optional, Tuple, Dict, Any
from ..core.config import config
from ..core.logging import get_logger
from ..core.exceptions import VisionError
from .ai_service import ai_service

logger = get_logger(__name__)


class VisionService:
    """Service for screen capture and vision analysis"""

    def __init__(self):
        self.system_config = config.system

        # Configure PyAutoGUI
        pyautogui.FAILSAFE = self.system_config.pyautogui_failsafe
        pyautogui.PAUSE = self.system_config.pyautogui_pause

        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        logger.info(f"Vision service initialized (screen: {self.screen_width}x{self.screen_height})")

    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Image.Image]:
        """
        Capture current screen
        region: (left, top, width, height) for partial screen capture
        """
        try:
            logger.debug("Capturing screen...")
            if region:
                screenshot = pyautogui.screenshot(region=region)
                logger.debug(f"Captured region: {region}")
            else:
                screenshot = pyautogui.screenshot()
                logger.debug("Captured full screen")

            return screenshot

        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            raise VisionError(f"Screen capture failed: {str(e)}", operation="capture")

    def capture_screen_to_base64(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[str]:
        """Capture screen and convert to base64 string"""
        try:
            screenshot = self.capture_screen(region)
            if not screenshot:
                return None

            # Convert to base64
            buffered = BytesIO()
            screenshot.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()

            logger.debug("Screen captured and converted to base64")
            return img_base64

        except Exception as e:
            logger.error(f"Screen capture to base64 failed: {e}")
            raise VisionError(f"Screen capture to base64 failed: {str(e)}", operation="capture_base64")

    def analyze_screen(self, user_query: str,
                      region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Dict[str, Any]]:
        """
        Analyze screen content using AI vision
        region: (left, top, width, height) for partial screen analysis
        """
        try:
            logger.info(f"Analyzing screen for: {user_query}")

            # Capture screen
            img_base64 = self.capture_screen_to_base64(region)
            if not img_base64:
                raise VisionError("Failed to capture screen for analysis", operation="analyze")

            # Use AI service to analyze
            result = ai_service.analyze_screen_content(img_base64, user_query)

            if result:
                logger.info(f"Screen analysis completed: {result.get('action', 'UNKNOWN')}")
            else:
                logger.warning("Screen analysis returned no result")

            return result

        except Exception as e:
            logger.error(f"Screen analysis failed: {e}")
            raise VisionError(f"Screen analysis failed: {str(e)}", operation="analyze")

    def click_position(self, x_percent: float, y_percent: float,
                      duration: float = 0.5) -> bool:
        """
        Click at screen position given as percentages
        x_percent, y_percent: 0-100 representing screen position
        """
        try:
            # Convert percentages to absolute coordinates
            x = int(self.screen_width * x_percent / 100)
            y = int(self.screen_height * y_percent / 100)

            # Move to position and click
            pyautogui.moveTo(x, y, duration=duration)
            time.sleep(0.2)  # Brief pause before click
            pyautogui.click()

            logger.info(f"Clicked at screen position ({x}, {y}) - ({x_percent:.1f}%, {y_percent:.1f}%)")
            return True

        except Exception as e:
            logger.error(f"Click failed: {e}")
            raise VisionError(f"Click failed: {str(e)}", operation="click")

    def click_at_coordinates(self, x: int, y: int, duration: float = 0.5) -> bool:
        """Click at absolute screen coordinates"""
        try:
            # Validate coordinates
            if not (0 <= x <= self.screen_width and 0 <= y <= self.screen_height):
                raise VisionError(f"Coordinates out of bounds: ({x}, {y})", operation="click")

            # Move to position and click
            pyautogui.moveTo(x, y, duration=duration)
            time.sleep(0.2)
            pyautogui.click()

            logger.info(f"Clicked at coordinates ({x}, {y})")
            return True

        except Exception as e:
            logger.error(f"Click at coordinates failed: {e}")
            raise VisionError(f"Click at coordinates failed: {str(e)}", operation="click")

    def find_and_click_element(self, element_description: str,
                              confidence_threshold: float = 0.7) -> bool:
        """
        Find element on screen and click it
        element_description: Description of element to find
        confidence_threshold: Minimum confidence for clicking
        """
        try:
            logger.info(f"Finding element: {element_description}")

            # Analyze screen to find element
            result = self.analyze_screen(f"Find and locate: {element_description}")

            if not result:
                logger.warning("Element not found on screen")
                return False

            action = result.get('action')
            confidence = result.get('confidence', 'low')

            # Check if element was found with sufficient confidence
            if action == 'CLICK' and self._convert_confidence(confidence) >= confidence_threshold:
                position = result.get('approximate_position')
                if position and 'x' in position and 'y' in position:
                    success = self.click_position(position['x'], position['y'])
                    if success:
                        logger.info(f"Successfully clicked {element_description}")
                    return success

            logger.warning(f"Element found but confidence too low: {confidence}")
            return False

        except Exception as e:
            logger.error(f"Find and click element failed: {e}")
            raise VisionError(f"Find and click element failed: {str(e)}", operation="find_and_click")

    def scroll_screen(self, direction: str = 'down', amount: int = 3,
                     x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """
        Scroll screen in specified direction
        direction: 'up', 'down', 'left', 'right'
        amount: Number of scroll units
        x, y: Position to scroll at (defaults to center)
        """
        try:
            direction = direction.lower()
            scroll_amount = amount * 100  # Convert to scroll units

            if direction in ['up', 'down']:
                scroll_amount = -scroll_amount if direction == 'up' else scroll_amount
                if x is not None and y is not None:
                    pyautogui.scroll(scroll_amount, x=x, y=y)
                else:
                    pyautogui.scroll(scroll_amount)
            elif direction in ['left', 'right']:
                scroll_amount = -scroll_amount if direction == 'left' else scroll_amount
                if x is not None and y is not None:
                    pyautogui.hscroll(scroll_amount, x=x, y=y)
                else:
                    pyautogui.hscroll(scroll_amount)
            else:
                raise VisionError(f"Invalid scroll direction: {direction}", operation="scroll")

            logger.info(f"Scrolled {direction} by {amount} units")
            return True

        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            raise VisionError(f"Scroll failed: {str(e)}", operation="scroll")

    def get_screen_info(self) -> Dict[str, Any]:
        """Get current screen information"""
        try:
            return {
                "width": self.screen_width,
                "height": self.screen_height,
                "resolution": f"{self.screen_width}x{self.screen_height}",
                "failsafe_enabled": pyautogui.FAILSAFE,
                "pause_duration": pyautogui.PAUSE,
                "primary_monitor": True  # Simplified for now
            }
        except Exception as e:
            logger.error(f"Failed to get screen info: {e}")
            return {"error": str(e)}

    def get_color_at_position(self, x: int, y: int) -> Optional[Tuple[int, int, int]]:
        """Get RGB color at specific screen position"""
        try:
            if not (0 <= x <= self.screen_width and 0 <= y <= self.screen_height):
                raise VisionError(f"Coordinates out of bounds: ({x}, {y})", operation="get_color")

            screenshot = self.capture_screen()
            if not screenshot:
                return None

            pixel_color = screenshot.getpixel((x, y))
            if isinstance(pixel_color, tuple) and len(pixel_color) >= 3:
                return pixel_color[:3]  # Return RGB only
            else:
                return pixel_color

        except Exception as e:
            logger.error(f"Failed to get color at position: {e}")
            return None

    def save_screen_capture(self, filename: str,
                           region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """Save screen capture to file"""
        try:
            screenshot = self.capture_screen(region)
            if not screenshot:
                return False

            screenshot.save(filename)
            logger.info(f"Screen capture saved to: {filename}")
            return True

        except Exception as e:
            logger.error(f"Failed to save screen capture: {e}")
            return False

    def _convert_confidence(self, confidence: str) -> float:
        """Convert confidence string to numeric value"""
        confidence_map = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        return confidence_map.get(confidence.lower(), 0.5)

    def test_vision_capabilities(self) -> Dict[str, Any]:
        """Test vision service capabilities"""
        test_results = {
            "screen_capture": False,
            "ai_analysis": False,
            "clicking": False,
            "scrolling": False,
            "errors": []
        }

        try:
            # Test screen capture
            screenshot = self.capture_screen()
            if screenshot:
                test_results["screen_capture"] = True
                screenshot_size = len(screenshot.tobytes())
                test_results["screenshot_size"] = screenshot_size
            else:
                test_results["errors"].append("Screen capture failed")

            # Test AI analysis
            try:
                result = self.analyze_screen("What do you see on this screen?")
                if result:
                    test_results["ai_analysis"] = True
                    test_results["analysis_result"] = result.get("action", "unknown")
                else:
                    test_results["errors"].append("AI analysis returned no result")
            except Exception as e:
                test_results["errors"].append(f"AI analysis failed: {str(e)}")

            # Test clicking (safe position - center of screen)
            try:
                center_x, center_y = self.screen_width // 2, self.screen_height // 2
                # We'll simulate a click without actually clicking to avoid issues
                pyautogui.moveTo(center_x, center_y, duration=0.1)
                test_results["clicking"] = True
                test_results["click_test"] = "Mouse moved to center position"
            except Exception as e:
                test_results["errors"].append(f"Click test failed: {str(e)}")

            # Test scrolling
            try:
                original_position = pyautogui.position()
                pyautogui.scroll(1)  # Small scroll
                pyautogui.scroll(-1)  # Scroll back
                test_results["scrolling"] = True
                test_results["scroll_test"] = "Scroll functionality tested"
            except Exception as e:
                test_results["errors"].append(f"Scroll test failed: {str(e)}")

        except Exception as e:
            test_results["errors"].append(f"Vision test failed: {str(e)}")

        test_results["success"] = (
            test_results["screen_capture"] and
            len(test_results["errors"]) == 0
        )

        return test_results


# Global vision service instance
vision_service = VisionService()