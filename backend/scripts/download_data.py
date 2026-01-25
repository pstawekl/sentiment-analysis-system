"""
Skrypt do pobierania danych z publicznego źródła.
Generuje przykładowy dataset opinii klientów.
"""

import pandas as pd
import os
from pathlib import Path

# Przykładowe opinie pozytywne i negatywne
POSITIVE_REVIEWS = [
    "This product is absolutely amazing! I love it so much. Best purchase ever.",
    "Excellent quality and fast shipping. Highly recommend to everyone.",
    "Great value for money. The product exceeded my expectations completely.",
    "Wonderful experience! The customer service was outstanding and helpful.",
    "Perfect product! Exactly as described. Very satisfied with my purchase.",
    "Fantastic quality! I will definitely buy from this seller again.",
    "Amazing product at an affordable price. Really happy with this buy.",
    "Top notch quality and excellent packaging. Exceeded all expectations.",
    "Outstanding product! The quality is superb and delivery was quick.",
    "Love this product! It's exactly what I was looking for. Highly recommended.",
    "Great product with excellent features. Worth every penny spent.",
    "Excellent! The product works perfectly and looks beautiful.",
    "Very satisfied! Fast delivery and product is exactly as advertised.",
    "Amazing quality! This is a must-have item. Completely satisfied.",
    "Perfect! Great value for money and excellent customer service.",
]

NEGATIVE_REVIEWS = [
    "Terrible product! It broke after just one use. Very disappointed.",
    "Poor quality and slow shipping. Would not recommend to anyone.",
    "Waste of money. The product doesn't work as described at all.",
    "Horrible experience. The item arrived damaged and unusable.",
    "Very disappointed! The quality is much worse than expected.",
    "Bad product! It stopped working after a few days. Do not buy.",
    "Not worth the money. Poor quality and terrible customer service.",
    "Awful product! It doesn't match the description at all.",
    "Extremely disappointed. The item was broken when it arrived.",
    "Terrible quality! I regret buying this product completely.",
    "Poor value for money. The product is cheaply made and unreliable.",
    "Bad experience overall. The product failed to meet expectations.",
    "Very poor quality. I would not recommend this to anyone.",
    "Disappointed with the purchase. The product is defective.",
    "Worst product ever! Complete waste of money and time.",
]


def generate_sample_dataset(num_reviews=100):
    """
    Generuje przykładowy dataset opinii.
    
    Args:
        num_reviews: Liczba opinii do wygenerowania
    
    Returns:
        pandas.DataFrame z kolumnami: review_text, rating, review_id
    """
    import random
    
    reviews = []
    review_id = 1
    
    # Generuj mieszankę opinii pozytywnych i negatywnych
    for i in range(num_reviews):
        # 60% pozytywnych, 40% negatywnych (realistyczny rozkład)
        if random.random() < 0.6:
            review_text = random.choice(POSITIVE_REVIEWS)
            rating = random.randint(4, 5)
            sentiment = "positive"
        else:
            review_text = random.choice(NEGATIVE_REVIEWS)
            rating = random.randint(1, 2)
            sentiment = "negative"
        
        reviews.append({
            "review_id": review_id,
            "review_text": review_text,
            "rating": rating,
            "sentiment": sentiment
        })
        review_id += 1
    
    df = pd.DataFrame(reviews)
    return df


def download_imdb_data():
    """
    Alternatywna funkcja do pobrania danych z IMDb.
    Wymaga połączenia z internetem i odpowiednich bibliotek.
    """
    print("Pobieranie danych z IMDb...")
    print("UWAGA: Ta funkcja wymaga zewnętrznych bibliotek i dostępu do internetu.")
    print("Dla projektu offline używamy wygenerowanych danych przykładowych.")
    return None


def main():
    """Główna funkcja do pobierania/generowania danych."""
    # Ścieżka do katalogu z danymi
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    output_file = data_dir / "dataset.csv"
    
    print("Generowanie przykładowego datasetu opinii...")
    df = generate_sample_dataset(num_reviews=200)
    
    # Zapisz do CSV
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Dataset zapisany do: {output_file}")
    print(f"Liczba opinii: {len(df)}")
    print(f"Pozytywnych: {len(df[df['sentiment'] == 'positive'])}")
    print(f"Negatywnych: {len(df[df['sentiment'] == 'negative'])}")
    
    return output_file


if __name__ == "__main__":
    main()

