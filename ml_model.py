from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob

reviews = ["good product", "bad quality", "excellent", "worst item"]
labels = [1, 0, 1, 0]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(reviews)

model = LogisticRegression()
model.fit(X, labels)


def predict_review(text):
    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    return "Genuine" if pred == 1 else "Fake"


def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"


def check_review_genuinity(new_review_text, existing_reviews, rating):
    sentiment_result = analyze_sentiment(new_review_text)
    mismatch = False
    if (sentiment_result == "Positive" and rating <= 2) or (sentiment_result == "Negative" and rating >= 4):
        mismatch = True
    texts = [new_review_text] + [r['review_text'] for r in existing_reviews]
    if len(texts) <= 1:
        similarity_score = 0
    else:
        tfidf = TfidfVectorizer().fit_transform(texts)
        similarity_values = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        similarity_score = max(similarity_values) if len(similarity_values) > 0 else 0
    if mismatch or similarity_score > 0.8:
        return "Possibly Fake"
    return "Genuine"


def check_image_text_consistency(text, image_url):
    if not image_url:
        return "No Image"
    keywords = ['photo', 'image', 'picture', 'camera', 'shown', 'depicted']
    for kw in keywords:
        if kw in text.lower():
            return "Consistent"
    return "Image Mentioned" if any(kw in text.lower() for kw in ['photo', 'image', 'picture']) else "Not Mentioned"