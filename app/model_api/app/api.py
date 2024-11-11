from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from app.model import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

app = FastAPI()

model = load_model()

MAX_LENGTH = 100

class InputData(BaseModel):
    words: list
    features: list

@app.post("/predict")
async def predict(data: InputData):
    try:
        words_padded = pad_sequences([data.words], maxlen=MAX_LENGTH, padding='post')
        features_padded = pad_sequences([data.features], maxlen=MAX_LENGTH, padding='post')

        prediction = model.predict([words_padded, features_padded])
        predicted_class = np.argmax(prediction, axis=-1)

        return {"prediction": int(predicted_class[0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))