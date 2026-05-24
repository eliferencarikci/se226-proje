import io
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from urllib.parse import quote
import webbrowser

from gemini_service import GeminiService
from image_service import ImageService
from lastfm_service import LastFMService
from PIL import Image, ImageTk
import requests
from utils import ExportUtils



GEMINI_API_KEY = "AIzaSyCNDPBDgzdBJomnKpviN7YlCMRzIbvU18w"
LASTFM_API_KEY = "965e178b0dd41faa21c2033be695943a"


class AlbumCoverStudioApp:

    def __init__(self, root):
        self.root = root


        self.root.title("PDA-226 Album Cover Studio")
        self.root.geometry("1350x780")
        self.root.configure(bg="#121212")


        self.album_data = None
        self.tracklist = None
        self.generated_image = None


        self.gemini_service = GeminiService(GEMINI_API_KEY)
        self.lastfm_service = LastFMService(LASTFM_API_KEY)
        self.image_service = ImageService()


        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()


        self.create_left_panel()
        self.create_right_panel()
        self.create_status_bar()

    def configure_styles(self):

        self.style.configure(
            "TLabel", background="#121212", foreground="white", font=("Arial", 10)
        )
        self.style.configure(
            "Panel.TLabel", background="#181818", foreground="white", font=("Arial", 10)
        )
        self.style.configure(
            "Header.TLabel",
            background="#181818",
            foreground="#1DB954",
            font=("Arial", 14, "bold"),
        )


        self.style.configure(
            "TCombobox", fieldbackground="#2A2A2A", background="#181818", foreground="white"
        )
        self.style.configure(
            "TSpinbox", fieldbackground="#2A2A2A", background="#181818", foreground="white"
        )


        self.style.configure(
            "Spotify.TButton",
            background="#1DB954",
            foreground="white",
            font=("Arial", 11, "bold"),
            borderwidth=0,
        )
        self.style.map("Spotify.TButton", background=[("active", "#1ED760")])


        self.style.configure(
            "Secondary.TButton",
            background="#282828",
            foreground="white",
            font=("Arial", 10),
            borderwidth=0,
        )
        self.style.map("Secondary.TButton", background=[("active", "#3E3E3E")])

        self.style.configure(
            "Listen.TButton",
            background="#181818",
            foreground="#1DB954",
            font=("Arial", 9, "bold"),
        )

    def create_left_panel(self):

        self.left_frame = tk.Frame(self.root, bg="#181818", width=420)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)
        self.left_frame.pack_propagate(False)


        lbl_title = ttk.Label(
            self.left_frame, text="Album Cover Studio", style="Header.TLabel"
        )
        lbl_title.pack(anchor=tk.W, padx=15, pady=15)


        lbl_journal = ttk.Label(
            self.left_frame,
            text="Describe your mood, enjoy the generated tracklist:",
            style="Panel.TLabel",
        )
        lbl_journal.pack(anchor=tk.W, padx=15, pady=5)

        self.txt_journal = tk.Text(
            self.left_frame,
            height=8,
            bg="#2A2A2A",
            fg="white",
            insertbackground="white",
            relief=tk.FLAT,
            font=("Arial", 10),
            wrap=tk.WORD,
        )
        self.txt_journal.pack(fill=tk.X, padx=15, pady=5)
        # Varsayılan Sensible Default Değer (Requirement 3)
        self.txt_journal.insert(
            tk.END,
            "I was looking at the sea in Izmir. It was raining softly, and an old song was playing through my headphones. I felt both peaceful and melancholic.",
        )


        lbl_genre = ttk.Label(self.left_frame, text="Genre:", style="Panel.TLabel")
        lbl_genre.pack(anchor=tk.W, padx=15, pady=5)

        genres = [
            "Pop", "Rock", "Hip-Hop / Rap", "Electronic", "Indie",
            "R&B / Soul", "Jazz", "Metal", "Türk Pop", "Klasik"
        ]
        self.cb_genre = ttk.Combobox(self.left_frame, values=genres, state="readonly")
        self.cb_genre.pack(fill=tk.X, padx=15, pady=5)
        self.cb_genre.set("Indie")  # Default


        lbl_era = ttk.Label(self.left_frame, text="Era:", style="Panel.TLabel")
        lbl_era.pack(anchor=tk.W, padx=15, pady=5)

        eras = ["1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]
        self.cb_era = ttk.Combobox(self.left_frame, values=eras, state="readonly")
        self.cb_era.pack(fill=tk.X, padx=15, pady=5)
        self.cb_era.set("2000s")  # Default


        lbl_tracks = ttk.Label(self.left_frame, text="Track Count (6-14):", style="Panel.TLabel")
        lbl_tracks.pack(anchor=tk.W, padx=15, pady=5)

        self.spin_tracks = ttk.Spinbox(self.left_frame, from_=6, to=14, state="readonly")
        self.spin_tracks.pack(anchor=tk.W, padx=15, pady=5)
        self.spin_tracks.set(10)  # Default


        self.btn_generate = ttk.Button(
            self.left_frame,
            text="Generate Album",
            style="Spotify.TButton",
            command=self.start_generation_thread,
        )
        self.btn_generate.pack(fill=tk.X, padx=15, pady=25)


        self.btn_export = ttk.Button(
            self.left_frame,
            text="Save Album (JSON + PNG)",
            style="Secondary.TButton",
            command=self.export_album_data,
            state=tk.DISABLED,
        )
        self.btn_export.pack(fill=tk.X, padx=15, pady=5)

    def create_right_panel(self):

        self.right_frame = tk.Frame(self.root, bg="#121212")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)


        self.upper_right = tk.Frame(self.right_frame, bg="#121212")
        self.upper_right.pack(fill=tk.X, pady=10, anchor=tk.W)


        self.cover_frame = tk.Frame(self.upper_right, bg="#181818", width=250, height=250)
        self.cover_frame.pack(side=tk.LEFT, padx=10, pady=5)
        self.cover_frame.pack_propagate(False)


        self.lbl_cover = tk.Label(
            self.cover_frame,
            text="No Cover Art\nGenerated",
            bg="#181818",
            fg="gray",
            font=("Arial", 10, "italic"),
        )
        self.lbl_cover.pack(fill=tk.BOTH, expand=True)

        # Sanatçı ve Albüm Bilgileri Metin Alanı
        self.txt_meta = tk.Text(
            self.upper_right,
            bg="#121212",
            fg="white",
            relief=tk.FLAT,
            font=("Arial", 11),
            height=12,
            wrap=tk.WORD,
        )
        self.txt_meta.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15)
        self.txt_meta.insert(tk.END, "Fictional album details will appear here after generation...")
        self.txt_meta.config(state=tk.DISABLED)

        # Alt Kısım: Şarkı Listesi Başlığı
        lbl_tracklist_title = ttk.Label(
            self.right_frame, text="GENERATED TRACKLIST (REAL SONGS)", style="TLabel"
        )
        lbl_tracklist_title.pack(anchor=tk.W, padx=10, pady=10)

        # Şarkı Listesi İçin Scrollable Ana Çerçeve
        self.tracklist_container = tk.Frame(self.right_frame, bg="#121212")
        self.tracklist_container.pack(fill=tk.BOTH, expand=True, padx=10)

        self.canvas = tk.Canvas(self.tracklist_container, bg="#121212", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self.tracklist_container, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg="#121212")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def create_status_bar(self):

        self.lbl_status = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#181818",
            fg="white",
            font=("Arial", 9),
            padx=10,
        )
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, text):
        self.lbl_status.config(text=text)
        self.root.update_idletasks()

    def start_generation_thread(self):

        threading.Thread(target=self.generate_album_process, daemon=True).start()

    def generate_album_process(self):

        self.btn_generate.config(state=tk.DISABLED)
        self.btn_export.config(state=tk.DISABLED)

        journal = self.txt_journal.get("1.0", tk.END).strip()
        genre = self.cb_genre.get()
        era = self.cb_era.get()
        track_count = int(self.spin_tracks.get())

        try:

            self.update_status("Gemini is thinking...")
            self.album_data = self.gemini_service.generate_album_data(
                journal, genre, era, track_count
            )


            self.update_status("Fetching tracks...")
            tags = self.album_data.get("lastfm_tags", [genre])
            self.tracklist = self.lastfm_service.build_tracklist(tags, track_count)


            self.update_status("Generating cover...")
            cover_prompt = self.album_data.get("cover_prompt", "Abstract art")

            self.generated_image = self.image_service.generate_cover(cover_prompt, genre, era=era)

            self.root.after(0, self.display_results)

        except Exception as e:
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Error Occurred", f"Failed to complete generation:\n{str(e)}"
                ),
            )
            self.root.after(0, lambda: self.update_status("Generation failed."))
        finally:
            self.root.after(0, lambda: self.btn_generate.config(state=tk.NORMAL))

    def display_results(self):

        self.txt_meta.config(state=tk.NORMAL)
        self.txt_meta.delete("1.0", tk.END)

        meta_text = (
            f"ALBUM (FICTIONAL CONCEPT):\n\n"
            f"💿 Title: {self.album_data.get('album_name', 'Unknown')}\n"
            f"🎤 Artist: {self.album_data.get('artist_name', 'Unknown')}\n"
            f"📅 Release Year: {self.album_data.get('year', 'N/A')} | 🏷️ Label: {self.album_data.get('label', 'N/A')}\n\n"
            f"💬 Vibe Description:\n\"{self.album_data.get('mood_description', 'N/A')}\"\n\n"
            f"🎨 Visual Prompt:\n\"{self.album_data.get('cover_prompt', 'N/A')}\""
        )
        self.txt_meta.insert(tk.END, meta_text)
        self.txt_meta.config(state=tk.DISABLED)


        bio_img = self.generated_image.resize((250, 250), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(bio_img)
        self.lbl_cover.config(image=self.tk_img, text="")


        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for idx, track in enumerate(self.tracklist, start=1):
            track_row = tk.Frame(self.scrollable_frame, bg="#121212", pady=4)
            track_row.pack(fill=tk.X, expand=True)


            track_info = f"{idx}.  {track.get('name')}  —  {track.get('artist')}"
            lbl_track = tk.Label(
                track_row,
                text=track_info,
                bg="#121212",
                fg="#B3B3B3",
                font=("Arial", 10),
                anchor=tk.W,
            )
            lbl_track.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)


            url = track.get("url")
            btn_listen = ttk.Button(
                track_row,
                text="Listen",
                style="Listen.TButton",
                command=lambda u=url: webbrowser.open(u) if u else None,
            )
            btn_listen.pack(side=tk.RIGHT, padx=15)

        self.update_status("Ready")
        self.btn_export.config(state=tk.NORMAL)

    def export_album_data(self):
        if not self.album_data or not self.generated_image:
            return

        folder_selected = filedialog.askdirectory()
        if folder_selected:
            try:
                ExportUtils.save_album(
                    self.album_data,
                    self.tracklist,
                    self.generated_image,
                    folder_selected,
                )
                messagebox.showinfo(
                    "Success", f"Album assets successfully saved to:\n{folder_selected}"
                )
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not save files:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AlbumCoverStudioApp(root)
    root.mainloop()



