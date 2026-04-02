"""
src.models.regression
======================
Supervised regression models:
  - Mobile money -> poverty prediction
  - Youth unemployment prediction
Author: Stephen Muema
"""

import pandas as pd
import numpy as np
from sklearn.linear_model    import Ridge
from sklearn.ensemble        import GradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing   import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics         import r2_score, mean_absolute_error
import warnings
warnings.filterwarnings("ignore")


def train_poverty_model(mm_df: pd.DataFrame) -> dict:
    """
    Train Ridge, Random Forest, and Gradient Boosting regressors
    to predict national poverty rate from mobile money indicators.
    """
    df = mm_df.dropna().copy()
    features = ["MPesa_Users_M", "Financial_Inclusion_Pct",
                "GDP_Growth", "Mobile_Money_Volume_B_KES", "Remittances_B_USD"]
    target   = "Poverty_Rate_National"

    X, y = df[features], df[target]
    scaler = StandardScaler()
    X_sc   = scaler.fit_transform(X)

    X_tr, X_te, y_tr, y_te = train_test_split(X_sc, y, test_size=0.25, random_state=42)

    candidates = {
        "Ridge Regression":  Ridge(alpha=1.0),
        "Random Forest":     RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
    }

    results, best_model, best_r2 = {}, None, -1
    for name, model in candidates.items():
        model.fit(X_tr, y_tr)
        preds = model.predict(X_te)
        r2  = r2_score(y_te, preds)
        mae = mean_absolute_error(y_te, preds)
        cv  = cross_val_score(model, X_sc, y, cv=3, scoring="r2").mean()
        results[name] = {"r2": round(r2, 3), "mae": round(mae, 3), "cv_r2": round(cv, 3)}
        if r2 > best_r2:
            best_r2, best_model = r2, model

    # Feature importance from Gradient Boosting
    gb = candidates["Gradient Boosting"]
    gb.fit(X_sc, y)
    importance = dict(zip(features, np.round(gb.feature_importances_ * 100, 2)))

    # Full-dataset predictions with best model
    best_model.fit(X_sc, y)
    df["Predicted"] = np.round(best_model.predict(X_sc), 2)

    return {
        "results":    results,
        "best_r2":    best_r2,
        "importance": importance,
        "predictions": df[["Year", target, "Predicted"]],
        "scaler":     scaler,
        "features":   features,
    }


def train_youth_model(yu_df: pd.DataFrame) -> dict:
    """
    Train a Gradient Boosting regressor to predict youth unemployment
    from macro-economic structural factors.
    """
    df = yu_df.dropna().copy()
    features = ["GDP_Growth", "University_Enrollment_K",
                "FDI_Inflows_B_USD", "Internet_Users_Pct", "Inflation_Rate"]
    target   = "Youth_Unemployment_Pct"

    X, y = df[features], df[target]
    model = GradientBoostingRegressor(
        n_estimators=200, learning_rate=0.05, max_depth=3, random_state=42
    )
    model.fit(X, y)
    preds = model.predict(X)

    importance = dict(zip(features, np.round(model.feature_importances_ * 100, 2)))
    r2  = r2_score(y, preds)
    mae = mean_absolute_error(y, preds)

    return {
        "model":      model,
        "r2":         round(r2, 3),
        "mae":        round(mae, 3),
        "importance": importance,
        "features":   features,
        "preds":      preds,
    }
