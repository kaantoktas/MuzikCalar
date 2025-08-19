from pydub import AudioSegment
from pydub.playback import play
import os
import tempfile

class AudioProcessor:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.temp_files = [] 

    def _get_temp_filepath(self, original_filename, suffix):
       
        name, ext = os.path.splitext(os.path.basename(original_filename))
        temp_filepath = os.path.join(self.temp_dir, f"{name}_{suffix}{ext}")
        self.temp_files.append(temp_filepath)
        return temp_filepath

    def apply_bass_boost(self, input_filepath, output_filepath=None, gain_db=6):
        """
        
        .
        gain_db: Bas frekanslarına uygulanacak desibel cinsinden kazanç.
        """
        try:
            audio = AudioSegment.from_file(input_filepath)
            
    
            bass_boosted_audio = audio.low_pass_filter(100).apply_gain(gain_db) + audio.high_pass_filter(100)

            if output_filepath is None:
                output_filepath = self._get_temp_filepath(input_filepath, "bass_boosted")
            
            bass_boosted_audio.export(output_filepath, format=audio.detect_format())
            print(f"Bas güçlendirme uygulandı ve kaydedildi: {output_filepath}")
            return output_filepath
        except Exception as e:
            print(f"Bas güçlendirme uygulanırken hata oluştu: {e}")
            return None

    def apply_treble_boost(self, input_filepath, output_filepath=None, gain_db=6):
        """
        Sese tiz güçlendirme efekti uygular.
        input_filepath: Giriş ses dosyasının yolu.
        output_filepath: Çıkış ses dosyasının kaydedileceği yol. None ise geçici dosya oluşturulur.
        gain_db: Tiz frekanslarına uygulanacak desibel cinsinden kazanç.
        """
        try:
            audio = AudioSegment.from_file(input_filepath)
            
          
            treble_boosted_audio = audio.high_pass_filter(2000).apply_gain(gain_db) + audio.low_pass_filter(2000)

            if output_filepath is None:
                output_filepath = self._get_temp_filepath(input_filepath, "treble_boosted")
            
            treble_boosted_audio.export(output_filepath, format=audio.detect_format())
            print(f"Tiz güçlendirme uygulandı ve kaydedildi: {output_filepath}")
            return output_filepath
        except Exception as e:
            print(f"Tiz güçlendirme uygulanırken hata oluştu: {e}")
            return None

    def reset_audio(self, input_filepath, output_filepath=None):
        """
        Sesi orijinal haline döndürür (efektleri kaldırır).
        Aslında sadece orijinal dosyayı yeniden döndürür veya kopyalar.
        """
        if output_filepath is None:
            output_filepath = self._get_temp_filepath(input_filepath, "original")
        
        try:
            audio = AudioSegment.from_file(input_filepath)
            audio.export(output_filepath, format=audio.detect_format())
            print(f"Ses orijinal haline döndürüldü: {output_filepath}")
            return output_filepath
        except Exception as e:
            print(f"Ses orijinal haline döndürülürken hata oluştu: {e}")
            return None

    def clean_temp_files(self):
        """
        Oluşturulan tüm geçici ses dosyalarını siler.
        """
        for filepath in self.temp_files:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"Geçici dosya silindi: {filepath}")
            except Exception as e:
                print(f"Geçici dosya silinirken hata: {filepath} - {e}")
        self.temp_files = [] 

if __name__ == "__main__":
    
    processor = AudioProcessor()
    test_song_path = os.path.join("songs", "test_song.mp3") 

    if os.path.exists(test_song_path):
        print(f"'{test_song_path}' dosyası bulunamadı. Lütfen songs/ klasörüne bir test şarkısı koyun.")
    else:
        print(f"'{test_song_path}' kullanarak ses işlemciyi test ediyorum.")
        
        bass_boosted_path = processor.apply_bass_boost(test_song_path)
        if bass_boosted_path:
            print(f"Bas güçlendirilmiş şarkı kaydedildi: {bass_boosted_path}")
     
        treble_boosted_path = processor.apply_treble_boost(test_song_path)
        if treble_boosted_path:
            print(f"Tiz güçlendirilmiş şarkı kaydedildi: {treble_boosted_path}")
            
        processor.clean_temp_files()
        print("Test tamamlandı. Geçici dosyalar temizlendi.")

