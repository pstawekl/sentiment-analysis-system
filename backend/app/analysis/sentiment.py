"""
Moduł analizy sentymentu przy użyciu LLaMA 3.2:1b przez Ollama i Pandas.
Zawiera funkcje EDA oraz klasyfikację sentymentu.
"""

import pandas as pd
import numpy as np
import asyncio
from typing import Dict, List, Tuple
from collections import Counter

from .preprocessing import preprocess_text
from .ollama_client import ollama_client


async def analyze_sentiment_async(text: str, use_cache: bool = True) -> Dict[str, float]:
    """
    Analizuje sentyment pojedynczego tekstu przy użyciu LLaMA przez Ollama.
    Async wersja z cache'owaniem.
    
    Args:
        text: Tekst do analizy
        use_cache: Czy używać cache
    
    Returns:
        Słownik z polarity (-1 do 1), subjectivity (0 do 1) i label
    """
    if not isinstance(text, str) or len(text.strip()) == 0:
        return {"polarity": 0.0, "subjectivity": 0.0, "label": "negative"}
    
    result = await ollama_client.analyze_sentiment(text, use_cache=use_cache)
    return result


def analyze_sentiment(text: str) -> Dict[str, float]:
    """
    Analizuje sentyment pojedynczego tekstu (synchroniczna wersja wrapper).
    Używa Ollama przez async wrapper dla kompatybilności wstecznej.
    
    Args:
        text: Tekst do analizy
    
    Returns:
        Słownik z polarity (-1 do 1) i subjectivity (0 do 1)
    """
    if not isinstance(text, str) or len(text.strip()) == 0:
        return {"polarity": 0.0, "subjectivity": 0.0}
    
    # Użyj asyncio.run dla synchronicznego wrapper
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Jeśli loop już działa, użyj run_until_complete w nowym executor
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, ollama_client.analyze_sentiment(text))
                result = future.result()
        else:
            result = loop.run_until_complete(ollama_client.analyze_sentiment(text))
    except RuntimeError:
        # Jeśli nie ma loop, utwórz nowy
        result = asyncio.run(ollama_client.analyze_sentiment(text))
    
    # Zwróć tylko polarity i subjectivity dla kompatybilności
    return {
        "polarity": result.get("polarity", 0.0),
        "subjectivity": result.get("subjectivity", 0.0)
    }


def classify_sentiment(polarity: float) -> str:
    """
    Klasyfikuje sentyment na podstawie polarity.
    
    Args:
        polarity: Wartość polarity (-1 do 1)
    
    Returns:
        'positive' jeśli polarity > 0, w przeciwnym razie 'negative'
    """
    return "positive" if polarity > 0 else "negative"


def perform_eda(df: pd.DataFrame) -> Dict:
    """
    Wykonuje eksploracyjną analizę danych (EDA) przy użyciu Pandas.
    Wykorzystuje wymagane funkcje: str.contains(), apply(), value_counts().
    
    Args:
        df: DataFrame z opiniami (musi mieć kolumnę 'review_text')
    
    Returns:
        Słownik ze statystykami EDA
    """
    if 'review_text' not in df.columns:
        raise ValueError("DataFrame musi zawierać kolumnę 'review_text'")
    
    # Liczba opinii
    total_reviews = len(df)
    
    # Długość opinii przy użyciu apply()
    df['review_length'] = df['review_text'].apply(lambda x: len(str(x)))
    df['word_count'] = df['review_text'].apply(lambda x: len(str(x).split()))
    
    # Statystyki długości
    avg_length = df['review_length'].mean()
    avg_word_count = df['word_count'].mean()
    
    # Jeśli polarity już istnieje w DataFrame (z analyze_batch), użyj go
    # W przeciwnym razie oblicz używając analyze_sentiment
    if 'polarity' not in df.columns:
        # Analiza sentymentu przy użyciu apply()
        sentiment_results = df['review_text'].apply(lambda x: analyze_sentiment(str(x))['polarity'])
        df['polarity'] = sentiment_results
    
    # Klasyfikacja przy użyciu apply()
    if 'sentiment_label' not in df.columns:
        df['sentiment_label'] = df['polarity'].apply(classify_sentiment)
    
    # Rozkład sentymentu przy użyciu value_counts()
    sentiment_counts = df['sentiment_label'].value_counts()
    positive_count = sentiment_counts.get('positive', 0)
    negative_count = sentiment_counts.get('negative', 0)
    
    # Filtrowanie przy użyciu str.contains() - przykłady użycia
    # Opinie zawierające słowo "excellent"
    excellent_reviews = df[df['review_text'].str.contains('excellent', case=False, na=False)]
    excellent_count = len(excellent_reviews)
    
    # Opinie zawierające słowo "terrible"
    terrible_reviews = df[df['review_text'].str.contains('terrible', case=False, na=False)]
    terrible_count = len(terrible_reviews)
    
    # Statystyki
    eda_results = {
        "total_reviews": total_reviews,
        "average_review_length": float(avg_length),
        "average_word_count": float(avg_word_count),
        "positive_count": int(positive_count),
        "negative_count": int(negative_count),
        "positive_percentage": float((positive_count / total_reviews) * 100) if total_reviews > 0 else 0.0,
        "negative_percentage": float((negative_count / total_reviews) * 100) if total_reviews > 0 else 0.0,
        "average_polarity": float(df['polarity'].mean()),
        "excellent_mentions": int(excellent_count),
        "terrible_mentions": int(terrible_count),
        "min_polarity": float(df['polarity'].min()),
        "max_polarity": float(df['polarity'].max()),
    }
    
    return eda_results, df


def get_top_words(df: pd.DataFrame, limit: int = 20, remove_stopwords: bool = True) -> List[Dict[str, int]]:
    """
    Zwraca najczęściej występujące słowa przy użyciu value_counts() i nlargest().
    
    Args:
        df: DataFrame z opiniami (musi mieć kolumnę 'review_text')
        limit: Liczba TOP słów do zwrócenia
        remove_stopwords: Czy usuwać stopwords
    
    Returns:
        Lista słowników z kluczami 'word' i 'count'
    """
    if 'review_text' not in df.columns:
        raise ValueError("DataFrame musi zawierać kolumnę 'review_text'")
    
    # Połącz wszystkie opinie i przetwórz
    all_words = []
    for text in df['review_text']:
        if pd.notna(text):
            tokens = preprocess_text(str(text), remove_stop=remove_stopwords)
            all_words.extend(tokens)
    
    # Utwórz Series z wszystkimi słowami i użyj value_counts()
    words_series = pd.Series(all_words)
    word_counts = words_series.value_counts()
    
    # Użyj nlargest() do pobrania TOP N słów
    top_words = word_counts.nlargest(limit)
    
    # Konwersja do listy słowników
    result = [{"word": word, "count": int(count)} for word, count in top_words.items()]
    
    return result


async def analyze_batch_async(df: pd.DataFrame, concurrent_limit: int = 5) -> pd.DataFrame:
    """
    Analizuje cały batch opinii asynchronicznie przy użyciu Ollama.
    Używa asyncio.gather() dla równoległych zapytań.
    
    Args:
        df: DataFrame z opiniami (musi mieć kolumnę 'review_text')
        concurrent_limit: Maksymalna liczba równoległych zapytań
    
    Returns:
        DataFrame z dodanymi kolumnami: polarity, sentiment_label, word_count
    """
    if 'review_text' not in df.columns:
        raise ValueError("DataFrame musi zawierać kolumnę 'review_text'")
    
    texts = df['review_text'].tolist()
    
    # Funkcja do analizy pojedynczego tekstu
    async def analyze_single(text: str) -> float:
        result = await ollama_client.analyze_sentiment(str(text), use_cache=True)
        return result.get("polarity", 0.0)
    
    # Batch processing z limitem równoległych zapytań
    semaphore = asyncio.Semaphore(concurrent_limit)
    
    async def analyze_with_limit(text: str) -> float:
        async with semaphore:
            return await analyze_single(text)
    
    # Wykonaj wszystkie zapytania równolegle
    tasks = [analyze_with_limit(text) for text in texts]
    polarities = await asyncio.gather(*tasks)
    
    # Dodaj wyniki do DataFrame
    df['polarity'] = polarities
    
    # Klasyfikacja przy użyciu apply()
    df['sentiment_label'] = df['polarity'].apply(classify_sentiment)
    
    # Liczba słów przy użyciu apply()
    df['word_count'] = df['review_text'].apply(lambda x: len(str(x).split()))
    
    return df


def analyze_batch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analizuje cały batch opinii i dodaje kolumny z wynikami (synchroniczna wersja).
    Używa async wrapper dla kompatybilności wstecznej.
    
    Args:
        df: DataFrame z opiniami (musi mieć kolumnę 'review_text')
    
    Returns:
        DataFrame z dodanymi kolumnami: polarity, sentiment_label, word_count
    """
    from ..config import BATCH_CONCURRENT_LIMIT
    
    if 'review_text' not in df.columns:
        raise ValueError("DataFrame musi zawierać kolumnę 'review_text'")
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Jeśli loop już działa, użyj run_in_executor
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    analyze_batch_async(df, BATCH_CONCURRENT_LIMIT)
                )
                return future.result()
        else:
            return loop.run_until_complete(analyze_batch_async(df, BATCH_CONCURRENT_LIMIT))
    except RuntimeError:
        # Jeśli nie ma loop, utwórz nowy
        return asyncio.run(analyze_batch_async(df, BATCH_CONCURRENT_LIMIT))


def get_average_polarity(df: pd.DataFrame) -> float:
    """
    Oblicza średnią polaryzację wszystkich opinii.
    
    Args:
        df: DataFrame z kolumną 'polarity' lub 'review_text'
    
    Returns:
        Średnia polaryzacja
    """
    if 'polarity' in df.columns:
        return float(df['polarity'].mean())
    elif 'review_text' in df.columns:
        # Oblicz polarity jeśli nie istnieje
        polarities = df['review_text'].apply(lambda x: analyze_sentiment(str(x))['polarity'])
        return float(polarities.mean())
    else:
        raise ValueError("DataFrame musi zawierać kolumnę 'polarity' lub 'review_text'")


if __name__ == "__main__":
    # Test funkcji
    from ..data.loader import load_data, clean_data
    
    try:
        df = load_data()
        df = clean_data(df)
        
        print("Wykonywanie EDA...")
        eda_results, df_analyzed = perform_eda(df)
        print("\nStatystyki EDA:")
        for key, value in eda_results.items():
            print(f"  {key}: {value}")
        
        print("\nTOP 10 słów:")
        top_words = get_top_words(df_analyzed, limit=10)
        for word_data in top_words:
            print(f"  {word_data['word']}: {word_data['count']}")
        
        print(f"\nŚrednia polaryzacja: {get_average_polarity(df_analyzed):.4f}")
        
    except Exception as e:
        print(f"Błąd: {e}")

