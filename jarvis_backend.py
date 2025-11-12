"""
JARVIS AI - OpenAI API Compatible Version
Install: pip install pyautogui pillow pywin32 youtube-search-python yt-dlp
Run: python jarvis_backend.py
"""

import os
import sys
import webbrowser
import subprocess
import platform
import speech_recognition as sr
import pyttsx3
from urllib.parse import quote
import requests
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading
import time
import re
import pyautogui
from PIL import Image
import base64
from io import BytesIO
from pathlib import Path
import glob

# YouTube search import
from youtubesearchpython import VideosSearch

# Windows-specific imports
if platform.system() == "Windows":
    import win32com.client
    import winreg
    import win32api
    import win32con

app = Flask(__name__)
CORS(app)

class JarvisAI:
    def __init__(self, use_voice=True):
        self.use_voice = use_voice
        self.is_listening = False
        
        if use_voice:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 230)
            self.engine.setProperty('volume', 1.0)
            self.engine.setProperty('pitch', 1.5)
            # Set male voice - specifically David
            voices = self.engine.getProperty('voices')
            male_voice_set = False
            
            # Try to find David voice specifically
            for voice in voices:
                if 'david' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    print(f"✅ Selected voice: {voice.name}")
                    male_voice_set = True
                    break
            
            # Fallback: try any male voice
            if not male_voice_set:
                for voice in voices:
                    if 'male' in voice.name.lower() or (hasattr(voice, 'gender') and voice.gender == 'male'):
                        self.engine.setProperty('voice', voice.id)
                        print(f"✅ Selected voice: {voice.name}")
                        male_voice_set = True
                        break
            
            # Final fallback: use first voice (usually David on Windows)
            if not male_voice_set and voices:
                self.engine.setProperty('voice', voices[0].id)
                print(f"✅ Selected default voice: {voices[0].name}")
            
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
        
        self.os_type = platform.system()
        
        # Enable PyAutoGUI fail-safe
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        self.context = {
            'last_browser_tab': None,
            'last_app': None,
            'conversation_history': [],
            'screen_elements': [],
            'last_search_results': []
        }
        
        # LLM Configuration - OpenAI API Compatible
        self.llm_config = {
            'provider': 'openrouter',  # Can be 'openai', 'openrouter', or 'custom'
            'api_key': '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',  # Replace with your API key
            'api_base': 'https://openrouter.ai/api/v1',  # Or https://openrouter.ai/api/v1
            'model': 'openai/gpt-oss-20b:free',  # Or 'openai/gpt-4o-mini' for OpenRouter
            'vision_model': 'gpt-4o',  # Model with vision capabilities
            'enable_reasoning': True,  # Set to True for reasoning models (OpenRouter)
        }
        
        # Common search locations
        self.search_locations = self.get_search_locations()
        
        # Cache installed apps for faster access
        self.installed_apps_cache = {}
        if self.os_type == "Windows":
            print("🔍 Indexing installed applications...")
            self.installed_apps_cache = self.get_windows_installed_apps()
            print(f"✅ Indexed {len(self.installed_apps_cache)} applications")
        
        print("🤖 Jarvis AI initialized with COMPLETE SYSTEM CONTROL!")
        print("👁️ Vision | ⌨️ Typing | 🔍 File Search | 🖱️ Mouse Control | 🎵 YouTube Direct Play")
    
    def call_openai_api(self, messages, use_vision=False, preserve_reasoning=False):
        """
        Universal OpenAI-compatible API caller
        Supports: OpenAI, OpenRouter, Azure OpenAI, and other compatible APIs
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.llm_config['api_key']}",
                "Content-Type": "application/json",
            }
            
            # Choose appropriate model
            model = self.llm_config['vision_model'] if use_vision else self.llm_config['model']
            
            payload = {
                "model": model,
                "messages": messages,
            }
            
            # Add reasoning support for OpenRouter
            if self.llm_config['enable_reasoning'] and self.llm_config['provider'] == 'openrouter':
                payload["extra_body"] = {"reasoning": {"enabled": True}}
            
            # Make API call
            response = requests.post(
                url=f"{self.llm_config['api_base']}/chat/completions",
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
            print(f"API Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def get_windows_installed_apps(self):
        """Get all installed Windows applications using registry and shell"""
        apps = {}
        
        if self.os_type != "Windows":
            return apps
        
        try:
            # Method 1: Windows Registry - Uninstall keys
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            ]
            
            for hkey, path in registry_paths:
                try:
                    key = winreg.OpenKey(hkey, path)
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)
                            
                            try:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                install_location = None
                                
                                try:
                                    install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                except:
                                    pass
                                
                                try:
                                    display_icon = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                    if display_icon and '.exe' in display_icon.lower():
                                        install_location = os.path.dirname(display_icon.split(',')[0])
                                except:
                                    pass
                                
                                if display_name and display_name not in apps:
                                    apps[display_name.lower()] = {
                                        'name': display_name,
                                        'path': install_location,
                                        'source': 'registry'
                                    }
                            except:
                                pass
                            
                            winreg.CloseKey(subkey)
                        except:
                            continue
                    
                    winreg.CloseKey(key)
                except:
                    continue
            
            # Method 2: Start Menu shortcuts
            start_menu_paths = [
                os.path.join(os.environ.get('PROGRAMDATA', ''), 'Microsoft\\Windows\\Start Menu\\Programs'),
                os.path.join(os.environ.get('APPDATA', ''), 'Microsoft\\Windows\\Start Menu\\Programs'),
            ]
            
            shell = win32com.client.Dispatch("WScript.Shell")
            
            for start_path in start_menu_paths:
                if os.path.exists(start_path):
                    for root, dirs, files in os.walk(start_path):
                        for file in files:
                            if file.endswith('.lnk'):
                                try:
                                    shortcut_path = os.path.join(root, file)
                                    shortcut = shell.CreateShortCut(shortcut_path)
                                    target = shortcut.Targetpath
                                    
                                    if target and os.path.exists(target):
                                        app_name = file.replace('.lnk', '')
                                        if app_name.lower() not in apps:
                                            apps[app_name.lower()] = {
                                                'name': app_name,
                                                'path': target,
                                                'source': 'start_menu'
                                            }
                                except:
                                    continue
            
        except Exception as e:
            print(f"Error indexing apps: {e}")
        
        return apps
    
    def find_app_path(self, app_name):
        """Find application path using cached data"""
        if self.os_type != "Windows":
            return None
        
        app_lower = app_name.lower()
        
        if app_lower in self.installed_apps_cache:
            return self.installed_apps_cache[app_lower]['path']
        
        for key, value in self.installed_apps_cache.items():
            if app_lower in key or key in app_lower:
                return value['path']
        
        for key, value in self.installed_apps_cache.items():
            if app_lower in value['name'].lower() or value['name'].lower() in app_lower:
                return value['path']
        
        return None
    
    def get_search_locations(self):
        """Get common file search locations"""
        locations = []
        if self.os_type == "Windows":
            user_profile = os.environ.get('USERPROFILE', '')
            locations = [
                user_profile,
                os.path.join(user_profile, 'Desktop'),
                os.path.join(user_profile, 'Documents'),
                os.path.join(user_profile, 'Downloads'),
                os.path.join(user_profile, 'Pictures'),
                os.path.join(user_profile, 'Videos'),
                os.path.join(user_profile, 'Music'),
                os.path.join(user_profile, 'OneDrive'),
            ]
        elif self.os_type == "Darwin":
            home = os.path.expanduser('~')
            locations = [
                home,
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Pictures'),
                '/Applications',
            ]
        else:
            home = os.path.expanduser('~')
            locations = [
                home,
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Pictures'),
            ]
        
        return [loc for loc in locations if os.path.exists(loc)]
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"Jarvis: {text}")
        if self.use_voice:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except:
                pass
        return text
    
    def capture_screen(self):
        """Capture current screen"""
        try:
            screenshot = pyautogui.screenshot()
            return screenshot
        except Exception as e:
            print(f"Screen capture error: {e}")
            return None
    
    def image_to_base64(self, image):
        """Convert PIL image to base64"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def scroll_action(self, direction, amount=3):
        """Scroll up or down"""
        try:
            if direction.lower() in ['up', 'top']:
                pyautogui.scroll(amount * 100)
                print(f"✅ Scrolled up")
            elif direction.lower() in ['down', 'bottom']:
                pyautogui.scroll(-amount * 100)
                print(f"✅ Scrolled down")
            return True
        except Exception as e:
            print(f"Scroll error: {e}")
            return False
    
    def type_text(self, text, interval=0.05):
        """Type text on keyboard"""
        try:
            pyautogui.write(text, interval=interval)
            print(f"✅ Typed: {text}")
            return True
        except Exception as e:
            print(f"Typing error: {e}")
            return False
    
    def press_key(self, key):
        """Press a specific key or key combination"""
        try:
            if '+' in key:
                keys = key.split('+')
                pyautogui.hotkey(*keys)
                print(f"✅ Pressed: {key}")
            else:
                pyautogui.press(key)
                print(f"✅ Pressed: {key}")
            return True
        except Exception as e:
            print(f"Key press error: {e}")
            return False
    
    def search_files(self, query, file_type=None, max_results=50):
        """Search for files and folders in user directory"""
        results = []
        search_pattern = f"*{query}*"
        
        print(f"🔍 Searching for: {query} in user directory")
        
        try:
            for location in self.search_locations:
                if not os.path.exists(location):
                    continue
                
                print(f"  Scanning: {location}")
                
                if file_type:
                    pattern = os.path.join(location, '**', f"*{query}*.{file_type}")
                else:
                    pattern = os.path.join(location, '**', f"*{query}*")
                
                try:
                    matches = glob.glob(pattern, recursive=True)
                    for match in matches:
                        if len(results) >= max_results:
                            break
                            
                        try:
                            if os.path.isfile(match):
                                results.append({
                                    'path': match,
                                    'name': os.path.basename(match),
                                    'size': os.path.getsize(match),
                                    'type': 'file',
                                    'parent': os.path.dirname(match)
                                })
                            elif os.path.isdir(match):
                                results.append({
                                    'path': match,
                                    'name': os.path.basename(match),
                                    'type': 'folder',
                                    'parent': os.path.dirname(match)
                                })
                        except Exception as e:
                            continue
                        
                except Exception as e:
                    print(f"  Error scanning {location}: {e}")
                    continue
                
                if len(results) >= max_results:
                    break
            
            results.sort(key=lambda x: (x['type'] != 'folder', x['name'].lower()))
            
            self.context['last_search_results'] = results
            print(f"✅ Found {len(results)} results")
            return results
            
        except Exception as e:
            print(f"File search error: {e}")
            return []
    
    def open_file(self, file_path):
        """Open a file or folder with default application"""
        try:
            if not os.path.exists(file_path):
                print(f"❌ Path does not exist: {file_path}")
                return False
                
            if self.os_type == "Windows":
                os.startfile(file_path)
            elif self.os_type == "Darwin":
                subprocess.run(['open', file_path])
            else:
                subprocess.run(['xdg-open', file_path])
            print(f"✅ Opened: {file_path}")
            return True
        except Exception as e:
            print(f"Open file error: {e}")
            return False
    
    def analyze_screen_with_vision(self, user_query):
        """Use OpenAI Vision API to analyze screen"""
        try:
            screenshot = self.capture_screen()
            if not screenshot:
                return None
            
            # Convert image to base64
            img_base64 = self.image_to_base64(screenshot)
            
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
                                "url": f"data:image/png;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ]
            
            response = self.call_openai_api(messages, use_vision=True)
            
            if response:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
                
                return {"action": "INFORMATION", "response": response}
            
            return None
            
        except Exception as e:
            print(f"Vision analysis error: {e}")
            return None
    
    def click_screen_position(self, x_percent, y_percent):
        """Click at screen position given as percentages"""
        try:
            screen_width, screen_height = pyautogui.size()
            x = int(screen_width * x_percent / 100)
            y = int(screen_height * y_percent / 100)
            
            pyautogui.moveTo(x, y, duration=0.5)
            time.sleep(0.2)
            pyautogui.click()
            print(f"✅ Clicked at ({x}, {y})")
            return True
        except Exception as e:
            print(f"Click error: {e}")
            return False
    
    def get_proper_url(self, website_input):
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
            
            if response:
                url = response.strip()
                url = re.sub(r'```.*?```', '', url, flags=re.DOTALL)
                url = url.strip()
                
                url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
                match = re.search(url_pattern, url)
                if match:
                    url = match.group(0)
                
                if not url.startswith('http://') and not url.startswith('https://'):
                    url = 'https://' + url
                
                url = re.sub(r'https?://(https?://)+', 'https://', url)
                
                print(f"🌐 Constructed URL: {url}")
                return url
            
            if not website_input.startswith('http'):
                return f"https://www.{website_input}.com"
            return website_input
            
        except Exception as e:
            print(f"URL construction error: {e}")
            if not website_input.startswith('http'):
                return f"https://www.{website_input}.com"
            return website_input
    
    def llm_interpret_command(self, user_command):
        """Enhanced LLM interpretation with all system controls using OpenAI API"""
        
        app_names = list(self.installed_apps_cache.keys())[:50] if self.installed_apps_cache else []
        apps_context = ", ".join(app_names) if app_names else "Scanning..."
        
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

System: {self.os_type}
Detected Apps: {apps_context}

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
"open chrome" → {{"action": "OPEN_APP", "target": "chrome", "response": "Opening Chrome"}}
"play despacito" → {{"action": "PLAY_YOUTUBE", "target": "despacito", "response": "Playing despacito"}}
"open youtube" → {{"action": "OPEN_WEBSITE", "target": "youtube", "response": "Opening YouTube"}}
"scroll down" → {{"action": "SCROLL", "target": "down", "params": {{"direction": "down", "amount": 3}}, "response": "Scrolling"}}

Now interpret: {user_command}"""

        try:
            messages = [{"role": "user", "content": system_prompt}]
            response = self.call_openai_api(messages)
            
            if response:
                response_text = response.strip()
                response_text = re.sub(r'```json\s*|\s*```', '', response_text)
                
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
                
                return {
                    "action": "CONVERSATION",
                    "target": "",
                    "reasoning": "Parse error",
                    "executable_hints": [],
                    "folder_paths": [],
                    "params": {},
                    "response": response_text
                }
            
            return None
                
        except Exception as e:
            print(f"LLM Error: {e}")
            return None
    
    def open_folder(self, folder_name, folder_paths):
        """Open folder with enhanced path detection"""
        print(f"📂 Opening folder: {folder_name}")
        
        if self.os_type == "Windows":
            user_profile = os.environ.get('USERPROFILE', '')
            common_folders = {
                'downloads': os.path.join(user_profile, 'Downloads'),
                'documents': os.path.join(user_profile, 'Documents'),
                'desktop': os.path.join(user_profile, 'Desktop'),
                'pictures': os.path.join(user_profile, 'Pictures'),
                'music': os.path.join(user_profile, 'Music'),
                'videos': os.path.join(user_profile, 'Videos'),
            }
            
            folder_lower = folder_name.lower()
            
            if folder_lower in common_folders:
                path = common_folders[folder_lower]
                if os.path.exists(path):
                    os.startfile(path)
                    return True
            
            for path_template in folder_paths:
                path = os.path.expandvars(path_template)
                path = os.path.expanduser(path)
                if os.path.exists(path):
                    os.startfile(path)
                    return True
            
            results = self.search_files(folder_name)
            folders = [r for r in results if r['type'] == 'folder']
            
            if folders:
                os.startfile(folders[0]['path'])
                print(f"✅ Found and opened: {folders[0]['path']}")
                return True
            
            if os.path.exists(folder_name):
                os.startfile(folder_name)
                return True
                
        elif self.os_type == "Darwin":
            for path in folder_paths:
                path = os.path.expanduser(path)
                if os.path.exists(path):
                    subprocess.run(['open', path])
                    return True
                    
        elif self.os_type == "Linux":
            for path in folder_paths:
                path = os.path.expanduser(path)
                if os.path.exists(path):
                    subprocess.run(['xdg-open', path])
                    return True
        
        return False
    
    def smart_find_and_open_app(self, app_name, executable_hints):
        """Enhanced app opening"""
        print(f"🔍 Searching for: {app_name}")
        
        if self.os_type == "Windows":
            app_path = self.find_app_path(app_name)
            if app_path and os.path.exists(app_path):
                try:
                    if os.path.isfile(app_path):
                        os.startfile(app_path)
                    else:
                        for file in os.listdir(app_path):
                            if file.endswith('.exe'):
                                os.startfile(os.path.join(app_path, file))
                                break
                    print(f"✅ Opened from cache: {app_path}")
                    return True
                except Exception as e:
                    print(f"Cache open error: {e}")
            
            for hint in executable_hints:
                try:
                    subprocess.Popen(hint, shell=True)
                    time.sleep(1)
                    print(f"✅ Opened via hint: {hint}")
                    return True
                except:
                    pass
            
            shell = win32com.client.Dispatch("WScript.Shell")
            for hint in [app_name] + executable_hints:
                try:
                    shell.Run(hint)
                    print(f"✅ Opened via shell: {hint}")
                    return True
                except:
                    pass
                    
        elif self.os_type == "Darwin":
            for hint in [app_name] + executable_hints:
                try:
                    subprocess.run(['open', '-a', hint], check=True)
                    return True
                except:
                    continue
                    
        elif self.os_type == "Linux":
            for hint in [app_name] + executable_hints:
                try:
                    subprocess.Popen([hint])
                    return True
                except:
                    continue
        
        print(f"❌ Could not find or open: {app_name}")
        return False
    
    def search_web(self, query):
        """Search the web"""
        search_url = f"https://www.google.com/search?q={quote(query)}"
        webbrowser.open(search_url)
        self.context['last_browser_tab'] = 'search'
    
    def youtube_search(self, query):
        """Search YouTube"""
        search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
        webbrowser.open(search_url)
        self.context['last_browser_tab'] = 'youtube'
    
    def play_youtube_video(self, query):
        """Play YouTube video directly using yt-dlp"""
        print(f"🎵 Searching YouTube with yt-dlp for: {query}")
        try:
            from yt_dlp import YoutubeDL

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'default_search': 'ytsearch1',
            }

            search_query = f"ytsearch1:{query}"
            print("🔎 Using search query:", search_query)

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=False)

            if not info:
                print("❌ No information returned by yt-dlp")
                raise ValueError("No info from yt-dlp")

            entries = None
            if isinstance(info, dict):
                entries = info.get('entries') or [info]

            if not entries:
                print("❌ No entries found in yt-dlp results")
                raise ValueError("No entries in results")

            first = entries[0] if entries else None
            if not first:
                print("❌ First result missing")
                raise ValueError("Missing first result")

            video_id = first.get('id')
            title = first.get('title') or query

            if not video_id:
                print("❌ Could not extract video ID")
                raise ValueError("No video id")

            video_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"✅ Found: {title}")
            print(f"🎬 Opening: {video_url}")

            webbrowser.open(video_url)
            self.context['last_browser_tab'] = 'youtube_video'
            return True

        except Exception as e:
            print(f"YouTube yt-dlp error: {e}")
            print("🔄 Falling back to standard YouTube search...")
            self.youtube_search(query)
            return False
    
    def open_website(self, site_input):
        """Open specific websites with intelligent URL construction"""
        print(f"🌐 Opening website: {site_input}")
        
        url = self.get_proper_url(site_input)
        webbrowser.open(url)
        self.context['last_browser_tab'] = site_input
        
        print(f"✅ Opened: {url}")
        return url
    
    def process_command(self, command):
        """Complete command processing with all features"""
        if not command:
            return {'success': False, 'response': 'No command received'}
        
        command_lower = command.lower()
        
        if any(word in command_lower for word in ['exit', 'quit', 'goodbye']):
            response = self.speak("Goodbye!")
            return {'success': True, 'response': response, 'action': 'exit'}
        
        print("🧠 Analyzing command...")
        interpretation = self.llm_interpret_command(command)
        
        if not interpretation:
            response = self.speak("I couldn't understand that.")
            return {'success': False, 'response': response}
        
        print(f"💭 Reasoning: {interpretation.get('reasoning', 'N/A')}")
        
        action = interpretation.get('action', 'CONVERSATION')
        target = interpretation.get('target', '')
        ai_response = interpretation.get('response', '')
        executable_hints = interpretation.get('executable_hints', [])
        folder_paths = interpretation.get('folder_paths', [])
        params = interpretation.get('params', {})
        
        # Execute action
        if action == "SCROLL":
            direction = params.get('direction', target)
            amount = params.get('amount', 3)
            success = self.scroll_action(direction, amount)
            response = self.speak(ai_response)
            return {'success': success, 'response': response, 'action': 'scroll'}
        
        elif action == "TYPE_TEXT":
            success = self.type_text(target)
            response = self.speak(ai_response)
            return {'success': success, 'response': response, 'action': 'type'}
        
        elif action == "PRESS_KEY":
            key = params.get('key', target)
            success = self.press_key(key)
            response = self.speak(ai_response)
            return {'success': success, 'response': response, 'action': 'keypress'}
        
        elif action == "SEARCH_FILES":
            file_type = params.get('file_type', None)
            results = self.search_files(target, file_type)
            
            if results:
                folders = [r for r in results if r['type'] == 'folder']
                files = [r for r in results if r['type'] == 'file']
                
                result_text = f"Found {len(results)} results:\n"
                if folders:
                    result_text += f"\nFolders ({len(folders)}):\n"
                    for i, res in enumerate(folders[:3], 1):
                        result_text += f"{i}. 📁 {res['name']}\n"
                if files:
                    result_text += f"\nFiles ({len(files)}):\n"
                    for i, res in enumerate(files[:3], 1):
                        result_text += f"{i}. 📄 {res['name']}\n"
                
                response = self.speak(f"Found {len(folders)} folders and {len(files)} files.")
                return {
                    'success': True, 
                    'response': response, 
                    'action': 'search_files',
                    'results': results
                }
            else:
                response = self.speak("No files or folders found.")
                return {'success': False, 'response': response}
        
        elif action == "OPEN_FILE":
            if target.isdigit() and self.context['last_search_results']:
                idx = int(target) - 1
                if 0 <= idx < len(self.context['last_search_results']):
                    file_path = self.context['last_search_results'][idx]['path']
                    success = self.open_file(file_path)
                    response = self.speak(f"Opening {os.path.basename(file_path)}")
                    return {'success': success, 'response': response, 'action': 'open_file'}
            else:
                results = self.search_files(target)
                if results:
                    success = self.open_file(results[0]['path'])
                    response = self.speak(f"Opening {results[0]['name']}")
                    return {'success': success, 'response': response, 'action': 'open_file'}
            
            response = self.speak("File not found.")
            return {'success': False, 'response': response}
        
        elif action == "OPEN_APP":
            success = self.smart_find_and_open_app(target, executable_hints)
            response = self.speak(ai_response if success else f"Couldn't find {target}")
            return {'success': success, 'response': response, 'action': 'open_app'}
        
        elif action == "OPEN_FOLDER":
            success = self.open_folder(target, folder_paths)
            response = self.speak(ai_response if success else f"Couldn't find {target} folder")
            return {'success': success, 'response': response, 'action': 'open_folder'}
        
        elif action == "SCREEN_CLICK":
            self.speak("Analyzing screen...")
            vision_result = self.analyze_screen_with_vision(command)
            
            if vision_result and vision_result.get('action') == 'CLICK':
                pos = vision_result.get('approximate_position', {})
                if pos:
                    success = self.click_screen_position(pos['x'], pos['y'])
                    response = self.speak(vision_result.get('response', 'Clicked'))
                    return {'success': success, 'response': response, 'action': 'click'}
            
            response = self.speak("Couldn't identify click target.")
            return {'success': False, 'response': response}
        
        elif action == "SCREEN_ANALYZE":
            self.speak("Analyzing screen...")
            vision_result = self.analyze_screen_with_vision(command)
            
            if vision_result:
                response = self.speak(vision_result.get('response', 'Screen analyzed'))
                return {'success': True, 'response': response, 'action': 'analyze'}
            
            response = self.speak("Couldn't analyze screen.")
            return {'success': False, 'response': response}
        
        elif action == "SEARCH_WEB":
            self.search_web(target)
            response = self.speak(ai_response)
            return {'success': True, 'response': response, 'action': 'search'}
        
        elif action == "SEARCH_YOUTUBE":
            self.youtube_search(target)
            response = self.speak(ai_response)
            return {'success': True, 'response': response, 'action': 'youtube'}
        
        elif action == "PLAY_YOUTUBE":
            success = self.play_youtube_video(target)
            response = self.speak(ai_response if success else f"Couldn't play {target}")
            return {'success': success, 'response': response, 'action': 'play_youtube'}
        
        elif action == "OPEN_WEBSITE":
            url = self.open_website(target)
            response = self.speak(ai_response)
            return {'success': True, 'response': response, 'action': 'website', 'url': url}
        
        elif action == "CONVERSATION":
            response = self.speak(ai_response)
            return {'success': True, 'response': response, 'action': 'conversation'}
        
        elif action == "SYSTEM_COMMAND":
            try:
                if self.os_type == "Windows":
                    os.system(target)
                else:
                    subprocess.run(target, shell=True)
                response = self.speak(ai_response)
                return {'success': True, 'response': response, 'action': 'system'}
            except Exception as e:
                response = self.speak(f"Error: {str(e)}")
                return {'success': False, 'response': response}
        
        else:
            response = self.speak("I'm not sure how to handle that.")
            return {'success': False, 'response': response}

# Initialize Jarvis
jarvis = JarvisAI(use_voice=False)

# API Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.json
    command = data.get('command', '')
    result = jarvis.process_command(command)
    return jsonify(result)

@app.route('/api/screen', methods=['GET'])
def get_screen():
    """Get current screen"""
    screenshot = jarvis.capture_screen()
    if screenshot:
        img_base64 = jarvis.image_to_base64(screenshot)
        return jsonify({'success': True, 'image': img_base64})
    return jsonify({'success': False})

@app.route('/api/search-files', methods=['POST'])
def search_files_api():
    """Search files endpoint"""
    data = request.json
    query = data.get('query', '')
    file_type = data.get('file_type', None)
    results = jarvis.search_files(query, file_type)
    return jsonify({'success': True, 'results': results})

@app.route('/api/apps', methods=['GET'])
def get_apps():
    """Get list of installed applications"""
    apps = [{'name': v['name'], 'path': v['path']} for v in jarvis.installed_apps_cache.values()]
    return jsonify({'success': True, 'apps': apps, 'count': len(apps)})

@app.route('/api/verify-url', methods=['POST'])
def verify_url():
    """Verify and get proper URL for a website"""
    data = request.json
    site_input = data.get('site', '')
    url = jarvis.get_proper_url(site_input)
    return jsonify({'success': True, 'url': url, 'input': site_input})

@app.route('/api/youtube-search', methods=['POST'])
def youtube_search_api():
    """Search YouTube and return video links"""
    data = request.json
    query = data.get('query', '')
    
    try:
        videos_search = VideosSearch(query, limit=5)
        results = videos_search.result()
        
        videos = []
        if results and 'result' in results:
            for video in results['result']:
                videos.append({
                    'title': video.get('title', ''),
                    'link': video.get('link', ''),
                    'duration': video.get('duration', ''),
                    'views': video.get('viewCount', {}).get('short', ''),
                    'thumbnail': video.get('thumbnails', [{}])[0].get('url', '')
                })
        
        return jsonify({'success': True, 'videos': videos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Get or update API configuration"""
    if request.method == 'POST':
        data = request.json
        if 'api_key' in data:
            jarvis.llm_config['api_key'] = data['api_key']
        if 'api_base' in data:
            jarvis.llm_config['api_base'] = data['api_base']
        if 'model' in data:
            jarvis.llm_config['model'] = data['model']
        if 'vision_model' in data:
            jarvis.llm_config['vision_model'] = data['vision_model']
        if 'provider' in data:
            jarvis.llm_config['provider'] = data['provider']
        if 'enable_reasoning' in data:
            jarvis.llm_config['enable_reasoning'] = data['enable_reasoning']
        return jsonify({'success': True, 'config': jarvis.llm_config})
    else:
        # Return config without exposing full API key
        safe_config = jarvis.llm_config.copy()
        if safe_config['api_key']:
            safe_config['api_key'] = safe_config['api_key'][:8] + '...'
        return jsonify({'success': True, 'config': safe_config})

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'online',
        'context': jarvis.context,
        'llm_provider': jarvis.llm_config['provider'],
        'api_base': jarvis.llm_config['api_base'],
        'model': jarvis.llm_config['model'],
        'indexed_apps': len(jarvis.installed_apps_cache),
        'search_locations': jarvis.search_locations,
        'features': {
            'vision': True,
            'typing': True,
            'file_search': True,
            'folder_search': True,
            'scroll': True,
            'keyboard': True,
            'url_intelligence': True,
            'youtube_direct_play': True,
            'youtube_search_python': True,
            'openai_compatible': True,
            'reasoning_support': jarvis.llm_config['enable_reasoning'],
            'pywin32': jarvis.os_type == "Windows"
        }
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🤖 JARVIS - OpenAI API Compatible Version")
    print("="*70)
    print("\n⚙️ Configuration:")
    print(f"   • Provider: {jarvis.llm_config['provider']}")
    print(f"   • API Base: {jarvis.llm_config['api_base']}")
    print(f"   • Model: {jarvis.llm_config['model']}")
    print(f"   • Vision Model: {jarvis.llm_config['vision_model']}")
    print(f"   • Reasoning: {jarvis.llm_config['enable_reasoning']}")
    print(f"   • API Key: {'✅ Set' if jarvis.llm_config['api_key'] != 'YOUR_API_KEY_HERE' else '❌ Not Set'}")
    print("\n⚠️  IMPORTANT: Update API configuration in llm_config dict")
    print("   - api_key: Your OpenAI/OpenRouter API key")
    print("   - api_base: API endpoint URL")
    print("   - model: Model name for text operations")
    print("   - vision_model: Model name for vision operations")
    print("\n✅ Features Active:")
    print("   • OpenAI API Compatible")
    print("   • Screen Vision & Click")
    print("   • Direct YouTube Video Playback (yt-dlp)")
    print("   • Scroll (up/down)")
    print("   • Type Text")
    print("   • Press Keys")
    print("   • File & Folder Search (User Directory)")
    print("   • App/Folder Opening (Enhanced)")
    print("   • Intelligent URL Construction")
    if jarvis.os_type == "Windows":
        print(f"   • Indexed {len(jarvis.installed_apps_cache)} Windows Apps")
        user_profile = os.environ.get('USERPROFILE', '')
        print(f"   • Search Directory: {user_profile}")
    print("\n💡 Examples:")
    print("   'play despacito' → Plays video directly")
    print("   'open youtube' → Opens YouTube homepage")
    print("   'open gmail' → https://mail.google.com")
    print("   'scroll down'")
    print("   'type hello world'")
    print("   'find my resume'")
    print("   'open chrome'")
    print("\n🌐 Server: http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(debug=True, port=5000, use_reloader=False)