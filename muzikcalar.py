
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pygame.mixer
import os
import json
from recommendation_engine import RecommendationEngine
from audio_processor import AudioProcessor
import threading
import time

class MusicPlayerApp:
    def __init__(self, master):
        self.master = master
        master.title("Kaan Müzik Çalar")
        master.geometry("800x650") 
        master.resizable(False, False) 

        pygame.mixer.init()

        self.audio_processor = AudioProcessor()
        self.recommender = RecommendationEngine() 
        self.current_playlist = []
        self.current_song_index = -1
        self.is_playing = False
        self.is_paused = False


        self.playlist_frame = tk.LabelFrame(master, text="Çalma Listesi", padx=10, pady=10)
        self.playlist_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.playlist_scrollbar = tk.Scrollbar(self.playlist_frame)
        self.playlist_scrollbar.pack(side="right", fill="y")

        self.playlist_box = tk.Listbox(self.playlist_frame, bg="white", fg="blue", selectbackground="lightblue", selectforeground="black",
                                      yscrollcommand=self.playlist_scrollbar.set, height=15)
        self.playlist_box.pack(fill="both", expand=True)
        self.playlist_scrollbar.config(command=self.playlist_box.yview)

        self.playlist_box.bind("<Double-Button-1>", self.play_selected_song)

        self.controls_frame = tk.Frame(master, padx=10, pady=10)
        self.controls_frame.pack(pady=5)

        self.play_img = tk.PhotoImage(file="icons/play.png") 
        self.pause_img = tk.PhotoImage(file="icons/pause.png")
        self.stop_img = tk.PhotoImage(file="icons/stop.png")
        self.next_img = tk.PhotoImage(file="icons/next.png")
        self.prev_img = tk.PhotoImage(file="icons/prev.png")

        self.prev_button = tk.Button(self.controls_frame, text="Önceki", command=self.play_previous, image=self.prev_img, compound=tk.LEFT)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.play_button = tk.Button(self.controls_frame, text="Çal", command=self.play_song, image=self.play_img, compound=tk.LEFT)
        self.play_button.grid(row=0, column=1, padx=5)

        self.pause_button = tk.Button(self.controls_frame, text="Duraklat", command=self.pause_song, image=self.pause_img, compound=tk.LEFT)
        self.pause_button.grid(row=0, column=2, padx=5)

        self.stop_button = tk.Button(self.controls_frame, text="Durdur", command=self.stop_song, image=self.stop_img, compound=tk.LEFT)
        self.stop_button.grid(row=0, column=3, padx=5)

        self.next_button = tk.Button(self.controls_frame, text="Sonraki", command=self.play_next, image=self.next_img, compound=tk.LEFT)
        self.next_button.grid(row=0, column=4, padx=5)
        
        self.volume_label = tk.Label(master, text="Ses Seviyesi:")
        self.volume_label.pack()
        self.volume_slider = ttk.Scale(master, from_=0, to=1, orient="horizontal", command=self.set_volume)
        self.volume_slider.set(0.5) 
        pygame.mixer.music.set_volume(0.5)
        self.volume_slider.pack(pady=5, padx=20, fill="x")

        self.now_playing_label = tk.Label(master, text="Şu An Çalan: Yok", bd=1, relief="sunken", anchor="w")
        self.now_playing_label.pack(fill="x", padx=10, pady=5)

        self.menu_bar = tk.Menu(master)
        master.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Dosya", menu=self.file_menu)
        self.file_menu.add_command(label="Klasörden Şarkı Yükle", command=self.load_songs_from_folder)
        self.file_menu.add_command(label="Çalma Listesini Kaydet", command=self.save_playlist)
        self.file_menu.add_command(label="Çalma Listesini Yükle", command=self.load_playlist)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Çıkış", command=self.on_closing)

        self.eq_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Ekolayzır", menu=self.eq_menu)
        self.eq_menu.add_command(label="Normal", command=lambda: self.apply_eq_preset("normal"))
        self.eq_menu.add_command(label="Bas Güçlendirme", command=lambda: self.apply_eq_preset("bass_boost"))
        self.eq_menu.add_command(label="Tiz Güçlendirme", command=lambda: self.apply_eq_preset("treble_boost"))

        self.recommendation_frame = tk.LabelFrame(master, text="Şarkı Önerileri", padx=10, pady=10)
        self.recommendation_frame.pack(pady=10, padx=10, fill="x")

        self.rec_label = tk.Label(self.recommendation_frame, text="Favori bir şarkı girin:")
        self.rec_label.pack(side="left", padx=5)
        self.rec_entry = tk.Entry(self.recommendation_frame, width=30)
        self.rec_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.rec_button = tk.Button(self.recommendation_frame, text="Öneri Al", command=self.get_recommendations)
        self.rec_button.pack(side="left", padx=5)

        self.rec_results_text = tk.Text(master, height=5, wrap="word", state="disabled")
        self.rec_results_text.pack(pady=5, padx=10, fill="x")

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.check_song_end_event()

    def set_volume(self, val):
       
        pygame.mixer.music.set_volume(float(val))

    def load_songs_from_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.current_playlist = []
            self.playlist_box.delete(0, tk.END) 

            supported_formats = (".mp3", ".wav", ".ogg")
            for root, _, files in os.walk(folder_selected):
                for file in files:
                    if file.lower().endswith(supported_formats):
                        filepath = os.path.join(root, file)
                        self.current_playlist.append(filepath)
                        self.playlist_box.insert(tk.END, os.path.basename(filepath))
            
            if self.current_playlist:
                messagebox.showinfo("Yükleme Tamamlandı", f"{len(self.current_playlist)} adet şarkı yüklendi.")
                self.current_song_index = -1 
            else:
                messagebox.showwarning("Uyarı", "Seçilen klasörde desteklenen formatta şarkı bulunamadı.")

    def play_song(self):
        if not self.current_playlist:
            messagebox.showwarning("Uyarı", "Lütfen önce bir çalma listesi yükleyin.")
            return

        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.is_paused = False
            self.now_playing_label.config(text=f"Şu An Çalan: {os.path.basename(self.current_playlist[self.current_song_index])}")
        elif not self.is_playing:
            if self.current_song_index == -1 and self.current_playlist:
                self.current_song_index = 0 
            
            if self.current_song_index != -1:
                self._load_and_play_song(self.current_playlist[self.current_song_index])
                self.is_playing = True
                self.is_paused = False
                self.playlist_box.selection_clear(0, tk.END)
                self.playlist_box.selection_set(self.current_song_index)
                self.playlist_box.see(self.current_song_index)
            else:
                messagebox.showwarning("Uyarı", "Çalma listesinde çalacak şarkı yok.")


    def _load_and_play_song(self, filepath):
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            self.now_playing_label.config(text=f"Şu An Çalan: {os.path.basename(filepath)}")
        except pygame.error as e:
            messagebox.showerror("Çalma Hatası", f"Şarkı çalınamadı: {os.path.basename(filepath)}\n{e}")
            self.stop_song() 
        except Exception as e:
            messagebox.showerror("Hata", f"Beklenmedik bir hata oluştu: {e}")
            self.stop_song()

    def play_selected_song(self, event=None):
        if not self.playlist_box.curselection():
            return
        self.current_song_index = self.playlist_box.curselection()[0]
        self._load_and_play_song(self.current_playlist[self.current_song_index])
        self.is_playing = True
        self.is_paused = False

    def pause_song(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.is_playing = False
            self.now_playing_label.config(text=f"Şu An Çalan: {os.path.basename(self.current_playlist[self.current_song_index])} (Duraklatıldı)")
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.is_paused = False
            self.now_playing_label.config(text=f"Şu An Çalan: {os.path.basename(self.current_playlist[self.current_song_index])}")


    def stop_song(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.now_playing_label.config(text="Şu An Çalan: Yok")
        self.audio_processor.clean_temp_files() 

    def play_next(self):
        if not self.current_playlist:
            return
        self.current_song_index = (self.current_song_index + 1) % len(self.current_playlist)
        self._load_and_play_song(self.current_playlist[self.current_song_index])
        self.is_playing = True
        self.is_paused = False
        self.playlist_box.selection_clear(0, tk.END)
        self.playlist_box.selection_set(self.current_song_index)
        self.playlist_box.see(self.current_song_index)

    def play_previous(self):
        if not self.current_playlist:
            return
        self.current_song_index = (self.current_song_index - 1 + len(self.current_playlist)) % len(self.current_playlist)
        self._load_and_play_song(self.current_playlist[self.current_song_index])
        self.is_playing = True
        self.is_paused = False
        self.playlist_box.selection_clear(0, tk.END)
        self.playlist_box.selection_set(self.current_song_index)
        self.playlist_box.see(self.current_song_index)

    def check_song_end_event(self):
        if self.is_playing and not pygame.mixer.music.get_busy() and not self.is_paused:
            self.play_next()
        self.master.after(1000, self.check_song_end_event) 

    def save_playlist(self):
        if not self.current_playlist:
            messagebox.showwarning("Uyarı", "Kaydedilecek bir çalma listesi yok.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Dosyaları", "*.json"), ("Tüm Dosyalar", "*.*")],
                                                 initialdir="./playlists")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_playlist, f, indent=4)
                messagebox.showinfo("Kaydedildi", "Çalma listesi başarıyla kaydedildi.")
            except Exception as e:
                messagebox.showerror("Hata", f"Çalma listesi kaydedilirken hata oluştu: {e}")

    def load_playlist(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON Dosyaları", "*.json"), ("Tüm Dosyalar", "*.*")],
                                               initialdir="./playlists") 
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_playlist = json.load(f)
                
                valid_songs = [s for s in loaded_playlist if os.path.exists(s)]
                
                if not valid_songs:
                    messagebox.showwarning("Uyarı", "Yüklenen çalma listesinde geçerli şarkı bulunamadı veya dosyalar mevcut değil.")
                    return

                self.current_playlist = valid_songs
                self.playlist_box.delete(0, tk.END)
                for song_path in self.current_playlist:
                    self.playlist_box.insert(tk.END, os.path.basename(song_path))
                
                messagebox.showinfo("Yüklendi", "Çalma listesi başarıyla yüklendi.")
                self.current_song_index = -1
                self.stop_song() 

            except Exception as e:
                messagebox.showerror("Hata", f"Çalma listesi yüklenirken hata oluştu: {e}")

    def apply_eq_preset(self, preset_name):
        if not self.current_playlist or self.current_song_index == -1:
            messagebox.showwarning("Uyarı", "Lütfen önce çalacak bir şarkı seçin veya bir şarkı çalın.")
            return

        current_filepath = self.current_playlist[self.current_song_index]
        modified_filepath = None

        messagebox.showinfo("Ekolayzır", f"{preset_name.replace('_', ' ').capitalize()} efekti uygulanıyor...")
        self.stop_song() 

        if preset_name == "normal":
            modified_filepath = self.audio_processor.reset_audio(current_filepath)
        elif preset_name == "bass_boost":
            modified_filepath = self.audio_processor.apply_bass_boost(current_filepath)
        elif preset_name == "treble_boost":
            modified_filepath = self.audio_processor.apply_treble_boost(current_filepath)
        
        if modified_filepath:
            self.current_playlist[self.current_song_index] = modified_filepath
            self._load_and_play_song(modified_filepath)
            self.is_playing = True
            self.is_paused = False
            messagebox.showinfo("Ekolayzır", "Efekt başarıyla uygulandı!")
        else:
            messagebox.showerror("Ekolayzır Hatası", "Efekt uygulanırken bir sorun oluştu.")
        

    def get_recommendations(self):
        user_fav_song = self.rec_entry.get().strip()
        if not user_fav_song:
            messagebox.showwarning("Uyarı", "Lütfen öneri almak için bir şarkı adı girin.")
            return

        if self.recommender.df.empty:
            messagebox.showwarning("Uyarı", "Öneri verileri yüklenemedi. Lütfen 'song_data.json' dosyasını kontrol edin.")
            return
            
        recommendations = self.recommender.get_song_recommendations(user_fav_song, num_recommendations=5)
        
        self.rec_results_text.config(state="normal") 
        self.rec_results_text.delete(1.0, tk.END) 

        if recommendations:
            self.rec_results_text.insert(tk.END, f"'{user_fav_song}' şarkısına benzer öneriler:\n")
            for i, song in enumerate(recommendations):
                self.rec_results_text.insert(tk.END, f"{i+1}. {song}\n")
        else:
            self.rec_results_text.insert(tk.END, "Öneri bulunamadı veya girilen şarkı veritabanında yok.")
        
        self.rec_results_text.config(state="disabled") 

    def on_closing(self):
        """Uygulama kapatıldığında kaynakları temizler."""
        if messagebox.askokcancel("Çıkış", "Uygulamadan çıkmak istediğinizden emin misiniz?"):
            self.stop_song() 
            pygame.mixer.quit() 
            self.audio_processor.clean_temp_files() 
            self.master.destroy() 

if __name__ == "__main__":
    #

    root = tk.Tk()
    app = MusicPlayerApp(root)
    root.mainloop()


