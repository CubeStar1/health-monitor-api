# File: health_data_api.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from datetime import datetime, timedelta
import math
import random


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
class HealthData(BaseModel):
    average_heart_rate: float
    average_temperature: float
    average_ecg: float
    average_spo2: float


def get_average_sensor_data(user_id: int, days: int = 800):


    return HealthData(
        average_heart_rate=random.randint(60, 100),
        average_temperature=random.randint(96, 100),
        average_ecg=random.randint(60, 100),
        average_spo2=random.randint(90, 100)
    )


@app.get("/api/health_data/{user_id}")
async def health_data_api(user_id: int):
    data = get_average_sensor_data(user_id)
    if data is None:
        print(f"No data found for user {user_id}")
        raise HTTPException(status_code=404, detail="No data found for this user")
    return data


