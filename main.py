from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import os

app = FastAPI()

# Input data model
class WaterIntakeInput(BaseModel):
    Age: int
    Gender: str
    Weight: float
    ActivityLevel: str
    Weather: str

# Load the model
MODEL_PATH = "water_intake_model.pkl"
model = None

if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
else:
    print(f"Warning: Model file '{MODEL_PATH}' not found. Using mock prediction.")

@app.get("/")
def read_root():
    return {"message": "Water Intake Prediction API"}

@app.post("/predict")
def predict_water_intake(data: WaterIntakeInput):
    # Encoding map
    gender_map = {'Male': 1, 'Female': 0}
    activity_map = {'Low': 0, 'Moderate': 1, 'High': 2}
    weather_map = {'Cool': 0, 'Moderate': 1, 'Hot': 2}

    try:
        # Preprocess input
        encoded_data = {
            'Age': data.Age,
            'Gender': gender_map.get(data.Gender),
            'Weight (kg)': data.Weight, # Note: Column name might need to match model training exactly
            'Physical Activity Level': activity_map.get(data.ActivityLevel),
            'Weather': weather_map.get(data.Weather)
        }

        # Check for invalid inputs
        if None in encoded_data.values():
             raise HTTPException(status_code=400, detail="Invalid input values for categorical fields.")

        # Create DataFrame for model input (ensuring order)
        input_df = pd.DataFrame([encoded_data])
        
        # Ensure column order matches the model training
        # 'Age', 'Gender', 'Weight (kg)', 'Physical Activity Level', 'Weather'
        input_df = input_df[['Age', 'Gender', 'Weight (kg)', 'Physical Activity Level', 'Weather']]

        if model:
            prediction = model.predict(input_df)[0]
        else:
            # Mock prediction logic if model is missing
            # Simple heuristic: weight * 0.03 + activity_bonus + weather_bonus
            base = data.Weight * 0.03
            act_bonus = encoded_data['Physical Activity Level'] * 0.5
            weather_bonus = encoded_data['Weather'] * 0.3
            prediction = base + act_bonus + weather_bonus

        return {"daily_water_intake_liters": round(prediction, 2)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
