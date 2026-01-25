"""
Moduł do wczytywania i czyszczenia danych przy użyciu Pandas.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional


def load_data(file_path: Optional[str] = None) -> pd.DataFrame:
    """
    Wczytuje dane z pliku CSV przy użyciu Pandas.
    
    Args:
        file_path: Ścieżka do pliku CSV. Jeśli None, używa domyślnej ścieżki.
    
    Returns:
        pandas.DataFrame z danymi opinii
    """
    if file_path is None:
        # Domyślna ścieżka względna do katalogu data
        base_dir = Path(__file__).parent.parent.parent
        file_path = base_dir / "data" / "dataset.csv"
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"Wczytano {len(df)} opinii z pliku: {file_path}")
        return df
    except FileNotFoundError:
        print(f"Błąd: Plik {file_path} nie został znaleziony.")
        print("Uruchom najpierw: python scripts/download_data.py")
        raise
    except Exception as e:
        print(f"Błąd podczas wczytywania danych: {e}")
        raise


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Czyści dane: usuwa braki danych i duplikaty.
    Używa Pandas dropna() do usunięcia brakujących wartości.
    
    Args:
        df: DataFrame z danymi
    
    Returns:
        Oczyszczony DataFrame
    """
    original_len = len(df)
    
    # Usuń wiersze z brakującymi wartościami w kolumnie review_text
    df_cleaned = df.dropna(subset=['review_text'])
    
    # Usuń duplikaty
    df_cleaned = df_cleaned.drop_duplicates(subset=['review_text'])
    
    # Usuń puste opinie (po strip)
    df_cleaned = df_cleaned[df_cleaned['review_text'].str.strip() != '']
    
    removed = original_len - len(df_cleaned)
    if removed > 0:
        print(f"Usunięto {removed} wierszy (braki danych i duplikaty)")
    
    print(f"Pozostało {len(df_cleaned)} opinii po czyszczeniu")
    return df_cleaned.reset_index(drop=True)


def preprocess_text_basic(text: str) -> str:
    """
    Podstawowe czyszczenie tekstu (bez użycia NLTK).
    Używane w loader.py przed bardziej zaawansowanym preprocessingiem.
    
    Args:
        text: Tekst do czyszczenia
    
    Returns:
        Oczyszczony tekst
    """
    if not isinstance(text, str):
        return ""
    
    # Konwersja na małe litery
    text = text.lower()
    
    # Usunięcie nadmiarowych białych znaków
    text = ' '.join(text.split())
    
    return text


def get_dataframe_info(df: pd.DataFrame) -> dict:
    """
    Zwraca podstawowe informacje o DataFrame.
    
    Args:
        df: DataFrame do analizy
    
    Returns:
        Słownik z informacjami
    """
    info = {
        "total_rows": len(df),
        "columns": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "dtypes": df.dtypes.to_dict()
    }
    return info


# Test funkcji (jeśli uruchomiony bezpośrednio)
if __name__ == "__main__":
    # Test wczytywania danych
    try:
        df = load_data()
        print("\nPierwsze 5 wierszy:")
        print(df.head())
        
        df_cleaned = clean_data(df)
        print(f"\nDataFrame po czyszczeniu:")
        print(df_cleaned.info())
    except Exception as e:
        print(f"Błąd: {e}")

