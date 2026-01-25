"""
Modele Pydantic dla API - definicje danych wejściowych i wyjściowych.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ReviewInput(BaseModel):
    """Model wejściowy dla analizy pojedynczej opinii."""
    review_text: str = Field(..., description="Tekst opinii do analizy", min_length=1)


class SentimentResponse(BaseModel):
    """Model odpowiedzi z wynikiem analizy sentymentu pojedynczej opinii."""
    polarity: float = Field(..., description="Polaryzacja sentymentu (-1 do 1)")
    sentiment_label: str = Field(..., description="Etykieta sentymentu: 'positive' lub 'negative'")
    word_count: int = Field(..., description="Liczba słów w opinii")


class WordCount(BaseModel):
    """Model pojedynczego słowa z liczbą wystąpień."""
    word: str = Field(..., description="Słowo")
    count: int = Field(..., description="Liczba wystąpień")


class StatisticsResponse(BaseModel):
    """Model odpowiedzi ze statystykami ogólnymi."""
    total_reviews: int = Field(..., description="Całkowita liczba opinii")
    positive_count: int = Field(..., description="Liczba opinii pozytywnych")
    negative_count: int = Field(..., description="Liczba opinii negatywnych")
    positive_percentage: float = Field(..., description="Procent opinii pozytywnych")
    negative_percentage: float = Field(..., description="Procent opinii negatywnych")
    average_polarity: float = Field(..., description="Średnia polaryzacja")
    average_review_length: float = Field(..., description="Średnia długość opinii (znaki)")
    average_word_count: float = Field(..., description="Średnia liczba słów w opinii")


class AveragePolarityResponse(BaseModel):
    """Model odpowiedzi ze średnią polaryzacją."""
    average_polarity: float = Field(..., description="Średnia polaryzacja wszystkich opinii")


class TopWordsResponse(BaseModel):
    """Model odpowiedzi z listą TOP słów."""
    words: List[WordCount] = Field(..., description="Lista najczęściej występujących słów")
    total_words_analyzed: int = Field(..., description="Całkowita liczba przeanalizowanych słów")


class HealthResponse(BaseModel):
    """Model odpowiedzi dla health check."""
    status: str = Field(default="ok", description="Status serwera")

