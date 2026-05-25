import io
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
from PIL import Image, ImageTk

# Servis Sınıflarının Bağlanması
from gemini_service import GeminiService
from lastfm_service import LastFMService
from image_service import ImageService
from utils import ExportUtils

# Kılavuzdaki Sabit API Anahtarları
GEMINI_API_KEY = "AIzaSyA2mrpSuuhtj5v_W-wBxIa0nV0tFRnNfX4"
LASTFM_API_KEY = "1093b73660eca2814acb8ca879408419"


class AlbumCoverStudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDA-226 Album Cover Studio")
        self.root.geometry("1300x820")
        self.root.configure(bg="#121212")  # Spotify Koyu Teması

        self.album_data = None
        self.tracklist = None
        self.generated_image = None

        # Servislerin Örneklenmesi
        self.gemini_service = GeminiService(GEMINI_API_KEY)
        self.lastfm_service = LastFMService(LASTFM_API_KEY)
        self.image_service = ImageService()

        # REQUIREMENT 2: 'clam' teması tabanlı ttk.Style yapılandırması
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()

        self.create_left_panel()
        self.create_right_panel()
        self.create_status_bar()

    def configure_styles(self):
        self.style.configure("TLabel", background="#121212", foreground="white", font=("Helvetica", 10))
        self.style.configure("Panel.TLabel", background="#181818", foreground="#B3B3B3", font=("Helvetica", 10))
        self.style.configure("Header.TLabel", background="#181818", foreground="#1DB954",
                             font=("Helvetica", 16, "bold"))
        self.style.configure("TCombobox", fieldbackground="#2A2A2A", background="#181818", foreground="white")
        self.style.configure("TSpinbox", fieldbackground="#2A2A2A", background="#181818", foreground="white")

        # Spotify Yeşili Butonlar
        self.style.configure("Spotify.TButton", background="#1DB954", foreground="white",
                             font=("Helvetica", 11, "bold"), borderwidth=0)
        self.style.map("Spotify.TButton", background=[("active", "#1ED760"), ("disabled", "#555555")])

        self.style.configure("Secondary.TButton", background="#282828", foreground="white", font=("Helvetica", 10),
                             borderwidth=0)
        self.style.map("Secondary.TButton", background=[("active", "#3E3E3E"), ("disabled", "#151515")])

    def create_left_panel(self):
        self.left_frame = tk.Frame(self.root, bg="#181818", width=420)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)
        self.left_frame.pack_propagate(False)

        lbl_title = ttk.Label(self.left_frame, text="Album Cover Studio", style="Header.TLabel")
        lbl_title.pack(anchor=tk.W, padx=20, pady=20)

        lbl_journal = ttk.Label(self.left_frame, text="Describe your mood, enjoy the generated tracklist:",
                                style="Panel.TLabel")
        lbl_journal.pack(anchor=tk.W, padx=20, pady=5)

        # REQUIREMENT 3: Çok satırlı giriş alanı ve Sensible Default Değer
        self.txt_journal = tk.Text(self.left_frame, height=8, bg="#2A2A2A", fg="white", insertbackground="white",
                                   relief=tk.FLAT, font=("Helvetica", 10), wrap=tk.WORD)
        self.txt_journal.pack(fill=tk.X, padx=20, pady=5)
        self.txt_journal.insert(tk.END,
                                "I was looking at the sea in Izmir. It was raining softly, and an old song was playing through my headphones. I felt both peaceful and melancholic.")

        # Giriş Parametreleri Kontrolleri (AGP)
        ttk.Label(self.left_frame, text="Music Genre:", style="Panel.TLabel").pack(anchor=tk.W, padx=20, pady=5)
        genres = ["Pop", "Rock", "Hip-Hop / Rap", "Electronic", "Indie", "R&B / Soul", "Jazz", "Metal", "Türk Pop",
                  "Klasik"]
        self.cb_genre = ttk.Combobox(self.left_frame, values=genres, state="readonly")
        self.cb_genre.pack(fill=tk.X, padx=20, pady=5)
        self.cb_genre.set("Indie")

        ttk.Label(self.left_frame, text="Era:", style="Panel.TLabel").pack(anchor=tk.W, padx=20, pady=5)
        eras = ["1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]
        self.cb_era = ttk.Combobox(self.left_frame, values=eras, state="readonly")
        self.cb_era.pack(fill=tk.X, padx=20, pady=5)
        self.cb_era.set("2000s")

        ttk.Label(self.left_frame, text="Track Count (6-14):", style="Panel.TLabel").pack(anchor=tk.W, padx=20, pady=5)
        self.spin_tracks = ttk.Spinbox(self.left_frame, from_=6, to=14, state="readonly")
        self.spin_tracks.pack(anchor=tk.W, padx=20, pady=5)
        self.spin_tracks.set(10)

        # Butonlar
        self.btn_generate = ttk.Button(self.left_frame, text="GENERATE ALBUM", style="Spotify.TButton",
                                       command=self.start_generation_thread)
        self.btn_generate.pack(fill=tk.X, padx=20, pady=25)

        self.btn_export = ttk.Button(self.left_frame, text="SAVE ALBUM (JSON + PNG)", style="Secondary.TButton",
                                     command=self.export_album_data, state=tk.DISABLED)
        self.btn_export.pack(fill=tk.X, padx=20, pady=5)

    def create_right_panel(self):
        self.right_frame = tk.Frame(self.root, bg="#121212")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Üst Alan: Spotify Stili Düzen Bölümü
        self.upper_right = tk.Frame(self.right_frame, bg="#121212")
        self.upper_right.pack(fill=tk.X, pady=10)

        self.cover_frame = tk.Frame(self.upper_right, bg="#181818", width=220, height=220)
        self.cover_frame.pack(side=tk.LEFT, padx=10, pady=5)
        self.cover_frame.pack_propagate(False)

        self.lbl_cover = tk.Label(self.cover_frame, text="Generated cover art\nwill appear here", bg="#181818",
                                  fg="#B3B3B3", font=("Helvetica", 10, "italic"))
        self.lbl_cover.pack(fill=tk.BOTH, expand=True)

        # Meta Veri Bilgi Kartları
        self.meta_display_frame = tk.Frame(self.upper_right, bg="#121212")
        self.meta_display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=25)

        self.lbl_album_title = tk.Label(self.meta_display_frame, text="Fictional Album Title", bg="#121212", fg="white",
                                        font=("Helvetica", 22, "bold"), anchor="w")
        self.lbl_album_title.pack(fill=tk.X, pady=2)

        self.lbl_artist_sub = tk.Label(self.meta_display_frame, text="Artist Concept", bg="#121212", fg="#B3B3B3",
                                       font=("Helvetica", 12, "bold"), anchor="w")
        self.lbl_artist_sub.pack(fill=tk.X, pady=2)

        self.lbl_details_sub = tk.Label(self.meta_display_frame, text="Year  •  Tracks  •  Record Label", bg="#121212",
                                        fg="#777777", font=("Helvetica", 10), anchor="w")
        self.lbl_details_sub.pack(fill=tk.X, pady=2)

        self.txt_mood_desc = tk.Text(self.meta_display_frame, bg="#121212", fg="#B3B3B3",
                                     font=("Helvetica", 9, "italic"), height=4, relief=tk.FLAT, wrap=tk.WORD,
                                     state=tk.DISABLED)
        self.txt_mood_desc.pack(fill=tk.X, pady=5)

        # Alt Alan: Kaydırılabilir Şarkı Tablosu
        lbl_tracklist_title = ttk.Label(self.right_frame, text="GENERATED TRACKLIST (REAL SONGS)",
                                        font=("Helvetica", 11, "bold"))
        lbl_tracklist_title.pack(anchor=tk.W, padx=10, pady=10)

        self.tracklist_container = tk.Frame(self.right_frame, bg="#121212")
        self.tracklist_container.pack(fill=tk.BOTH, expand=True, padx=10)

        self.canvas = tk.Canvas(self.tracklist_container, bg="#121212", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.tracklist_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#121212")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def create_status_bar(self):
        # REQUIREMENT 9: Durum Çubuğu
        self.lbl_status = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#181818",
                                   fg="white", font=("Helvetica", 9), padx=15)
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, text):
        self.root.after(0, lambda: self.lbl_status.config(text=text))

    def start_generation_thread(self):
        # REQUIREMENT 9: Arayüz kilitlenmelerini önleyen arka plan iş parçacığı (threading)
        threading.Thread(target=self.generate_album_process, daemon=True).start()

    def generate_album_process(self):
        self.root.after(0, lambda: self.btn_generate.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.btn_export.config(state=tk.DISABLED))

        journal = self.txt_journal.get("1.0", tk.END).strip()
        genre = self.cb_genre.get()
        era = self.cb_era.get()
        track_count = int(self.spin_tracks.get())

        try:
            # Step 1: Gemini Veri Üretimi
            self.update_status("Gemini is thinking...")
            self.album_data = self.gemini_service.generate_album_data(journal, genre, era, track_count)

            # Step 2: Last.fm Gerçek Şarkı İstekleri
            self.update_status("Fetching tracks...")
            tags = self.album_data.get("lastfm_tags", [genre])
            self.tracklist = self.lastfm_service.build_tracklist(tags, track_count)

            # Step 3: Kapak Tasarımı Oluşturulması
            self.update_status("Generating cover...")
            cover_prompt = self.album_data.get("cover_prompt", "Abstract art")
            self.generated_image = self.image_service.generate_cover(cover_prompt, genre, era)

            # Sonuç ekranının çizilmesi
            self.root.after(0, self.display_results)

        except Exception as e:
            self.root.after(0,
                            lambda: messagebox.showerror("Pipeline Error", f"Failed to complete processing:\n{str(e)}"))
            self.update_status("Generation failed.")
        finally:
            self.root.after(0, lambda: self.btn_generate.config(state=tk.NORMAL))

    def display_results(self):
        # REQUIREMENT 7: Spotify tarzı arayüz mockup çıktısı
        self.lbl_album_title.config(text=self.album_data.get('album_name', 'Unknown Title'))
        self.lbl_artist_sub.config(text=f"By {self.album_data.get('artist_name', 'Unknown Artist')}")

        details = f"{self.album_data.get('year', 'N/A')}  •  {len(self.tracklist)} songs  •  {self.album_data.get('label', 'Fictional Records')}"
        self.lbl_details_sub.config(text=details)

        self.txt_mood_desc.config(state=tk.NORMAL)
        self.txt_mood_desc.delete("1.0", tk.END)
        self.txt_mood_desc.insert(tk.END, f"Mood/Concept: {self.album_data.get('mood_description', '')}")
        self.txt_mood_desc.config(state=tk.DISABLED)

        # Görsel Entegrasyonu (Requirement 6)
        resized_img = self.generated_image.resize((220, 220), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(resized_img)
        self.lbl_cover.config(image=self.tk_img, text="")

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # REQUIREMENT 7: Her şarkı satırı ve web tarayıcısını tetikleyen "Listen" butonları
        for idx, track in enumerate(self.tracklist, start=1):
            track_row = tk.Frame(self.scrollable_frame, bg="#121212", pady=6)
            track_row.pack(fill=tk.X, expand=True)

            track_text = f"{idx:<2}   {track.get('name')}   —   {track.get('artist')}"
            lbl_track = tk.Label(track_row, text=track_text, bg="#121212", fg="#B3B3B3", font=("Helvetica", 10),
                                 anchor=tk.W)
            lbl_track.pack(side=tk.LEFT, padx=15, fill=tk.X, expand=True)

            # Tıklanınca ilgili linki varsayılan browserda açar
            url = track.get("url")
            btn_listen = tk.Button(track_row, text="Listen", bg="#181818", fg="#1DB954", font=("Helvetica", 9, "bold"),
                                   relief=tk.FLAT, activebackground="#1DB954", activeforeground="white",
                                   command=lambda u=url: webbrowser.open(u) if u else None)
            btn_listen.pack(side=tk.RIGHT, padx=25)

        self.update_status("Ready")
        self.btn_export.config(state=tk.NORMAL)

    def export_album_data(self):
        if not self.album_data or not self.generated_image:
            return

        # REQUIREMENT 8: Klasör seçme penceresi ve kaydetme çağrısı
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            try:
                ExportUtils.save_album(self.album_data, self.tracklist, self.generated_image, folder_selected)
                messagebox.showinfo("Success", f"Fictional assets successfully exported to:\n{folder_selected}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not save files:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AlbumCoverStudioApp(root)
    root.mainloop()



