"""
Moduł do preprocessing tekstu przy użyciu NLTK.
Zawiera funkcje tokenizacji, usuwania stopwords i normalizacji.
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from typing import List

# Pobierz wymagane dane NLTK przy pierwszym imporcie
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


def get_stopwords(language: str = 'english') -> set:
    """
    Pobiera listę stopwords dla danego języka.
    
    Args:
        language: Kod języka ('english', 'polish' itp.)
    
    Returns:
        Zbiór stopwords
    """
    try:
        return set(stopwords.words(language))
    except LookupError:
        # Domyślnie angielski
        return set(stopwords.words('english'))


def normalize_text(text: str) -> str:
    """
    Normalizuje tekst: lowercase, usunięcie znaków specjalnych.
    
    Args:
        text: Tekst do normalizacji
    
    Returns:
        Znormalizowany tekst
    """
    if not isinstance(text, str):
        return ""
    
    # Konwersja na małe litery
    text = text.lower()
    
    # Usunięcie znaków specjalnych (zachowaj litery, cyfry, spacje)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    # Usunięcie nadmiarowych białych znaków
    text = ' '.join(text.split())
    
    return text


def tokenize_text(text: str) -> List[str]:
    """
    Tokenizuje tekst przy użyciu NLTK word_tokenize.
    
    Args:
        text: Tekst do tokenizacji
    
    Returns:
        Lista tokenów (słów)
    """
    if not isinstance(text, str) or len(text.strip()) == 0:
        return []
    
    try:
        tokens = word_tokenize(text)
        # Filtruj puste tokeny
        tokens = [token for token in tokens if token.strip()]
        return tokens
    except Exception as e:
        print(f"Błąd podczas tokenizacji: {e}")
        return []


def remove_stopwords(tokens: List[str], language: str = 'english') -> List[str]:
    """
    Usuwa stopwords z listy tokenów.
    
    Args:
        tokens: Lista tokenów
        language: Język stopwords
    
    Returns:
        Lista tokenów bez stopwords
    """
    stop_words = get_stopwords(language)
    filtered_tokens = [token for token in tokens if token.lower() not in stop_words]
    return filtered_tokens


def preprocess_text(text: str, remove_stop: bool = True, language: str = 'english') -> List[str]:
    """
    Kompletny preprocessing tekstu: normalizacja, tokenizacja, usuwanie stopwords.
    
    Args:
        text: Tekst do przetworzenia
        remove_stop: Czy usuwać stopwords
        language: Język dla stopwords
    
    Returns:
        Lista przetworzonych tokenów
    """
    # Krok 1: Normalizacja
    normalized = normalize_text(text)
    
    # Krok 2: Tokenizacja
    tokens = tokenize_text(normalized)
    
    # Krok 3: Usunięcie stopwords (jeśli wymagane)
    if remove_stop:
        tokens = remove_stopwords(tokens, language)
    
    # Filtruj bardzo krótkie tokeny (mniej niż 2 znaki)
    tokens = [token for token in tokens if len(token) >= 2]
    
    return tokens


def preprocess_text_to_string(text: str, remove_stop: bool = True, language: str = 'english') -> str:
    """
    Preprocessing tekstu z zwróceniem jako string (użyteczne dla niektórych analiz).
    
    Args:
        text: Tekst do przetworzenia
        remove_stop: Czy usuwać stopwords
        language: Język dla stopwords
    
    Returns:
        Przetworzony tekst jako string
    """
    tokens = preprocess_text(text, remove_stop, language)
    return ' '.join(tokens)


if __name__ == "__main__":
    # Test preprocessing
    test_text = "This product is absolutely amazing! I love it so much. Best purchase ever."
    print(f"Oryginalny tekst: {test_text}")
    
    tokens = preprocess_text(test_text)
    print(f"Tokeny po preprocessing: {tokens}")
    
    processed_string = preprocess_text_to_string(test_text)
    print(f"Tekst po preprocessing: {processed_string}")

