import hashlib
from textblob import TextBlob

def generate_token(order_id):
    return hashlib.md5(str(order_id).encode()).hexdigest()

def check_sentiment(text):
    return TextBlob(text).sentiment.polarity

def calculate_trust(sentiment, rating, ml_result):
    score = 50

    if sentiment > 0 and rating >= 3:
        score += 20
    elif sentiment < 0 and rating <= 2:
        score += 20
    else:
        score -= 10

    if ml_result == "Genuine":
        score += 20
    else:
        score -= 15

    return max(10, min(score, 100))