"""
System Service for JARVIS AI
Handles system automation, application management, and file operations
"""

import os
import sys
import subprocess
import platform
import time
import webbrowser
import pyautogui
from pathlib import Path
import glob
from typing import Dict, Any, List, Optional
from urllib.parse import quote

# Windows-specific imports
if platform.system() == "Windows":
    import win32com.client
    import winreg
    import win32api
    import win32con

from ..core.config import config
from ..core.logging import get_logger
from ..core.exceptions import SystemError, ApplicationError, FileNotFoundError

logger = get_logger(__name__)


class SystemService:
    """Service for system operations and automation"""

    def __init__(self):
        self.system_config = config.system
        self.os_type = platform.system()
        self.search_locations = config.search_locations
        self.installed_apps_cache = {}
        self._load_installed_apps()
        logger.info(f"System service initialized for {self.os_type}")

    def _load_installed_apps(self):
        """Load installed applications cache"""
        if self.os_type == "Windows":
            logger.info("Indexing Windows installed applications...")
            self.installed_apps_cache = self._get_windows_installed_apps()
            logger.info(f"Indexed {len(self.installed_apps_cache)} applications")

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            info = {
                "os": self.os_type,
                "platform": platform.platform(),
                "architecture": platform.architecture(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "search_locations": self.search_locations,
                "installed_apps_count": len(self.installed_apps_cache),
                "screen_size": pyautogui.size()
            }

            if self.os_type == "Windows":
                info.update({
                    "windows_version": platform.win32_ver()[0],
                    "computer_name": os.environ.get('COMPUTERNAME', 'Unknown'),
                    "user_name": os.environ.get('USERNAME', 'Unknown'),
                })

            return info

        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {"error": str(e)}

    def find_app_path(self, app_name: str) -> Optional[str]:
        """Find application path using cached data"""
        if not app_name or self.os_type != "Windows":
            return None

        app_lower = app_name.lower()

        # Direct match
        if app_lower in self.installed_apps_cache:
            return self.installed_apps_cache[app_lower]['path']

        # Partial match
        for key, value in self.installed_apps_cache.items():
            if app_lower in key or key in app_lower:
                return value['path']

        # Name match
        for key, value in self.installed_apps_cache.items():
            if app_lower in value['name'].lower() or value['name'].lower() in app_lower:
                return value['path']

        return None

    def open_application(self, app_name: str, executable_hints: List[str] = None) -> bool:
        """Open application by name"""
        logger.info(f"Opening application: {app_name}")

        if not executable_hints:
            executable_hints = []

        try:
            if self.os_type == "Windows":
                return self._open_windows_app(app_name, executable_hints)
            elif self.os_type == "Darwin":
                return self._open_macos_app(app_name, executable_hints)
            else:
                return self._open_linux_app(app_name, executable_hints)

        except Exception as e:
            logger.error(f"Failed to open application {app_name}: {e}")
            raise ApplicationError(f"Failed to open application {app_name}: {str(e)}",
                                 app_name=app_name)

    def _open_windows_app(self, app_name: str, executable_hints: List[str]) -> bool:
        """Open Windows application"""
        # Try to find app in cache
        app_path = self.find_app_path(app_name)
        if app_path and os.path.exists(app_path):
            try:
                if os.path.isfile(app_path):
                    os.startfile(app_path)
                else:
                    # Find executable in directory
                    for file in os.listdir(app_path):
                        if file.endswith('.exe'):
                            os.startfile(os.path.join(app_path, file))
                            break
                logger.info(f"Opened {app_name} from cache: {app_path}")
                return True
            except Exception as e:
                logger.warning(f"Failed to open from cache: {e}")

        # Try executable hints
        for hint in executable_hints:
            try:
                subprocess.Popen(hint, shell=True)
                time.sleep(1)  # Give it time to start
                logger.info(f"Opened {app_name} via hint: {hint}")
                return True
            except:
                continue

        # Try shell run
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            for hint in [app_name] + executable_hints:
                try:
                    shell.Run(hint)
                    logger.info(f"Opened {app_name} via shell: {hint}")
                    return True
                except:
                    continue
        except Exception as e:
            logger.warning(f"Shell run failed: {e}")

        logger.error(f"Could not find or open application: {app_name}")
        return False

    def _open_macos_app(self, app_name: str, executable_hints: List[str]) -> bool:
        """Open macOS application"""
        for hint in [app_name] + executable_hints:
            try:
                subprocess.run(['open', '-a', hint], check=True)
                logger.info(f"Opened macOS application: {hint}")
                return True
            except:
                continue
        return False

    def _open_linux_app(self, app_name: str, executable_hints: List[str]) -> bool:
        """Open Linux application"""
        for hint in [app_name] + executable_hints:
            try:
                subprocess.Popen([hint])
                logger.info(f"Opened Linux application: {hint}")
                return True
            except:
                continue
        return False

    def open_folder(self, folder_name: str, folder_paths: List[str] = None) -> bool:
        """Open folder with enhanced path detection"""
        logger.info(f"Opening folder: {folder_name}")

        if not folder_paths:
            folder_paths = []

        try:
            if self.os_type == "Windows":
                return self._open_windows_folder(folder_name, folder_paths)
            elif self.os_type == "Darwin":
                return self._open_macos_folder(folder_name, folder_paths)
            else:
                return self._open_linux_folder(folder_name, folder_paths)

        except Exception as e:
            logger.error(f"Failed to open folder {folder_name}: {e}")
            raise SystemError(f"Failed to open folder {folder_name}: {str(e)}",
                            operation="open_folder", target=folder_name)

    def _open_windows_folder(self, folder_name: str, folder_paths: List[str]) -> bool:
        """Open Windows folder"""
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

        # Try common folders
        if folder_lower in common_folders:
            path = common_folders[folder_lower]
            if os.path.exists(path):
                os.startfile(path)
                logger.info(f"Opened common folder: {path}")
                return True

        # Try provided folder paths
        for path_template in folder_paths:
            path = os.path.expandvars(path_template)
            path = os.path.expanduser(path)
            if os.path.exists(path):
                os.startfile(path)
                logger.info(f"Opened folder from paths: {path}")
                return True

        # Search for folder
        search_results = self.search_files(folder_name, max_results=10)
        folders = [r for r in search_results if r['type'] == 'folder']

        if folders:
            os.startfile(folders[0]['path'])
            logger.info(f"Found and opened: {folders[0]['path']}")
            return True

        # Try direct path
        if os.path.exists(folder_name):
            os.startfile(folder_name)
            logger.info(f"Opened direct folder path: {folder_name}")
            return True

        return False

    def _open_macos_folder(self, folder_name: str, folder_paths: List[str]) -> bool:
        """Open macOS folder"""
        for path in folder_paths:
            path = os.path.expanduser(path)
            if os.path.exists(path):
                subprocess.run(['open', path])
                return True
        return False

    def _open_linux_folder(self, folder_name: str, folder_paths: List[str]) -> bool:
        """Open Linux folder"""
        for path in folder_paths:
            path = os.path.expanduser(path)
            if os.path.exists(path):
                subprocess.run(['xdg-open', path])
                return True
        return False

    def search_files(self, query: str, file_type: str = None,
                    max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for files and folders in user directory"""
        results = []
        search_pattern = f"*{query}*"

        logger.info(f"Searching for files: {query}")

        try:
            for location in self.search_locations:
                if not os.path.exists(location):
                    continue

                logger.debug(f"Scanning location: {location}")

                # Build search pattern
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
                            result = self._create_file_result(match)
                            if result:
                                results.append(result)
                        except Exception as e:
                            logger.debug(f"Error processing file {match}: {e}")
                            continue

                except Exception as e:
                    logger.debug(f"Error scanning {location}: {e}")
                    continue

                if len(results) >= max_results:
                    break

            # Sort results (folders first, then alphabetically)
            results.sort(key=lambda x: (x['type'] != 'folder', x['name'].lower()))

            logger.info(f"Found {len(results)} search results")
            return results

        except Exception as e:
            logger.error(f"File search failed: {e}")
            raise SystemError(f"File search failed: {str(e)}",
                            operation="search_files", target=query)

    def _create_file_result(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Create file/folder result dictionary"""
        try:
            if os.path.isfile(file_path):
                return {
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'size': os.path.getsize(file_path),
                    'type': 'file',
                    'parent': os.path.dirname(file_path),
                    'extension': os.path.splitext(file_path)[1].lower()
                }
            elif os.path.isdir(file_path):
                return {
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'type': 'folder',
                    'parent': os.path.dirname(file_path)
                }
        except Exception:
            pass
        return None

    def open_file(self, file_path: str) -> bool:
        """Open file or folder with default application"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Path does not exist: {file_path}", path=file_path)

            if self.os_type == "Windows":
                os.startfile(file_path)
            elif self.os_type == "Darwin":
                subprocess.run(['open', file_path])
            else:
                subprocess.run(['xdg-open', file_path])

            logger.info(f"Opened: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to open file {file_path}: {e}")
            raise SystemError(f"Failed to open file {file_path}: {str(e)}",
                            operation="open_file", target=file_path)

    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """Type text on keyboard"""
        try:
            pyautogui.write(text, interval=interval)
            logger.info(f"Typed text: {text[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            raise SystemError(f"Failed to type text: {str(e)}",
                            operation="type_text", target=text)

    def press_key(self, key: str) -> bool:
        """Press a specific key or key combination"""
        try:
            if '+' in key:
                keys = key.split('+')
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(key)

            logger.info(f"Pressed key: {key}")
            return True

        except Exception as e:
            logger.error(f"Failed to press key {key}: {e}")
            raise SystemError(f"Failed to press key {key}: {str(e)}",
                            operation="press_key", target=key)

    def open_website(self, site_name: str) -> str:
        """Open website with intelligent URL construction"""
        logger.info(f"Opening website: {site_name}")

        try:
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

    def search_web(self, query: str) -> bool:
        """Search the web"""
        try:
            search_url = f"https://www.google.com/search?q={quote(query)}"
            webbrowser.open(search_url)
            logger.info(f"Performed web search for: {query}")
            return True

        except Exception as e:
            logger.error(f"Failed to search web: {e}")
            raise SystemError(f"Failed to search web: {str(e)}",
                            operation="search_web", target=query)

    def execute_system_command(self, command: str) -> bool:
        """Execute system command (with safety checks)"""
        # Dangerous commands to block
        dangerous_commands = [
            'format', 'del ', 'rmdir', 'shutdown', 'reboot',
            'rm -rf', 'sudo rm', 'dd if=', ':(){ :|:& };:',
            'fork bomb', 'virus', 'malware'
        ]

        command_lower = command.lower()
        if any(dangerous in command_lower for dangerous in dangerous_commands):
            raise SystemError(f"Command blocked for safety: {command}",
                            operation="system_command", target=command)

        try:
            if self.os_type == "Windows":
                os.system(command)
            else:
                subprocess.run(command, shell=True, check=True)

            logger.info(f"Executed system command: {command}")
            return True

        except Exception as e:
            logger.error(f"Failed to execute system command {command}: {e}")
            raise SystemError(f"Failed to execute system command: {str(e)}",
                            operation="system_command", target=command)

    def get_installed_apps(self) -> List[Dict[str, Any]]:
        """Get list of installed applications"""
        return [
            {'name': app['name'], 'path': app['path']}
            for app in self.installed_apps_cache.values()
        ]

    def _get_windows_installed_apps(self) -> Dict[str, Any]:
        """Get all installed Windows applications using registry and shell"""
        apps = {}

        try:
            # Method 1: Windows Registry
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
            logger.error(f"Error getting Windows apps: {e}")

        return apps


# Global system service instance
system_service = SystemService()