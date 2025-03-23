from transformers import pipeline

# Load sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

# Test with different sentences
print(sentiment_pipeline("i want to kill myself. LOL!"))
