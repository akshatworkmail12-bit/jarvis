"""
AI Service for JARVIS AI
Handles all LLM interactions and command interpretation
"""

import re
import requests
import json
from typing import Dict, Any, Optional, List
from ..core.config import config
from ..core.logging import get_logger
from ..core.exceptions import LLMError, ValidationError

logger = get_logger(__name__)


class AIService:
    """Service for AI/LLM operations"""

    def __init__(self):
        self.llm_config = config.llm
        logger.info(f"AI Service initialized with provider: {self.llm_config.provider}")

    def call_openai_api(self, messages: List[Dict[str, Any]],
                       use_vision: bool = False,
                       preserve_reasoning: bool = False) -> Any:
        """
        Universal OpenAI-compatible API caller
        Supports: OpenAI, OpenRouter, Azure OpenAI, and other compatible APIs
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.llm_config.api_key}",
                "Content-Type": "application/json",
            }

            # Choose appropriate model
            model = self.llm_config.vision_model if use_vision else self.llm_config.model

            payload = {
                "model": model,
                "messages": messages,
            }

            # Add reasoning support for OpenRouter
            if self.llm_config.enable_reasoning and self.llm_config.provider == "openrouter":
                payload["extra_body"] = {"reasoning": {"enabled": True}}

            # Make API call
            response = requests.post(
                url=f"{self.llm_config.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            # Extract response
            message = result['choices'][0]['message']
            content = message.get('content', '')

            # Preserve reasoning details if enabled
            if preserve_reasoning and 'reasoning_details' in message:
                return {
                    'content': content,
                    'reasoning_details': message['reasoning_details']
                }

            return content

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise LLMError(f"API request failed: {str(e)}",
                          provider=self.llm_config.provider,
                          model=model)
        except Exception as e:
            logger.error(f"Unexpected error in AI API call: {e}")
            raise LLMError(f"Unexpected error: {str(e)}",
                          provider=self.llm_config.provider)

    def interpret_command(self, user_command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced LLM interpretation with all system controls"""

        # Validate input
        if not user_command:
            raise ValidationError("Command cannot be empty", field="command")

        logger.info(f"Interpreting command: {user_command[:100]}...")

        # Prepare context
        if context is None:
            context = {}

        apps_context = context.get('detected_apps', [])
        apps_text = ", ".join(apps_context[:50]) if apps_context else "Scanning..."

        system_prompt = f"""You are Jarvis with COMPLETE system control capabilities.

CRITICAL: Respond with VALID JSON only. No markdown, no extra text.

Available Actions:
1. OPEN_APP - Open application
2. OPEN_FOLDER - Open folder
3. SEARCH_WEB - Google search
4. SEARCH_YOUTUBE - YouTube search (search only)
5. PLAY_YOUTUBE - Play YouTube video directly
6. OPEN_WEBSITE - Open website (for specific sites)
7. SCREEN_CLICK - Click on screen
8. SCREEN_ANALYZE - Analyze screen
9. TYPE_TEXT - Type text
10. PRESS_KEY - Press key/combination
11. SCROLL - Scroll up/down
12. SEARCH_FILES - Search files/folders
13. OPEN_FILE - Open specific file/folder
14. CONVERSATION - General chat
15. SYSTEM_COMMAND - Execute command

System: {config.system.os_type}
Detected Apps: {apps_text}

JSON Format:
{{
    "action": "ACTION_TYPE",
    "target": "target/query",
    "reasoning": "why this action",
    "executable_hints": ["possible", "executables"],
    "folder_paths": ["possible/paths"],
    "params": {{"direction": "up/down", "amount": 3, "key": "enter"}},
    "response": "user message"
}}

CRITICAL YOUTUBE RULES:
1. PLAY_YOUTUBE = When user wants to PLAY/WATCH/LISTEN
   - Keywords: "play", "watch", "listen", "put on"
   - Examples: "play despacito", "watch tutorial", "listen to music"
2. SEARCH_YOUTUBE = ONLY when user explicitly says "search"
3. OPEN_WEBSITE = When opening YouTube homepage: target should be "youtube"

Examples:
"open chrome" -> {{"action": "OPEN_APP", "target": "chrome", "response": "Opening Chrome"}}
"play despacito" -> {{"action": "PLAY_YOUTUBE", "target": "despacito", "response": "Playing despacito"}}
"open youtube" -> {{"action": "OPEN_WEBSITE", "target": "youtube", "response": "Opening YouTube"}}
"scroll down" -> {{"action": "SCROLL", "target": "down", "params": {{"direction": "down", "amount": 3}}, "response": "Scrolling"}}

Now interpret: {user_command}"""

        try:
            messages = [{"role": "user", "content": system_prompt}]
            response = self.call_openai_api(messages)

            if not response:
                raise LLMError("Empty response from AI service")

            response_text = str(response).strip()
            response_text = re.sub(r'```json\s*|\s*```', '', response_text)

            # Try to parse JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                    logger.info(f"Command interpreted successfully: {parsed.get('action', 'UNKNOWN')}")
                    return parsed
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON from AI response: {json_match.group(0)}")

            # Fallback to conversation action
            return {
                "action": "CONVERSATION",
                "target": "",
                "reasoning": "Parse error - treating as conversation",
                "executable_hints": [],
                "folder_paths": [],
                "params": {},
                "response": response_text
            }

        except LLMError:
            raise
        except Exception as e:
            logger.error(f"Command interpretation failed: {e}")
            raise LLMError(f"Command interpretation failed: {str(e)}")

    def construct_url(self, website_input: str) -> str:
        """Use LLM to intelligently construct proper URL"""
        try:
            prompt = f"""Given the website input: "{website_input}"

Return ONLY a valid, complete URL with proper format.

Rules:
1. Return ONLY the URL, nothing else
2. Must start with https://
3. Use correct domain extension (.com, .org, .net, .io, etc.)
4. For popular sites, use the exact correct URL
5. No www duplication
6. Clean, single URL only

Examples:
Input: "youtube" → Output: https://www.youtube.com
Input: "gmail" → Output: https://mail.google.com
Input: "github" → Output: https://github.com
Input: "reddit" → Output: https://www.reddit.com

Now process: "{website_input}"

Return ONLY the URL:"""

            messages = [{"role": "user", "content": prompt}]
            response = self.call_openai_api(messages)

            if not response:
                raise LLMError("Empty response from AI service")

            url = str(response).strip()
            url = re.sub(r'```.*?```', '', url, flags=re.DOTALL)
            url = url.strip()

            # Extract URL using regex
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
            match = re.search(url_pattern, url)
            if match:
                url = match.group(0)

            # Ensure it starts with http
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'https://' + url

            # Fix duplicate http prefixes
            url = re.sub(r'https?://(https?://)+', 'https://', url)

            logger.info(f"Constructed URL: {url}")
            return url

        except LLMError:
            raise
        except Exception as e:
            logger.error(f"URL construction failed: {e}")
            # Fallback to simple construction
            if not website_input.startswith('http'):
                return f"https://www.{website_input}.com"
            return website_input

    def analyze_screen_content(self, screenshot_base64: str, user_query: str) -> Optional[Dict[str, Any]]:
        """Use OpenAI Vision API to analyze screen content"""
        try:
            prompt = f"""Analyze this screenshot and help with: "{user_query}"

Respond with JSON ONLY:
{{
    "action": "CLICK" | "INFORMATION" | "NOT_FOUND",
    "target_description": "what to interact with",
    "approximate_position": {{"x": percent_x, "y": percent_y}},
    "confidence": "high" | "medium" | "low",
    "reasoning": "what you found",
    "response": "user message"
}}

For clicks: provide x,y as percentages (0-100) of screen size.
For information: describe what you see."""

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{screenshot_base64}"
                            }
                        }
                    ]
                }
            ]

            response = self.call_openai_api(messages, use_vision=True)

            if not response:
                logger.warning("Empty response from vision analysis")
                return None

            # Try to extract JSON from response
            response_text = str(response).strip()
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                    logger.info(f"Screen analysis completed: {parsed.get('action', 'UNKNOWN')}")
                    return parsed
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON from vision response: {json_match.group(0)}")

            # Fallback to information action
            return {
                "action": "INFORMATION",
                "target_description": "general screen content",
                "approximate_position": {"x": 50, "y": 50},
                "confidence": "medium",
                "reasoning": "Could not parse structured response",
                "response": response_text
            }

        except LLMError:
            raise
        except Exception as e:
            logger.error(f"Screen analysis failed: {e}")
            raise LLMError(f"Screen analysis failed: {str(e)}")

    def generate_conversation_response(self, message: str, context: Dict[str, Any] = None) -> str:
        """Generate conversational response"""
        try:
            # Build context-aware prompt
            context_prompt = ""
            if context:
                if context.get('last_actions'):
                    context_prompt += f"Recent actions: {', '.join(context['last_actions'][-3:])}\n"
                if context.get('system_status'):
                    context_prompt += f"System status: {context['system_status']}\n"

            prompt = f"""{context_prompt}
User message: "{message}"

Respond naturally as a helpful AI assistant. Be concise but friendly. No need for JSON formatting."""

            messages = [{"role": "user", "content": prompt}]
            response = self.call_openai_api(messages)

            if not response:
                raise LLMError("Empty response from AI service")

            logger.info("Generated conversational response")
            return str(response).strip()

        except LLMError:
            raise
        except Exception as e:
            logger.error(f"Conversation response generation failed: {e}")
            raise LLMError(f"Conversation response failed: {str(e)}")

    def validate_api_configuration(self) -> Dict[str, Any]:
        """Validate the AI service configuration"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "config_info": {
                "provider": self.llm_config.provider,
                "api_base": self.llm_config.api_base,
                "model": self.llm_config.model,
                "vision_model": self.llm_config.vision_model,
                "reasoning_enabled": self.llm_config.enable_reasoning,
                "api_key_configured": bool(self.llm_config.api_key and len(self.llm_config.api_key) > 10)
            }
        }

        # Check API key format
        if not self.llm_config.api_key or len(self.llm_config.api_key) < 10:
            validation_result["errors"].append("API key is not configured or too short")
            validation_result["valid"] = False

        # Test API connectivity (simple validation)
        try:
            test_messages = [{"role": "user", "content": "test"}]
            response = self.call_openai_api(test_messages)
            if not response:
                validation_result["errors"].append("API returned empty response")
                validation_result["valid"] = False
        except Exception as e:
            validation_result["errors"].append(f"API connectivity test failed: {str(e)}")
            validation_result["valid"] = False

        return validation_result


# Global AI service instance
ai_service = AIService()