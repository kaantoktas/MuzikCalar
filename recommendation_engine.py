
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os

class RecommendationEngine:
    def __init__(self, song_data_path="song_data.json"):
        self.song_data_path = song_data_path
        self.df = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self._load_and_process_data()

    def _load_and_process_data(self):
        if not os.path.exists(self.song_data_path):
            print(f"Hata: Şarkı veri dosyası bulunamadı: {self.song_data_path}")
            self.df = pd.DataFrame() 
            return

        try:
            with open(self.song_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.df = pd.DataFrame(data)

            required_cols = ['title', 'artist', 'genre', 'keywords']
            if not all(col in self.df.columns for col in required_cols):
                print(f"Uyarı: '{self.song_data_path}' dosyasında eksik sütunlar var. "
                      f"Gerekli sütunlar: {required_cols}")
                self.df = pd.DataFrame()
                return

            self.df['combined_features'] = self.df.apply(
                lambda row: ' '.join([
                    row['genre'].lower().replace(" ", ""),
                    row['artist'].lower().replace(" ", "")] + 
                    [kw.lower().replace(" ", "") for kw in row['keywords']]
                ),
                axis=1
            )

            self.tfidf_vectorizer = TfidfVectorizer(stop_words='english') 
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.df['combined_features'])
            print("Öneri motoru verileri başarıyla yüklendi ve işlendi.")

        except Exception as e:
            print(f"Şarkı verileri yüklenirken veya işlenirken hata oluştu: {e}")
            self.df = pd.DataFrame()

    def get_song_recommendations(self, user_song_title, num_recommendations=5):
       
        if self.df.empty:
            print("Öneri yapılamıyor: Şarkı verileri yüklenemedi veya boş.")
            return []

        user_song_index = self.df[self.df['title'].str.lower() == user_song_title.lower()].index
        
        if user_song_index.empty:
            print(f"Üzgünüm, '{user_song_title}' isimli şarkı veritabanımızda bulunamadı.")
            return []
        
        user_song_index = user_song_index[0]

        user_song_vector = self.tfidf_matrix[user_song_index]

        cosine_sim = cosine_similarity(user_song_vector, self.tfidf_matrix)

        sim_scores = list(enumerate(cosine_sim[0]))
        sim_scores = [s for s in sim_scores if s[0] != user_song_index] 

        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        recommended_indices = [i[0] for i in sim_scores[:num_recommendations]]

        return self.df['title'].iloc[recommended_indices].tolist()

if __name__ == "__main__":
    recommender = RecommendationEngine()
    
    if not recommender.df.empty:
        print("\nÖrnek öneri:")
        recommendations = recommender.get_song_recommendations("Ateşböceği")
        if recommendations:
            print("Ateşböceği'ne benzer şarkılar:")
            for i, song in enumerate(recommendations):
                print(f"{i+1}. {song}")
        else:
            print("Öneri bulunamadı.")
    else:
        print("Öneri motoru başlatılamadı, lütfen song_data.json dosyasını kontrol edin.")

