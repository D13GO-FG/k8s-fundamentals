import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import os

MODEL_PATH = "model.joblib"


class IrisModel:
    def __init__(self):
        self.model = None
        self.class_names = None

    def train(self):
        print("Training model...")
        iris = load_iris()
        X = iris.data
        y = iris.target
        self.class_names = iris.target_names

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model = LogisticRegression(max_iter=200)
        self.model.fit(X_train, y_train)

        # Save model and class names
        joblib.dump({"model": self.model, "class_names": self.class_names}, MODEL_PATH)
        print("Model trained and saved.")

    def load(self):
        if os.path.exists(MODEL_PATH):
            print("Loading model...")
            data = joblib.load(MODEL_PATH)
            self.model = data["model"]
            self.class_names = data["class_names"]
            print("Model loaded.")
        else:
            self.train()

    def predict(self, input_data: list):
        if not self.model:
            self.load()

        prediction = self.model.predict([input_data])[0]
        probability = self.model.predict_proba([input_data])[0][prediction]

        return self.class_names[prediction], probability


model_instance = IrisModel()
