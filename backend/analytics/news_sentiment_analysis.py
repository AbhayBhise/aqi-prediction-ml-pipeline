import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from textblob import TextBlob
import sys

# Ensure NLTK data is downloaded
def download_resources():
    print("[NLP] Downloading NLTK resources...")
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger_eng')
    nltk.download('punkt_tab')

def process_aqi_news(headlines):
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    
    results = []
    
    for text in headlines:
        print(f"\n--- Processing: {text} ---")
        
        # 1. Tokenization
        tokens = word_tokenize(text)
        print(f"Tokens: {tokens}")
        
        # 2. Stop-word Removal
        filtered_tokens = [w for w in tokens if not w.lower() in stop_words and w.isalnum()]
        print(f"Filtered (No Stop-words): {filtered_tokens}")
        
        # 3. Stemming
        stemmed_tokens = [stemmer.stem(w) for w in filtered_tokens]
        print(f"Stemmed: {stemmed_tokens}")
        
        # 4. Part of Speech (POS) Tagging
        pos_tags = nltk.pos_tag(tokens)
        print(f"POS Tags: {pos_tags[:5]}...") # Showing first 5
        
        # 5. Sentiment Analysis (Predictive Analytics Application)
        analysis = TextBlob(text)
        sentiment = "Positive" if analysis.sentiment.polarity > 0 else "Negative" if analysis.sentiment.polarity < 0 else "Neutral"
        print(f"Sentiment: {sentiment} (Polarity: {analysis.sentiment.polarity:.2f})")
        
        results.append({
            "original": text,
            "sentiment": sentiment,
            "polarity": analysis.sentiment.polarity
        })
    
    return results

if __name__ == "__main__":
    download_resources()
    
    sample_headlines = [
        "Dangerous levels of PM2.5 detected in Delhi, residents advised to stay indoors.",
        "Air quality improves significantly after seasonal rainfall in Mumbai.",
        "Government announces new strict policies to curb industrial pollution emissions.",
        "Smog levels reach record highs as winter sets in over northern India.",
        "Innovative air purifiers showing great results in reducing indoor allergens."
    ]
    
    print("\n" + "="*50)
    print("AQI NEWS SENTIMENT & NLP PROCESSOR")
    print("="*50)
    
    process_aqi_news(sample_headlines)
