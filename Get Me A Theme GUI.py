import os
import re
import threading
import subprocess
import urllib.request
import platform
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

MIN_FILE_SIZE_BYTES = 10240
SEARCH_SUFFIX = "official theme song audio"
YTDLP_BIN = "yt-dlp.exe" if platform.system() == "Windows" else "./yt-dlp"

def clean_folder_name(name):
    clean_name = name.replace('.', ' ').replace('_', ' ')
    year_match = re.search(r'^(.+)\b((?:19|20)\d{2})\b', clean_name)
    if year_match:
        return f"{year_match.group(1).strip()} {year_match.group(2)}"
    junk_pattern = r'(?i)\b(1080p|1080|720p|720|2160p|2160|4k|bluray|webrip|web-dl|hdrip|dvdrip|x264|x265|hevc|yts|yify|remux)\b.*'
    clean_name = re.sub(junk_pattern, '', clean_name)
    return ' '.join(re.sub(r'[\[\]\(\)-]', ' ', clean_name).split())

class ModernThemeScraperApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Get Me A Theme")
        self.geometry("750x600")
        
        self.folders = []
        self.ffmpeg_path = ""
        
        self.waiting_for_input = threading.Event()
        self.manual_url_result = ""

        self.label = ctk.CTkLabel(self, text="🎵 Get Me A Theme", font=ctk.CTkFont(size=26, weight="bold"))
        self.label.pack(pady=(20, 10))

        self.folder_textbox = ctk.CTkTextbox(self, height=100, width=650, corner_radius=10, border_width=1, border_color="#3B3B3B", fg_color="#1E1E1E")
        self.folder_textbox.pack(pady=5)
        self.folder_textbox.configure(state="disabled")

        config_frame = ctk.CTkFrame(self, fg_color="transparent")
        config_frame.pack(pady=10)
        
        ctk.CTkButton(config_frame, text="➕ Add Folder", width=160, corner_radius=15, command=self.add_folder).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkButton(config_frame, text="🗑️ Clear Folders", width=160, corner_radius=15, fg_color="#A52F2F", hover_color="#7C1010", command=self.remove_folder).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkButton(config_frame, text="⚙️ Set FFmpeg", width=160, corner_radius=15, command=self.set_ffmpeg).grid(row=1, column=0, padx=10, pady=5)
        ctk.CTkButton(config_frame, text="🔄 Update Core (yt-dlp)", width=160, corner_radius=15, fg_color="#005A9E", hover_color="#003A6E", command=self.update_ytdlp_thread).grid(row=1, column=1, padx=10, pady=5)

        # FIXED FONT: Forces Windows to render full-color emojis!
        self.console = ctk.CTkTextbox(self, height=200, width=650, font=ctk.CTkFont(family="Segoe UI Emoji", size=14), corner_radius=10, border_width=1, border_color="#3B3B3B", fg_color="#000000", text_color="#FFFFFF")
        self.console.pack(pady=10)
        self.console.configure(state="disabled")

        self.start_btn = ctk.CTkButton(self, text="🚀 START SCRAPING", font=ctk.CTkFont(size=16, weight="bold"), fg_color="#2FA572", hover_color="#107C41", corner_radius=25, height=50, width=200, command=self.start_thread)
        self.start_btn.pack(pady=10)

        if not os.path.exists(YTDLP_BIN):
            self.log(f"⚠️ {YTDLP_BIN} is missing! Click 'Update Core' to download.")

    def log(self, message):
        self.console.configure(state="normal")
        self.console.insert("end", message + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Media Folder")
        if folder and folder not in self.folders:
            self.folders.append(folder)
            self.folder_textbox.configure(state="normal")
            self.folder_textbox.insert("end", folder + "\n")
            self.folder_textbox.configure(state="disabled")

    def remove_folder(self):
        self.folder_textbox.configure(state="normal")
        self.folder_textbox.delete("1.0", "end")
        self.folders = []
        self.folder_textbox.configure(state="disabled")
        self.log("🗑️ Cleared all media folders.")

    def set_ffmpeg(self):
        path = filedialog.askdirectory(title="Select FFmpeg Folder")
        if path:
            self.ffmpeg_path = path
            self.log(f"⚙️ FFmpeg path set to: {self.ffmpeg_path}")

    def update_ytdlp_thread(self):
        threading.Thread(target=self.download_ytdlp_binary, daemon=True).start()

    def download_ytdlp_binary(self):
        self.log("\n[INFO] Connecting to GitHub to download latest Core engine...")
        self.start_btn.configure(state="disabled")
        try:
            url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe" if platform.system() == "Windows" else "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
            urllib.request.urlretrieve(url, YTDLP_BIN)
            if platform.system() != "Windows":
                os.chmod(YTDLP_BIN, 0o755)
            self.log("✅ Core engine updated!")
        except Exception as e:
            self.log(f"❌ Failed to download core: {e}")
        finally:
            self.start_btn.configure(state="normal")

    def start_thread(self):
        if not self.folders:
            messagebox.showwarning("No Folders", "Please add a folder!")
            return
        if not os.path.exists(YTDLP_BIN):
            messagebox.showerror("Missing Core", "Download Core first!")
            return
        self.start_btn.configure(state="disabled", text="Scraping...")
        threading.Thread(target=self.run_scraper, daemon=True).start()

    def ask_manual_url(self, item, error_reason):
        dialog_text = f"Failed for:\n{item}\n\nReason: {error_reason}\n\nPaste YouTube URL:"
        dialog = ctk.CTkInputDialog(text=dialog_text, title="Manual Fallback")
        self.manual_url_result = dialog.get_input()
        self.waiting_for_input.set()

    def download_theme(self, folder_path, folder_name, direct_url=None):
        search_title = clean_folder_name(folder_name)
        theme_dest = os.path.join(folder_path, "theme.mp3")
        download_target = direct_url if direct_url else f"ytsearch10:{search_title} {SEARCH_SUFFIX}"
        
        self.log(f"🔍 Searching: {search_title}...")
        
        cmd = [YTDLP_BIN, "-f", "bestaudio/best", "-x", "--audio-format", "mp3", 
               "--audio-quality", "192", "--no-playlist", "-q", "--no-warnings", "-i",
               "-o", os.path.join(folder_path, 'theme.%(ext)s'), download_target]
        
        if self.ffmpeg_path:
            cmd.extend(["--ffmpeg-location", self.ffmpeg_path])

        try:
            flag = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=flag)
            if os.path.exists(theme_dest):
                ignore_file = os.path.join(folder_path, ".ignore")
                if not os.path.exists(ignore_file): open(ignore_file, "w").close()
                self.log(f"✅ Success!")
                return True, ""
            return False, result.stderr.strip() or "File missing. Stream may be DRM protected."
        except Exception as e:
            return False, str(e)

    def run_scraper(self):
        for base_folder in self.folders:
            self.log(f"\n📂 Library: {base_folder}")
            for item in os.listdir(base_folder):
                folder_path = os.path.join(base_folder, item)
                if os.path.isdir(folder_path):
                    theme_path = os.path.join(folder_path, "theme.mp3")
                    
                    if os.path.exists(theme_path):
                        if os.path.getsize(theme_path) < MIN_FILE_SIZE_BYTES:
                            self.log(f"🗑️ Found broken/empty file in {item}. Replacing...")
                            os.remove(theme_path)
                        else:
                            self.log(f"⏭️ Skipped: {item} (Valid theme.mp3 exists)")
                            continue
                    
                    success, error_msg = self.download_theme(folder_path, item)
                    if not success:
                        self.log(f"❌ Automated search failed. Reason: {error_msg}")
                        last_error = error_msg
                        while True:
                            self.after(0, self.ask_manual_url, item, last_error)
                            self.waiting_for_input.wait()
                            link = self.manual_url_result
                            self.waiting_for_input.clear()
                            
                            if not link:
                                self.log(f"⏭️ Skipping {item}.")
                                break
                            
                            s, e = self.download_theme(folder_path, item, direct_url=link)
                            if s: break
                            self.log(f"❌ Manual link failed. Reason: {e}")
                            last_error = e

        self.log("\n--- Finished! ---")
        self.start_btn.configure(state="normal", text="🚀 START SCRAPING")
        messagebox.showinfo("Done", "Scraping complete!")

if __name__ == "__main__":
    app = ModernThemeScraperApp()
    app.mainloop()