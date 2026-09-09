import os
from pathlib import Path

# ── Model path — absolute so it works regardless of working directory ──────────
_THIS_DIR = Path(__file__).parent
MODEL_PATH = str(_THIS_DIR / "landslide_model.pkl")

FEATURES = [
    "rainfall_24h_mm",
    "rainfall_7d_mm",
    "slope_deg"
]

# --------------------------------------------------
# LOAD MODEL (graceful if packages are missing)
# --------------------------------------------------

_HAS_ML = False
model = None

try:
    import joblib
    import pandas as pd
    model = joblib.load(MODEL_PATH)
    _HAS_ML = True
except (ImportError, Exception):
    pass


# --------------------------------------------------
# RISK LEVEL
# --------------------------------------------------

def get_risk_level(risk):

    if risk < 30:
        return "LOW"

    elif risk < 60:
        return "MEDIUM"

    else:
        return "HIGH"


# --------------------------------------------------
# FALLBACK HEURISTIC (when ML packages unavailable)
# --------------------------------------------------

def _heuristic_risk(rainfall_24h_mm, rainfall_7d_mm, slope_deg):
    """Simple weighted heuristic when the ML model isn't available."""
    # Normalise inputs to [0, 1] range using reasonable NE India maxima
    r24_norm = min(rainfall_24h_mm / 150.0, 1.0)   # 150mm/day = extreme
    r7d_norm = min(rainfall_7d_mm / 500.0, 1.0)     # 500mm/week = extreme
    slope_norm = min(slope_deg / 45.0, 1.0)          # 45° = very steep

    # Weighted combination: slope matters most, then recent rain
    risk = (0.40 * slope_norm + 0.35 * r24_norm + 0.25 * r7d_norm) * 100
    return round(max(0, min(100, risk)))


# --------------------------------------------------
# PREDICT LANDSLIDE RISK
# --------------------------------------------------

def predict_landslide_risk(
    rainfall_24h_mm,
    rainfall_7d_mm,
    slope_deg
):
    if _HAS_ML and model is not None:
        import pandas as pd
        input_data = pd.DataFrame(
            [[
                rainfall_24h_mm,
                rainfall_7d_mm,
                slope_deg
            ]],
            columns=FEATURES
        )

        # Probability of class 1 = landslide
        probability = model.predict_proba(input_data)[0][1]

        # Convert probability to 0-100
        risk = round(probability * 100)
    else:
        # Fallback heuristic when sklearn/joblib not available (e.g. Vercel)
        risk = _heuristic_risk(rainfall_24h_mm, rainfall_7d_mm, slope_deg)

    risk_level = get_risk_level(risk)

    return {
        "landslide_risk": risk,
        "risk_level": risk_level
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    result = predict_landslide_risk(
        rainfall_24h_mm=80,
        rainfall_7d_mm=300,
        slope_deg=35
    )

    print("\nMARG LANDSLIDE RISK")
    print("===================")

    print(
        f"Landslide Risk: "
        f"{result['landslide_risk']}%"
    )

    print(
        f"Risk Level: "
        f"{result['risk_level']}"
    )
