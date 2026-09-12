import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# load the dataset — 2200 rows of soil/weather conditions mapped to crop labels
df = pd.read_csv("data/crop_recommendation.csv")

# split features from the target label
X = df.drop("label", axis=1)
y = df["label"]

# hold back 20% of data for testing so we can see how well the model actually does
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# train a Random Forest — works great out of the box for this kind of classification
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# save the model to disk so recommender.py can load it without retraining every time
joblib.dump(model, "crop_model.pkl")

# quick check — how accurate is it on data it hasn't seen before?
accuracy = model.score(X_test, y_test)
print("Accuracy:", accuracy)