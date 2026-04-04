import os
import re
import subprocess
import urllib.request
import platform

# --- CONFIGURATION ---
MEDIA_FOLDERS = [
    r"C:\Path\To\Your\TV Shows",
    r"D:\Media\Movies"
]
FFMPEG_DIR = ""
MIN_FILE_SIZE_BYTES = 10240
SEARCH_SUFFIX = "official theme song audio"

YTDLP_BIN = "yt-dlp.exe" if platform.system() == "Windows" else "./yt-dlp"

def ensure_ytdlp():
    """Automatically downloads the yt-dlp core engine if missing."""
    if not os.path.exists(YTDLP_BIN):
        print(f"⚠️ {YTDLP_BIN} not found! Downloading the latest Core engine from GitHub...")
        try:
            url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe" if platform.system() == "Windows" else "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
            urllib.request.urlretrieve(url, YTDLP_BIN)
            if platform.system() != "Windows":
                os.chmod(YTDLP_BIN, 0o755)
            print("✅ Core engine downloaded successfully!\n")
        except Exception as e:
            print(f"❌ Failed to download core engine: {e}")
            exit(1)

def clean_folder_name(name):
    clean_name = name.replace('.', ' ').replace('_', ' ')
    year_match = re.search(r'^(.+)\b((?:19|20)\d{2})\b', clean_name)
    if year_match:
        return f"{year_match.group(1).strip()} {year_match.group(2)}"
    junk_pattern = r'(?i)\b(1080p|1080|720p|720|2160p|2160|4k|bluray|webrip|web-dl|hdrip|dvdrip|x264|x265|hevc|yts|yify|remux)\b.*'
    clean_name = re.sub(junk_pattern, '', clean_name)
    return ' '.join(re.sub(r'[\[\]\(\)-]', ' ', clean_name).split())

def download_theme(folder_path, folder_name, direct_url=None):
    search_title = clean_folder_name(folder_name)
    theme_dest = os.path.join(folder_path, "theme.mp3")
    download_target = direct_url if direct_url else f"ytsearch10:{search_title} {SEARCH_SUFFIX}"
    
    if direct_url:
        print(f"  🔗 Testing manual link...")
    else:
        print(f"  🔍 Searching theme for: {search_title} ...")
    
    cmd = [YTDLP_BIN, "-f", "bestaudio/best", "-x", "--audio-format", "mp3", 
           "--audio-quality", "192", "--no-playlist", "-q", "--no-warnings", "-i",
           "-o", os.path.join(folder_path, 'theme.%(ext)s'), download_target]
    
    if FFMPEG_DIR:
        cmd.extend(["--ffmpeg-location", FFMPEG_DIR])

    try:
        flag = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=flag)
        
        if os.path.exists(theme_dest):
            ignore_file = os.path.join(folder_path, ".ignore")
            if not os.path.exists(ignore_file): open(ignore_file, "w").close()
            print(f"  ✅ Success!")
            return True, ""
        
        return False, result.stderr.strip() or "File missing. Stream may be DRM protected."
    except Exception as e:
        return False, str(e)

def main():
    ensure_ytdlp()
    
    for base_folder in MEDIA_FOLDERS:
        print(f"\n📂 Scanning directory: {base_folder}")
        if not os.path.exists(base_folder): 
            print("  ⚠️ Directory not found. Skipping.")
            continue

        for item in os.listdir(base_folder):
            folder_path = os.path.join(base_folder, item)
            if os.path.isdir(folder_path):
                theme_path = os.path.join(folder_path, "theme.mp3")
                
                if os.path.exists(theme_path):
                    if os.path.getsize(theme_path) < MIN_FILE_SIZE_BYTES:
                        print(f"  🗑️ Found broken file in {item}. Replacing...")
                        os.remove(theme_path)
                    else:
                        print(f"  ⏭️ Skipped: {item} (Valid theme.mp3 exists)")
                        continue
                
                success, error_msg = download_theme(folder_path, item)
                
                if not success:
                    print(f"  ❌ Automated search failed. Reason: {error_msg}")
                    
                    while True:
                        manual_link = input(f"\n  ❓ Paste a direct YouTube URL for '{item}'\n  (or press Enter to skip): ").strip()
                        
                        if not manual_link:
                            print(f"  ⏭️ Skipping {item}.")
                            break 
                        
                        man_success, man_error = download_theme(folder_path, item, direct_url=manual_link)
                        
                        if man_success:
                            break 
                        else:
                            print(f"  ❌ Manual link failed. Reason: {man_error}")

if __name__ == "__main__":
    print("--- Starting Get Me A Theme (CLI) ---")
    main()
    print("\n--- Finished scanning all libraries! ---")
    # This stops the window from auto-closing suspiciously!
    input("\nPress Enter to exit...")