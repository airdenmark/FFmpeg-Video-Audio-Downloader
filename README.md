# 🎬 ffmpeg Video Downloader
A powerful, standalone GUI-based video downloader powered by `yt-dlp` and `ffmpeg`. Designed for high-quality video archiving with full subtitle support.

![App Preview](app_preview.png)

## ✨ Key Features
* **Dark Mode UI:** A clean, modern interface built with CustomTkinter.
* **Advanced Subtitles:** Automatically embeds subtitles into the MP4 file and generates a separate `.srt` file for external use.
* **Wide Support:** Powered by `yt-dlp`, supporting 1,000+ sites (YouTube, DRTV, ARTE, Vimeo, etc.).
* **Portable:** No Python installation required. Just download and run!

## ⚖️ Comparison: Standalone vs. Extensions

| Feature | Browser Extensions | ffmpeg Video Downloader |
| :--- | :--- | :--- |
| **Privacy** | Can track browsing history | **100% Private / Local** |
| **FFmpeg Merging** | Usually requires extra install | **Fully Bundled** |
| **Subtitle Files** | Often hardcoded or ignored | **Embedded + Separate .srt** |
| **Speed/Limits** | Often restricted for free users | **Unlimited & Free** |
| **Site Support** | Varies by extension | **1000+ Sites (yt-dlp)** |

## 📦 Installation & Usage
1. Go to the [Latest Release](https://github.com/airdenmark/ffmpeg-Video-Downloader/releases/latest).
2. Download the `.zip` file (e.g., `ffmpeg.Video.Downloader.v1.1.2.zip`).
3. Extract the contents to a folder of your choice.
4. **Pro Tip:** Right-click the `.exe` file, select **Properties**, check the **Unblock** box at the bottom, and click **OK**. This prevents Windows from asking for permission every time you run the app.
5. Run the `.exe` file to start downloading!

> [!IMPORTANT]
> **Note on Windows SmartScreen:**
> Because this is a new, independent application, Windows may show a warning. If you haven't "unblocked" the file as described above, click **"More info"** and then **"Run anyway"**

## ⚙️ Technical Specifications & Core Components
This application is compiled using the latest stable libraries to ensure maximum compatibility and speed.

| Component | Version | Link |
| :--- | :--- | :--- |
| **yt-dlp** | 2026.07.04 | [View Project](https://github.com/yt-dlp/yt-dlp) |
| **FFmpeg** | 2026-07-20-git-c23123630e | [gyan.dev Builds](https://www.gyan.dev/ffmpeg/builds/) |
| **Python** | 3.13 | [View Project](https://www.python.org/) |
| **CustomTkinter** | v6.0.0 | [View Project](https://github.com/TomSchimansky/CustomTkinter) |
