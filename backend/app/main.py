"""
Główna aplikacja FastAPI - REST API do analizy sentymentu opinii.
"""

from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .analysis.ollama_client import ollama_client
from .analysis.sentiment import (analyze_batch, analyze_batch_async,
                                 analyze_sentiment, analyze_sentiment_async,
                                 classify_sentiment, get_average_polarity,
                                 get_top_words, perform_eda)
from .data.loader import clean_data, load_data
from .models import (AveragePolarityResponse, HealthResponse, ReviewInput,
                     SentimentResponse, StatisticsResponse, TopWordsResponse)

# Inicjalizacja FastAPI
app = FastAPI(
    title="Sentiment Analysis API",
    description="API do analizy sentymentu opinii klientów",
    version="1.0.0"
)

# Konfiguracja CORS dla frontendu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "http://localhost:3000"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globalne zmienne do cache'owania danych
cached_df: Optional[pd.DataFrame] = None
eda_stats: Optional[dict] = None


async def load_and_analyze_data():
    """Wczytuje i analizuje dane przy starcie aplikacji (async)."""
    global cached_df, eda_stats

    try:
        print("Wczytywanie danych...")
        df = load_data()
        df = clean_data(df)

        print("Wykonywanie analizy sentymentu z Ollama...")
        # Użyj async analyze_batch dla równoległych zapytań do Ollama
        df_analyzed = await analyze_batch_async(df)

        print("Wykonywanie EDA...")
        eda_results, df_final = perform_eda(df_analyzed)

        cached_df = df_final
        eda_stats = eda_results

        print(f"Przygotowano {len(cached_df)} opinii do analizy")
        return True
    except Exception as e:
        print(f"Błąd podczas wczytywania danych: {e}")
        import traceback
        traceback.print_exc()
        return False


# Event handler - wczytaj dane przy starcie
@app.on_event("startup")
async def startup_event():
    """Wczytuje dane przy starcie aplikacji."""
    # Sprawdź health Ollama
    ollama_available = await ollama_client.health_check()
    if ollama_available:
        print("✓ Ollama jest dostępny i działa")
    else:
        print("⚠ UWAGA: Ollama nie jest dostępny, używam TextBlob jako fallback")

    success = await load_and_analyze_data()
    if not success:
        print("UWAGA: Aplikacja uruchomiona bez danych. Uruchom: python scripts/download_data.py")


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")


@app.get("/api/health/ollama")
async def health_check_ollama():
    """
    Health check endpoint dla Ollama.
    Sprawdza czy Ollama jest dostępny i działa.
    """
    try:
        is_available = await ollama_client.health_check()
        if is_available:
            return {
                "status": "ok",
                "ollama_available": True,
                "model": ollama_client.model,
                "base_url": ollama_client.base_url
            }
        else:
            return {
                "status": "degraded",
                "ollama_available": False,
                "message": "Ollama nie jest dostępny, używany jest TextBlob jako fallback"
            }
    except Exception as e:
        return {
            "status": "error",
            "ollama_available": False,
            "error": str(e)
        }


@app.get("/api/stats", response_model=StatisticsResponse)
async def get_statistics():
    """
    Zwraca statystyki ogólne dotyczące analizowanych opinii.
    Wykorzystuje cache'owane dane z EDA.
    """
    if cached_df is None or eda_stats is None:
        # Próba ponownego wczytania danych
        if not await load_and_analyze_data():
            raise HTTPException(
                status_code=503,
                detail="Dane nie zostały załadowane. Uruchom: python scripts/download_data.py"
            )

    return StatisticsResponse(
        total_reviews=eda_stats["total_reviews"],
        positive_count=eda_stats["positive_count"],
        negative_count=eda_stats["negative_count"],
        positive_percentage=eda_stats["positive_percentage"],
        negative_percentage=eda_stats["negative_percentage"],
        average_polarity=eda_stats["average_polarity"],
        average_review_length=eda_stats["average_review_length"],
        average_word_count=eda_stats["average_word_count"]
    )


@app.get("/api/polarity/average", response_model=AveragePolarityResponse)
async def get_average_polarity_endpoint():
    """
    Zwraca średnią polaryzację wszystkich opinii.
    """
    if cached_df is None:
        if not await load_and_analyze_data():
            raise HTTPException(
                status_code=503,
                detail="Dane nie zostały załadowane. Uruchom: python scripts/download_data.py"
            )

    avg_polarity = get_average_polarity(cached_df)
    return AveragePolarityResponse(average_polarity=avg_polarity)


@app.get("/api/words/top", response_model=TopWordsResponse)
async def get_top_words_endpoint(limit: int = Query(20, ge=1, le=100, description="Liczba słów do zwrócenia")):
    """
    Zwraca najczęściej występujące słowa w opiniach.

    Args:
        limit: Liczba TOP słów do zwrócenia (1-100)
    """
    if cached_df is None:
        if not await load_and_analyze_data():
            raise HTTPException(
                status_code=503,
                detail="Dane nie zostały załadowane. Uruchom: python scripts/download_data.py"
            )

    top_words = get_top_words(cached_df, limit=limit)

    # Oblicz całkowitą liczbę słów
    total_words = sum(word_data["count"] for word_data in top_words)

    return TopWordsResponse(
        words=top_words,
        total_words_analyzed=total_words
    )


@app.post("/api/analyze", response_model=SentimentResponse)
async def analyze_single_review(review_input: ReviewInput):
    """
    Analizuje pojedynczą opinię i zwraca wynik sentymentu.
    Używa LLaMA przez Ollama dla analizy.

    Args:
        review_input: Model z tekstem opinii
    """
    if not review_input.review_text or len(review_input.review_text.strip()) == 0:
        raise HTTPException(
            status_code=400, detail="Tekst opinii nie może być pusty")

    try:
        # Analiza sentymentu przy użyciu async Ollama
        sentiment_result = await analyze_sentiment_async(review_input.review_text, use_cache=True)
        polarity = sentiment_result.get("polarity", 0.0)
        sentiment_label = sentiment_result.get(
            "label", classify_sentiment(polarity))
    except Exception as e:
        # Fallback do synchronicznej wersji
        print(f"Błąd podczas async analizy, używam fallback: {e}")
        sentiment_result = analyze_sentiment(review_input.review_text)
        polarity = sentiment_result["polarity"]
        sentiment_label = classify_sentiment(polarity)

    # Liczba słów
    word_count = len(review_input.review_text.split())

    return SentimentResponse(
        polarity=polarity,
        sentiment_label=sentiment_label,
        word_count=word_count
    )


# Endpoint do ręcznego przeładowania danych (dla developmentu)
@app.post("/api/reload")
async def reload_data():
    """
    Endpoint do ręcznego przeładowania danych (tylko dla developmentu).
    """
    success = await load_and_analyze_data()
    if success:
        from ..utils.cache import sentiment_cache
        cache_stats = sentiment_cache.get_stats()
        return {
            "status": "success",
            "message": f"Zaladowano {len(cached_df)} opinii",
            "cache_stats": cache_stats
        }
    else:
        raise HTTPException(
            status_code=500, detail="Błąd podczas wczytywania danych")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
