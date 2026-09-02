import customtkinter as ctk
import subprocess
import threading
import re
import os
import platform
import sys
import urllib.request
import json
import webbrowser
from tkinter import Menu

# --- APP INFO & UPDATER ---
CURRENT_VERSION = "v1.2.1"
REPO_API_URL = "https://api.github.com/repos/airdenmark/FFmpeg-Video-Audio-Downloader/releases/latest"
RELEASES_URL = "https://github.com/airdenmark/FFmpeg-Video-Audio-Downloader/releases/latest"

# --- PORTABLE RESOURCE FINDER ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_download_path():
    """ Returns the actual Windows Downloads folder path, even if moved or localized """
    if platform.system() == "Windows":
        try:
            import winreg
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            downloads_guid = "{374DE290-123F-4565-9164-39C4925E467B}"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
                return os.path.expandvars(location)
        except Exception:
            pass
    return os.path.join(os.path.expanduser('~'), 'Downloads')

# --- DYNAMIC PATHS ---
YT_DLP_PATH = resource_path("yt-dlp.exe")
FFMPEG_PATH = resource_path("ffmpeg.exe") 
ICON_PATH = resource_path("icon.ico") 

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FFmpeg Video Audio Downloader")
        self.geometry("550x460") 
        
        # Track highest percentage reached during a single download pass
        self._last_percent = 0.0
        
        # Set the window icon (Delay handles CustomTkinter initialization timing on Windows)
        if os.path.exists(ICON_PATH):
            self.after(200, lambda: self.iconbitmap(ICON_PATH))
        
        self.download_dir = get_download_path()
        
        # UI Elements
        self.label = ctk.CTkLabel(self, text="Paste link below:", font=("Segoe UI", 16, "bold"))
        self.label.pack(pady=(20, 10))

        self.entry = ctk.CTkEntry(self, width=420, placeholder_text="https://...")
        self.entry.pack(pady=10)
        
        # Format Dropdown Selector (Includes Native Audio & Transcoded MP3 Options)
        self.format_var = ctk.StringVar(value="MP4 (Video)")
        self.format_menu = ctk.CTkOptionMenu(
            self,
            values=[
                "MP4 (Video)", 
                "M4A (Best Native AAC)", 
                "MP3 (Best Available)", 
                "Opus (Raw WebM)"
            ],
            variable=self.format_var,
            width=220
        )
        self.format_menu.pack(pady=(5, 5))
        
        # Right-click context menu
        self.menu = Menu(self, tearoff=0)
        self.menu.add_command(label="Paste", command=self.paste_link)
        self.entry.bind("<Button-3>", self.show_menu)

        self.progress_bar = ctk.CTkProgressBar(self, width=420)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(15, 0))

        self.status_label = ctk.CTkLabel(self, text="Ready to download", font=("Segoe UI", 12))
        self.status_label.pack(pady=(5, 10))

        self.button = ctk.CTkButton(self, text="Download Now", command=self.start_thread, 
                                   fg_color="#2ecc71", hover_color="#27ae60", font=("Segoe UI", 13, "bold"), height=40)
        self.button.pack(pady=10)

        self.folder_button = ctk.CTkButton(self, text="Open Downloads Folder", command=self.open_downloads,
                                          fg_color="transparent", border_width=2, text_color="white",
                                          state="disabled", width=220)
        self.folder_button.pack(pady=10)

        # Update Notification Label
        self.update_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 12, "underline"), text_color="#3498db", cursor="hand2")
        self.update_label.pack(side="bottom", pady=(0, 15))
        self.update_label.bind("<Button-1>", lambda e: webbrowser.open(RELEASES_URL))

        # Version Label
        self.version_label = ctk.CTkLabel(self, text=f"Version: {CURRENT_VERSION}", 
                                         font=("Segoe UI", 10), text_color="gray")
        self.version_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        # Start update check in background
        threading.Thread(target=self.check_for_updates, daemon=True).start()

    def check_for_updates(self):
        try:
            req = urllib.request.Request(REPO_API_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_tag = data.get("tag_name", "").strip()
                
                if latest_tag:
                    # Parse version strings like "v1.1.2" into numeric tuples (1, 1, 2)
                    def parse_version(v_str):
                        clean_str = v_str.lstrip('vV')
                        return tuple(map(int, clean_str.split('.')))

                    latest_ver = parse_version(latest_tag)
                    current_ver = parse_version(CURRENT_VERSION)

                    # Only display prompt if the GitHub release version is strictly GREATER THAN current app version
                    if latest_ver > current_ver:
                        self.after(0, lambda: self.update_label.configure(
                            text=f"New update available ({latest_tag}) Click here to download."
                        ))
        except Exception:
            pass

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def paste_link(self):
        try:
            text = self.clipboard_get()
            self.entry.delete(0, 'end')
            self.entry.insert(0, text)
        except:
            pass

    def open_downloads(self):
        if platform.system() == "Windows":
            os.startfile(self.download_dir)
        else:
            subprocess.Popen(["open" if platform.system() == "Darwin" else "xdg-open", self.download_dir])

    def run_download(self, url):
        # Reset progress baseline for each new download
        self._last_percent = 0.0

        # Safely schedule UI initialization on the main thread
        self.after(0, lambda: (
            self.progress_bar.set(0),
            self.status_label.configure(text="Initializing...", text_color="white"),
            self.folder_button.configure(state="disabled")
        ))
        
        selected = self.format_var.get()

        # Base yt-dlp arguments
        cmd = [
            YT_DLP_PATH,
            "--newline",
            "-o", "%(title)s.%(ext)s",
            "--no-colors",
            "--ffmpeg-location", FFMPEG_PATH,
            "-P", self.download_dir,
        ]

        # Format-specific flags
        if selected == "M4A (Best Native AAC)":
            # Direct stream extraction: Zero quality loss, native AAC container
            cmd.extend([
                "-f", "ba[ext=m4a]/ba",
                "-x",
                "--audio-format", "m4a"
            ])

        elif selected == "Opus (Raw WebM)":
            # Direct stream extraction: Zero quality loss, native WebM container
            cmd.extend([
                "-f", "ba[ext=webm]/ba",
                "-x",
                "--audio-format", "opus"
            ])

        elif selected == "MP3 (Best Available)":
            # Transcodes best available audio stream into best available MP3 VBR
            cmd.extend([
                "-f", "bestaudio/best",
                "-x",
                "--audio-format", "mp3",
                "--audio-quality", "0"
            ])

        else:
            # Default: Full MP4 Video + Embedded Subtitles
            cmd.extend([
                "--merge-output-format", "mp4",
                "--write-subs",
                "--write-auto-subs",
                "--convert-subs", "srt",
                "--embed-subs",
            ])

        cmd.append(url)
        
        try:
            env = os.environ.copy()
            env["PATH"] = os.path.dirname(YT_DLP_PATH) + os.pathsep + env["PATH"]

            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                errors='replace',
                env=env,
                creationflags=0x08000000 
            )

            if process.stdout:
                for line in process.stdout:
                    match = re.search(r'(\d+\.\d+)%', line)
                    if match:
                        percent = float(match.group(1))
                        # Monotonic check: Only update UI if progress moves strictly forward
                        if percent > self._last_percent:
                            self._last_percent = percent
                            self.after(0, lambda p=percent: (
                                self.progress_bar.set(p / 100),
                                self.status_label.configure(text=f"Downloading: {p}%")
                            ))

            process.wait()

            if process.returncode == 0:
                self.after(0, lambda: (
                    self.progress_bar.set(1),
                    self.status_label.configure(text="Download complete! ✔", text_color="#2ecc71"),
                    self.folder_button.configure(state="normal")
                ))
            else:
                self.after(0, lambda: self.status_label.configure(
                    text="Download failed (check link)", text_color="#e74c3c"
                ))

        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda: self.status_label.configure(
                text=f"Error: {err_msg}", text_color="#e74c3c"
            ))
        
        finally:
            self.after(0, lambda: self.button.configure(state="normal", text="Download Now"))

    def start_thread(self):
        url = self.entry.get().strip()
        if not url: return
        self.button.configure(state="disabled", text="Working...")
        threading.Thread(target=self.run_download, args=(url,), daemon=True).start()

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()