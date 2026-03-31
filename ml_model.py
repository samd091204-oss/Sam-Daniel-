from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

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