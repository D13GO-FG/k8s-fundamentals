from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.schemas import PredictionInput, PredictionOutput
from backend.model import model_instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    model_instance.load()
    yield
    # Clean up the ML models and release the resources
    pass


app = FastAPI(title="Iris ML API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Iris ML API. Use /predict to get predictions."}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionOutput)
def predict(input_data: PredictionInput):
    features = [
        input_data.sepal_length,
        input_data.sepal_width,
        input_data.petal_length,
        input_data.petal_width,
    ]

    class_name, probability = model_instance.predict(features)

    return PredictionOutput(class_name=class_name, probability=probability)
