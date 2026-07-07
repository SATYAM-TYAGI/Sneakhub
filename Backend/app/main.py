"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health, recommendations

# Global dictionary to store loaded model
ml_model = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI startup and shutdown events lifecycle helper.

    Loads the scikit-learn Random Forest model on start.
    """
    # Resolve absolute path relative to Backend root directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, settings.model_path)

    if os.path.exists(model_path):
        try:
            ml_model["model"] = joblib.load(model_path)
            print(f"Successfully loaded ML model from: {model_path}")
        except Exception as e:
            print(f"Error loading ML model from {model_path}: {e}")
    else:
        print(
            f"ML model file not found at {model_path}. "
            "Server will use direct math formula fallback scoring."
        )
    yield
    # Clean up model references
    ml_model.clear()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(recommendations.router)
