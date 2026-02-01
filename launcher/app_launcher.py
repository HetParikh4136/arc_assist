# launcher/app_launcher.py
import subprocess
import platform
import os
import time
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

class AppLauncherError(Exception):
    """Custom exception for app launcher errors."""
    pass

class AppLauncher:
    def __init__(self):
        self.os_type = platform.system()
        self._load_config()

    def _load_config(self):
        """Load application configuration from environment variables."""
        from config import DEBUG
        
        self.debug = DEBUG
        
        # Load paths from environment variables
        self.vs_code_path = os.getenv("VS_CODE_PATH", "code")
        self.spotify_path = os.getenv("SPOTIFY_PATH")
        self.discord_path = os.getenv("DISCORD_PATH")
        self.brave_path = os.getenv("BRAVE_PATH", "brave")
        self.chrome_url = os.getenv("CHROME_URL", "https://claude.ai")
        self.github_url = os.getenv("GITHUB_URL", "https://github.com/HetParikh4136")

    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        if not isinstance(url, str):
            return False
        return url.startswith(("http://", "https://", "file://"))

    def _validate_path(self, path: str) -> bool:
        """Validate file path exists."""
        return Path(path).exists()

    def _safe_popen(
        self,
        args: List[str],
        shell: bool = False,
        description: str = ""
    ) -> Optional[subprocess.Popen]:
        """
        Safely execute a subprocess with validation.
        
        Args:
            args: Command and arguments as list
            shell: Whether to use shell (dangerous, avoid when possible)
            description: Description of what's being launched
        
        Returns:
            Popen object or None if execution failed
        """
        if not args or not isinstance(args, list):
            logger.error(f"Invalid arguments for subprocess: {args}")
            return None

        try:
            # On Windows, always use list form and avoid shell=True
            process = subprocess.Popen(
                args,
                shell=shell,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if self.os_type == "Windows" else 0
            )
            if description:
                print(f"✅ {description}")
            return process
        except FileNotFoundError:
            logger.error(f"Command not found: {args[0]}")
            if description:
                print(f"❌ Failed to launch: {description}")
            return None
        except Exception as e:
            logger.error(f"Error launching subprocess: {e}")
            if description:
                print(f"❌ Error launching: {description}")
            return None

    # ---------- macOS ----------
    def _launch_macos(self):
        print("\n🚀 DOUBLE CLAP DETECTED! Launching apps...\n")

        try:
            # VS Code with folder
            tbt_path = os.path.expanduser("~/code/tbt")
            if self._validate_path(tbt_path):
                self._safe_popen(
                    ["open", "-a", "Visual Studio Code", tbt_path],
                    description=f"Launched VS Code with folder: {tbt_path}"
                )
            else:
                logger.warning(f"VS Code folder not found: {tbt_path}")
                self._safe_popen(
                    ["open", "-a", "Visual Studio Code"],
                    description="Launched VS Code"
                )
            time.sleep(0.5)

            # Chrome with URL
            if self._validate_url(self.chrome_url):
                self._safe_popen(
                    ["open", "-a", "Google Chrome", "--args", "--new-window", self.chrome_url],
                    description=f"Launched Chrome with {self.chrome_url}"
                )
            time.sleep(0.5)

        except Exception as e:
            logger.error(f"Error in macOS launch: {e}")
            print(f"❌ Error during macOS launch: {e}")

    # ---------- Windows ----------
    def _launch_windows(self):
        print("\n🚀 DOUBLE CLAP DETECTED! Launching apps...\n")

        try:
            # VS Code - use cmd.exe to launch
            import shlex
            self._safe_popen(
                ["cmd.exe", "/c", "start", "", self.vs_code_path],
                description="Launched VS Code"
            )
            time.sleep(0.5)

            # Spotify
            if self.spotify_path and self._validate_path(self.spotify_path):
                self._safe_popen(
                    ["cmd.exe", "/c", "start", "", self.spotify_path],
                    description="Launched Spotify"
                )
                time.sleep(0.5)
            else:
                logger.warning("Spotify path not configured or not found")

            # Brave Browser
            if self._validate_path(self.brave_path):
                self._safe_popen(
                    ["cmd.exe", "/c", "start", "", self.brave_path, "--new-window", "--profile-directory=Default"],
                    description="Launched Brave Browser (Default Profile)"
                )
            else:
                logger.warning(f"Brave path not found: {self.brave_path}")
            time.sleep(0.5)

            # Discord
            if self.discord_path and self._validate_path(self.discord_path):
                self._safe_popen(
                    [self.discord_path, "--processStart", "Discord.exe"],
                    description="Launched Discord"
                )
            else:
                logger.warning("Discord path not configured or not found")
            time.sleep(0.5)

        except Exception as e:
            logger.error(f"Error in Windows launch: {e}")
            print(f"❌ Error during Windows launch: {e}")

    # ---------- Linux ----------
    def _launch_linux(self):
        print("\n🚀 DOUBLE CLAP DETECTED! Launching apps...\n")

        try:
            # VS Code
            self._safe_popen(
                ["code"],
                description="Launched VS Code"
            )
            time.sleep(0.5)

            # Chrome / Chromium with URL
            if self._validate_url(self.chrome_url):
                process = self._safe_popen(
                    ["google-chrome", self.chrome_url],
                    description="Launched Google Chrome"
                )
                if not process:
                    self._safe_popen(
                        ["chromium-browser", self.chrome_url],
                        description="Launched Chromium"
                    )
            time.sleep(0.5)

            # Discord
            self._safe_popen(
                ["discord"],
                description="Launched Discord"
            )
            time.sleep(0.5)

        except Exception as e:
            logger.error(f"Error in Linux launch: {e}")
            print(f"❌ Error during Linux launch: {e}")

    # ---------- PUBLIC METHODS ----------
    def launch_apps(self):
        """Launch platform-specific applications."""
        try:
            if self.os_type == "Darwin":
                self._launch_macos()
            elif self.os_type == "Windows":
                self._launch_windows()
            elif self.os_type == "Linux":
                self._launch_linux()
            else:
                raise AppLauncherError(f"Unsupported OS: {self.os_type}")

            print("\n✨ All apps launched!\n")
        except Exception as e:
            logger.error(f"Error launching apps: {e}")
            print(f"❌ Failed to launch apps: {e}")

    def open_url(self, url: Optional[str] = None):
        """Open URL in default browser."""
        try:
            target_url = url or self.github_url
            
            if not self._validate_url(target_url):
                raise AppLauncherError(f"Invalid URL format: {target_url}")
            
            print("\n🎵 TRIPLE CLAP DETECTED! Opening URL...\n")

            if self.os_type == "Darwin":
                self._safe_popen(
                    ["open", target_url],
                    description=f"Opening: {target_url}"
                )
            elif self.os_type == "Windows":
                # Use URL handler instead of shell command
                import webbrowser
                webbrowser.open(target_url)
                print(f"✅ Opening: {target_url}")
            elif self.os_type == "Linux":
                self._safe_popen(
                    ["xdg-open", target_url],
                    description=f"Opening: {target_url}"
                )

            print("\n✨ Enjoy!\n")
        except Exception as e:
            logger.error(f"Error opening URL: {e}")
            print(f"❌ Failed to open URL: {e}")
