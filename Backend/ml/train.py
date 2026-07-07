"""Machine Learning model training pipeline for sneaker compatibility score prediction."""

import json
import os
import random
import sys
import time
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# Add root Backend folder to sys.path so we can import from app and ml
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.core.logging import get_logger
from app.database import SessionLocal
from app.models.sneaker import Sneaker
from ml.features import calculate_compatibility_score, extract_pairwise_features

logger = get_logger("ml_train")


def run_training():
    """Reads sneakers from database, builds comparison dataset, trains model, and saves outputs."""
    start_time = time.time()
    logger.info("Initializing ML training pipeline...")

    db = SessionLocal()
    try:
        # Load all sneakers along with relations
        sneakers = db.query(Sneaker).all()
        logger.info(f"Loaded {len(sneakers)} sneakers from PostgreSQL database.")

        if len(sneakers) < 5:
            logger.error("Not enough sneakers in database to train model. Need at least 5.")
            return
    except Exception as e:
        logger.critical(f"Database query failed: {e}")
        return
    finally:
        db.close()

    # Generate training pairs
    logger.info("Generating pairwise sneaker combinations dataset...")
    pairs = []
    sneakers_list = list(sneakers)
    num_sneakers = len(sneakers_list)

    # Number of random pairs to sample per sneaker
    pairs_per_sneaker = min(100, num_sneakers)

    for s1 in sneakers_list:
        # 1. Guarantee perfect match representation (s1 with s1 itself)
        pairs.append((s1, s1))

        # 2. Randomly sample other sneakers for comparison
        candidates = random.sample(sneakers_list, pairs_per_sneaker)
        for s2 in candidates:
            if s1.id != s2.id:
                pairs.append((s1, s2))

    logger.info(f"Generated {len(pairs)} sneaker pairs for training.")

    # Extract features and targets
    features_list = []
    targets_list = []

    for s1, s2 in pairs:
        feats = extract_pairwise_features(s1, s2)
        score = calculate_compatibility_score(s1, s2)
        features_list.append(feats)
        targets_list.append(score)

    X = pd.DataFrame(features_list)
    y = pd.Series(targets_list)

    # Keep track of columns
    feature_cols = list(X.columns)
    logger.info(f"Feature columns: {feature_cols}")

    # Train/Test Split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info(
        f"Dataset split. Training samples: {len(X_train)}, Testing samples: {len(X_test)}"
    )

    # Fit RandomForestRegressor
    logger.info("Fitting RandomForestRegressor model...")
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    logger.info("Model fitting complete.")

    # Evaluate model
    y_pred = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, y_pred))
    # Calculate RMSE in a cross-version compatible way
    mse = mean_squared_error(y_test, y_pred)
    rmse = float(pd.Series(mse).apply(lambda v: v**0.5).iloc[0])
    r2 = float(r2_score(y_test, y_pred))

    logger.info("========================================")
    logger.info("EVALUATION METRICS REPORT")
    logger.info(f"Mean Absolute Error (MAE):     {mae:.4f}")
    logger.info(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
    logger.info(f"R² Score:                       {r2:.4f}")
    logger.info("========================================")

    # Save artifacts to configured path
    # If path is relative, resolve it against the current script's parent (Backend)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, settings.model_path)
    artifacts_dir = os.path.dirname(model_path)

    os.makedirs(artifacts_dir, exist_ok=True)

    # Save outputs
    # 1. Model pkl
    joblib.dump(model, model_path)
    logger.info(f"Saved model artifact to: {model_path}")

    # 2. Features json
    features_path = os.path.join(artifacts_dir, "feature_columns.json")
    with open(features_path, "w", encoding="utf-8") as f:
        json.dump(feature_cols, f, indent=2)
    logger.info(f"Saved feature list to: {features_path}")

    # 3. Metrics json
    metrics_path = os.path.join(artifacts_dir, "metrics.json")
    metrics_data = {"mae": mae, "rmse": rmse, "r2": r2}
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
    logger.info(f"Saved evaluation metrics to: {metrics_path}")

    elapsed = time.time() - start_time
    logger.info(f"ML pipeline finished successfully in {elapsed:.2f} seconds.")


if __name__ == "__main__":
    run_training()
