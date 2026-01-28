/**
 * Typy TypeScript dla aplikacji frontendowej.
 */

export interface Statistics {
  total_reviews: number;
  positive_count: number;
  negative_count: number;
  positive_percentage: number;
  negative_percentage: number;
  average_polarity: number;
  average_review_length: number;
  average_word_count: number;
}

export interface WordCount {
  word: string;
  count: number;
}

export interface TopWords {
  words: WordCount[];
  total_words_analyzed: number;
}

export interface SentimentAnalysis {
  polarity: number;
  sentiment_label: 'positive' | 'negative';
  word_count: number;
}

export interface AveragePolarity {
  average_polarity: number;
}

export interface ReviewItem {
  index: number;
  review_id?: number;
  review_text: string;
  polarity: number;
  sentiment_label: 'positive' | 'negative';
  word_count: number;
  review_length?: number;
}

