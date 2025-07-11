from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import random

import sqlite3

def get_best_match(current_user_id: int) -> int | None:
    with sqlite3.connect("data/database.db") as db:
        cursor = db.cursor()
        
        # Получаем анкету текущего пользователя
        cursor.execute("SELECT about FROM users WHERE id = ?", (current_user_id,))
        current_about = cursor.fetchone()
        if not current_about or not current_about[0].strip():
            return None

        current_about = current_about[0]

        # Получаем всех других пользователей
        cursor.execute("SELECT id, about FROM users WHERE id != ? AND about IS NOT NULL", (current_user_id,))
        users = cursor.fetchall()

    if not users:
        return None

    id_to_about = {uid: about for uid, about in users if about and about.strip()}

    if not id_to_about:
        return None

    # TF-IDF
    vectorizer = TfidfVectorizer(analyzer='word', token_pattern=r'\b\w+\b')
    all_texts = [current_about] + list(id_to_about.values())
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

    # Сопоставим с ID
    user_ids = list(id_to_about.keys())
    scored_users = list(zip(user_ids, similarity))
    scored_users.sort(key=lambda x: x[1], reverse=True)

    best_score = scored_users[0][1] if scored_users else 0
    best_user_id = scored_users[0][0] if scored_users else None

    if best_score < 0.1:
        # Низкое сходство — лучше вернуть случайную анкету
        return None

    return best_user_id