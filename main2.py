import io
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
from PIL import Image, ImageTk

# Ekip arkadaşlarınızın yazdığı servis modülleri
from gemini_service import GeminiService
from lastfm_service import LastFMService
from image_service import ImageService
from utils import ExportUtils  # Arkadaşının son yazdığı utils modülü tam entegre

# Kılavuzdaki Sabit API Anahtarları
GEMINI_API_KEY = "AIzaSyA2mrpSuuhtj5v_W-wBxIa0nV0tFRnNfX4"
LASTFM_API_KEY = "1093b73660eca2814acb8ca879408419"


class AlbumCoverStudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDA-226 Album Cover Studio")
        self.root.geometry("1300x850")
        self.root.configure(bg="#121212")  # Spotify Koyu Teması Ana Arka Plan

        # Veri depoları
        self.album_data = None
        self.tracklist = None
        self.generated_image = None
        self.tk_img = None  # Resmin Python hafızasından silinmesini engellemek için

        # Servislerin Örneklenmesi
        self.gemini_service = GeminiService(GEMINI_API_KEY)
        self.lastfm_service = LastFMService(LASTFM_API_KEY)
        self.image_service = ImageService()

        # REQUIREMENT 2: 'clam' teması tabanlı modern ttk.Style yapılandırması
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()

        # Arayüz Bileşenlerinin Oluşturulması (Layout Yönetimi)
        self.create_left_panel()
        self.create_right_panel()
        self.create_status_bar()

    def configure_styles(self):
        """Uygulamanın genel Spotify estetiğini belirleyen stil tanımlamaları"""
        self.style.configure("TLabel", background="#121212", foreground="white", font=("Helvetica", 10))
        self.style.configure("Panel.TLabel", background="#181818", foreground="#B3B3B3", font=("Helvetica", 10, "bold"))
        self.style.configure("Header.TLabel", background="#181818", foreground="#1DB954", font=("Helvetica", 18, "bold"))
        self.style.configure("Section.TLabel", background="#121212", foreground="#FFFFFF", font=("Helvetica", 12, "bold"))
        
        self.style.configure("TCombobox", fieldbackground="#2A2A2A", background="#181818", foreground="white", arrowcolor="white")
        self.style.map("TCombobox", fieldbackground=[("readonly", "#2A2A2A")], foreground=[("readonly", "white")])
        
        self.style.configure("TSpinbox", fieldbackground="#2A2A2A", background="#181818", foreground="white", arrowcolor="white")
        self.style.map("TSpinbox", fieldbackground=[("readonly", "#2A2A2A")], foreground=[("readonly", "white")])

        # Spotify Yeşili Birincil Buton Tasarımı
        self.style.configure("Spotify.TButton", background="#1DB954", foreground="white",
                             font=("Helvetica", 11, "bold"), borderwidth=0, focuscolor="none")
        self.style.map("Spotify.TButton", 
                       background=[("active", "#1ED760"), ("disabled", "#333333")],
                       foreground=[("disabled", "#777777")])

        # Koyu Gri İkincil Buton Tasarımı
        self.style.configure("Secondary.TButton", background="#282828", foreground="white", 
                             font=("Helvetica", 10, "bold"), borderwidth=0, focuscolor="none")
        self.style.map("Secondary.TButton", 
                       background=[("active", "#3E3E3E"), ("disabled", "#151515")],
                       foreground=[("disabled", "#555555")])

        # Modern Kaydırma Çubuğu (Scrollbar) Tasarımı
        self.style.configure("TScrollbar", gripcount=0, background="#282828", troughcolor="#121212", 
                             bordercolor="#121212", arrowcolor="#282828")
        self.style.map("TScrollbar", background=[("active", "#3E3E3E")])

    def create_left_panel(self):
        """Parametre girişlerinin ve butonların yer aldığı sol panel"""
        self.left_frame = tk.Frame(self.root, bg="#181818", width=420, highlightbackground="#282828", highlightthickness=1)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        self.left_frame.pack_propagate(False)

        lbl_title = ttk.Label(self.left_frame, text="🎵 Album Cover Studio", style="Header.TLabel")
        lbl_title.pack(anchor=tk.W, padx=25, pady=(25, 15))

        lbl_journal = ttk.Label(self.left_frame, text="Describe your mood / journal entry:", style="Panel.TLabel")
        lbl_journal.pack(anchor=tk.W, padx=25, pady=(10, 5))

        # REQUIREMENT 3: Çok satırlı metin alanı ve Sensible Default Değer ataması
        self.txt_journal = tk.Text(self.left_frame, height=7, bg="#2A2A2A", fg="white", insertbackground="white",
                                   relief=tk.FLAT, font=("Helvetica", 10), wrap=tk.WORD, padx=10, pady=10)
        self.txt_journal.pack(fill=tk.X, padx=25, pady=5)
        self.txt_journal.insert(tk.END,
                                "I was looking at the sea in Izmir. It was raining softly, and an old song was playing through my headphones. I felt both peaceful and melancholic.")

        # Giriş Parametreleri Seçim Alanları
        ttk.Label(self.left_frame, text="Music Genre:", style="Panel.TLabel").pack(anchor=tk.W, padx=25, pady=(15, 5))
        genres = ["Pop", "Rock", "Hip-Hop / Rap", "Electronic", "Indie", "R&B / Soul", "Jazz", "Metal", "Türk Pop", "Klasik"]
        self.cb_genre = ttk.Combobox(self.left_frame, values=genres, state="readonly")
        self.cb_genre.pack(fill=tk.X, padx=25, pady=5)
        self.cb_genre.set("Indie")

        ttk.Label(self.left_frame, text="Historical Era:", style="Panel.TLabel").pack(anchor=tk.W, padx=25, pady=(15, 5))
        eras = ["1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]
        self.cb_era = ttk.Combobox(self.left_frame, values=eras, state="readonly")
        self.cb_era.pack(fill=tk.X, padx=25, pady=5)
        self.cb_era.set("2000s")

        ttk.Label(self.left_frame, text="Track Count (6-14):", style="Panel.TLabel").pack(anchor=tk.W, padx=25, pady=(15, 5))
        self.spin_tracks = ttk.Spinbox(self.left_frame, from_=6, to=14, state="readonly")
        self.spin_tracks.pack(anchor=tk.W, padx=25, pady=5)
        self.spin_tracks.set(10)

        # Tetikleme ve Dışa Aktarma Butonları
        self.btn_generate = ttk.Button(self.left_frame, text="GENERATE ALBUM", style="Spotify.TButton",
                                       command=self.start_generation_thread)
        self.btn_generate.pack(fill=tk.X, padx=25, pady=(35, 10), ipady=8)

        self.btn_export = ttk.Button(self.left_frame, text="💾 EXPORT AS JSON + PNG", style="Secondary.TButton",
                                     command=self.export_album_data, state=tk.DISABLED)
        self.btn_export.pack(fill=tk.X, padx=25, pady=5, ipady=6)

    def create_right_panel(self):
        """Albüm kapağının ve şarkı listesinin sergileneceği sağ panel"""
        self.right_frame = tk.Frame(self.root, bg="#121212")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 20), pady=20)

        # Üst Alan: Albüm Özeti ve Kapak Resmi Kartı
        self.upper_right = tk.Frame(self.right_frame, bg="#121212")
        self.upper_right.pack(fill=tk.X, pady=(10, 20))

        # Albüm Kapak Çerçevesi
        self.cover_frame = tk.Frame(self.upper_right, bg="#181818", width=220, height=220, highlightbackground="#282828", highlightthickness=1)
        self.cover_frame.pack(side=tk.LEFT, padx=10, pady=5)
        self.cover_frame.pack_propagate(False)

        self.lbl_cover = tk.Label(self.cover_frame, text="Generated cover art\nwill appear here", bg="#181818",
                                 fg="#777777", font=("Helvetica", 10, "italic"))
        self.lbl_cover.pack(fill=tk.BOTH, expand=True)

        # Meta Veri Metin Kartı Bölümü
        self.meta_display_frame = tk.Frame(self.upper_right, bg="#121212")
        self.meta_display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=25)

        self.lbl_album_title = tk.Label(self.meta_display_frame, text="Fictional Album Title", bg="#121212", fg="white",
                                        font=("Helvetica", 24, "bold"), anchor="w")
        self.lbl_album_title.pack(fill=tk.X, pady=(5, 2))

        self.lbl_artist_sub = tk.Label(self.meta_display_frame, text="Artist Concept", bg="#121212", fg="#1DB954",
                                       font=("Helvetica", 13, "bold"), anchor="w")
        self.lbl_artist_sub.pack(fill=tk.X, pady=2)

        self.lbl_details_sub = tk.Label(self.meta_display_frame, text="Year  •  Tracks  •  Record Label", bg="#121212",
                                        fg="#B3B3B3", font=("Helvetica", 10), anchor="w")
        self.lbl_details_sub.pack(fill=tk.X, pady=2)

        # Yapay Zeka Gerekçe Alanı (Mood Description)
        self.txt_mood_desc = tk.Text(self.meta_display_frame, bg="#121212", fg="#777777",
                                     font=("Helvetica", 9, "italic"), height=4, relief=tk.FLAT, wrap=tk.WORD,
                                     state=tk.DISABLED, highlightthickness=0)
        self.txt_mood_desc.pack(fill=tk.X, pady=(10, 5))

        # Alt Alan: Kaydırılabilir Şarkılar Listesi
        lbl_tracklist_title = ttk.Label(self.right_frame, text="GENERATED TRACKLIST (REAL SONGS RECOMMENDED BY LAST.FM)", style="Section.TLabel")
        lbl_tracklist_title.pack(anchor=tk.W, padx=10, pady=(10, 15))

        self.tracklist_container = tk.Frame(self.right_frame, bg="#121212")
        self.tracklist_container.pack(fill=tk.BOTH, expand=True, padx=10)

        # Sürükleme ve Kaydırma Altyapısı
        self.canvas = tk.Canvas(self.tracklist_container, bg="#121212", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.tracklist_container, orient="vertical", command=self.canvas.yview, style="TScrollbar")
        self.scrollable_frame = tk.Frame(self.canvas, bg="#121212")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_frame_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Dinamik Genişlik Ayarı ve Fare Tekerleği Entegrasyonu
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_frame_window, width=e.width))
        self.root.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    def create_status_bar(self):
        """REQUIREMENT 9: Alt kısımda yer alan durum bilgilendirme çubuğu"""
        self.lbl_status = tk.Label(self.root, text="Ready", bd=0, relief=tk.FLAT, anchor=tk.W, bg="#282828",
                                   fg="#B3B3B3", font=("Helvetica", 9), padx=20, pady=6)
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, text):
        self.root.after(0, lambda: self.lbl_status.config(text=text))

    def start_generation_thread(self):
        """REQUIREMENT 9: GUI donmasını engelleyen Thread tetikleyicisi"""
        threading.Thread(target=self.generate_album_process, daemon=True).start()

    def generate_album_process(self):
        """Pipeline Akış Motoru"""
        self.root.after(0, lambda: self.btn_generate.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.btn_export.config(state=tk.DISABLED))

        journal = self.txt_journal.get("1.0", tk.END).strip()
        genre = self.cb_genre.get()
        era = self.cb_era.get()
        track_count = int(self.spin_tracks.get())

        try:
            # Adım 1: Gemini Veri Üretimi
            self.update_status("🔄 Gemini is analyzing your mood journal...")
            self.album_data = self.gemini_service.generate_album_data(journal, genre, era, track_count)

            # Adım 2: Last.fm Entegrasyonu (DÜZELTİLDİ: "mood_tags" uyuşmazlığı giderildi)
            self.update_status("🎵 Querying Last.fm database for real songs...")
            tags = self.album_data.get("mood_tags", [genre.lower()])
            hybrid_tags = self.lastfm_service.build_lastfm_tags(genre, era, tags)
            self.tracklist = self.lastfm_service.build_tracklist(hybrid_tags, track_count)

            # Adım 3: Pollinations.ai Üzerinden Görsel Üretimi
            self.update_status("🎨 Painting unique cover artwork via AI...")
            cover_prompt = self.album_data.get("cover_prompt", "Abstract art digital cover")
            self.generated_image = self.image_service.generate_cover(cover_prompt, genre, era)

            # Sonuçları ekrana bas
            self.root.after(0, self.display_results)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Pipeline Error", f"Processing failed:\n{str(e)}"))
            self.update_status("❌ Generation failed due to an error.")
        finally:
            self.root.after(0, lambda: self.btn_generate.config(state=tk.NORMAL))

    def display_results(self):
        """Gelen verileri ekrana basan Spotify Mockup çizim motoru"""
        self.lbl_album_title.config(text=self.album_data.get('album_name', 'Fictional Album Title'))
        self.lbl_artist_sub.config(text=f"by {self.album_data.get('artist_name', 'Fictional Artist')}")

        details = f"{self.album_data.get('year', 'N/A')}  •  {len(self.tracklist)} songs  •  {self.album_data.get('label', 'Fictional Records')}"
        self.lbl_details_sub.config(text=details)

        self.txt_mood_desc.config(state=tk.NORMAL)
        self.txt_mood_desc.delete("1.0", tk.END)
        self.txt_mood_desc.insert(tk.END, f"AI Logic: {self.album_data.get('mood_description', '')}")
        self.txt_mood_desc.config(state=tk.DISABLED)

        # REQUIREMENT 6: PIL nesnesini Tkinter resmine dönüştürme ve boyutlandırma
        resized_img = self.generated_image.resize((220, 220), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(resized_img)
        self.lbl_cover.config(image=self.tk_img, text="")

        # Eski şarkı listesi satırlarını temizle
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # REQUIREMENT 7: Şarkı listesinin Spotify satır stiliyle doldurulması
        for idx, track in enumerate(self.tracklist, start=1):
            track_row = tk.Frame(self.scrollable_frame, bg="#121212", pady=4)
            track_row.pack(fill=tk.X, expand=True, padx=5)

            # Spotify satır içi Hover efekti
            def on_enter(e, row=track_row): row.config(bg="#1A1A1A")
            def on_leave(e, row=track_row): row.config(bg="#121212")

            lbl_num = tk.Label(track_row, text=f"{idx:<3}", bg="#121212", fg="#777777", font=("Helvetica", 10, "bold"), width=4, anchor="w")
            lbl_num.pack(side=tk.LEFT, padx=(15, 0))

            track_text = f"{track.get('name')}  —  {track.get('artist')}"
            lbl_track = tk.Label(track_row, text=track_text, bg="#121212", fg="#FFFFFF", font=("Helvetica", 10), anchor="w")
            lbl_track.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

            track_row.bind("<Enter>", on_enter)
            track_row.bind("<Leave>", on_leave)
            lbl_num.bind("<Enter>", on_enter)
            lbl_track.bind("<Enter>", on_enter)

            # REQUIREMENT 7 & 1: Varsayılan tarayıcıda Last.fm URL'sini açan buton
            url = track.get("url")
            btn_listen = tk.Button(
                track_row, text="▶ LISTEN", bg="#121212", fg="#1DB954", font=("Helvetica", 9, "bold"),
                relief=tk.FLAT, activebackground="#1DB954", activeforeground="white", bd=0, cursor="hand2",
                command=lambda u=url: webbrowser.open(u) if u else None
            )
            btn_listen.pack(side=tk.RIGHT, padx=25, ipadx=10, ipady=4)

        self.update_status("Ready")
        self.btn_export.config(state=tk.NORMAL)

    def export_album_data(self):
        """REQUIREMENT 8: Klasör seçme penceresi ve kaydetme çağrısı"""
        if not self.album_data or not self.generated_image:
            return

        folder_selected = filedialog.askdirectory(title="Select Destination Folder for Export")
        if folder_selected:
            try:
                # Arkadaşının yazdığı utils modülünü güvenle çağırıyoruz
                ExportUtils.save_album(self.album_data, self.tracklist, self.generated_image, folder_selected)
                messagebox.showinfo("Export Success", f"All fictional assets and metadata successfully saved to:\n{folder_selected}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not export assets:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AlbumCoverStudioApp(root)
    root.mainloop()
