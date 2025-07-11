import sqlite3
import random
import numpy as np
import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


logger = logging.getLogger(__name__)



def get_best_match(current_user_id: int) -> int | None:
    """Находит наиболее подходящую анкету по схожести описания"""
    try:
        with sqlite3.connect("data/database.db") as db:
            cursor = db.cursor()
        
            # Получение описания текущего пользователя
            cursor.execute("SELECT about FROM users WHERE id = ?", (current_user_id,))
            current_about_row = cursor.fetchone()

            if not current_about_row or not current_about_row[0].strip():
                return None

            current_about = current_about_row[0]

            # Получение описаний других пользователей
            cursor.execute("""
                SELECT id, about FROM users 
                WHERE id != ? AND about IS NOT NULL
            """, (current_user_id,))
            users = cursor.fetchall()

        if not users:
            return None

        # Сопоставляем ID и текст
        id_to_about = {uid: about for uid, about in users if about and about.strip()}


        # Формируем матрицу TF-IDF
        all_texts = [current_about] + list(id_to_about.values())
        vectorizer = TfidfVectorizer(analyzer='word', token_pattern=r'\b\w+\b')
        tfidf_matrix = vectorizer.fit_transform(all_texts)


        # Вычисляем косинусное сходство
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]


        # Сопоставление ID и сходства
        user_ids = list(id_to_about.keys())
        scored_users = list(zip(user_ids, similarity))
        scored_users.sort(key=lambda x: x[1], reverse=True)


        best_score = scored_users[0][1] if scored_users else 0
        best_user_id = scored_users[0][0] if scored_users else None

        return best_user_id if best_score >= 0.1 else None
    
    except Exception as e:
        logger.error(f"Ошибка при поиске совпадения: {e}")