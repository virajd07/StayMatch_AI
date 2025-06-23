from textblob import TextBlob

def get_sentiment_score(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    label = "POSITIVE" if polarity >= 0 else "NEGATIVE"
    return label, round(abs(polarity), 2)
