"""
ML Models Module
Forecasting, clustering, regression & scenario simulation for Kenya Economic Pulse.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────
#  COUNTY CLUSTERING
# ─────────────────────────────────────────────

def cluster_counties(county_df: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
    """
    KMeans clustering on Kenya counties using socioeconomic features.
    Returns the DataFrame with cluster labels and cluster names.
    """
    features = ["Poverty_Rate", "Unemployment_Rate", "Mobile_Penetration",
                "Electricity_Access", "HDI_Score"]
    X = county_df[features].fillna(county_df[features].mean())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
    county_df = county_df.copy()
    county_df["Cluster"] = km.fit_predict(X_scaled)

    # Name clusters by average poverty rate
    cluster_poverty = county_df.groupby("Cluster")["Poverty_Rate"].mean().sort_values()
    cluster_map = {
        old: new
        for new, old in enumerate(cluster_poverty.index)
    }
    county_df["Cluster"] = county_df["Cluster"].map(cluster_map)

    cluster_labels = {
        0: "🌿 Emerging (Low Poverty)",
        1: "📈 Developing",
        2: "⚡ Transitioning",
        3: "⚠️ Vulnerable",
        4: "🔴 Critical Need"
    }
    county_df["Cluster_Label"] = county_df["Cluster"].map(cluster_labels)
    return county_df


# ─────────────────────────────────────────────
#  TIME-SERIES FORECASTING
# ─────────────────────────────────────────────

def forecast_indicator(series: pd.Series, years: list, forecast_years: int = 5) -> pd.DataFrame:
    """
    Forecast a time series using Holt-Winters Exponential Smoothing.
    Returns a DataFrame with historical + forecast values.
    """
    clean = series.dropna()
    if len(clean) < 5:
        return pd.DataFrame()

    try:
        model = ExponentialSmoothing(
            clean.values,
            trend="add",
            seasonal=None,
            damped_trend=True
        )
        fit = model.fit(optimized=True)
        forecast = fit.forecast(forecast_years)

        all_years  = list(years[:len(clean)]) + list(range(max(years[:len(clean)]) + 1,
                                                           max(years[:len(clean)]) + 1 + forecast_years))
        all_values = list(clean.values) + list(forecast)
        is_forecast = [False] * len(clean) + [True] * forecast_years

        return pd.DataFrame({
            "Year":        all_years,
            "Value":       all_values,
            "Is_Forecast": is_forecast
        })
    except Exception:
        return pd.DataFrame()


def arima_forecast(series: pd.Series, steps: int = 5) -> tuple:
    """
    ARIMA(2,1,2) forecast. Returns (forecast_values, conf_int_df).
    """
    clean = series.dropna()
    if len(clean) < 8:
        return None, None
    try:
        model = ARIMA(clean.values, order=(2, 1, 2))
        result = model.fit()
        forecast_obj = result.get_forecast(steps=steps)
        mean_fc    = forecast_obj.predicted_mean
        conf_int   = forecast_obj.conf_int(alpha=0.2)
        return mean_fc, conf_int
    except Exception:
        return None, None


# ─────────────────────────────────────────────
#  MOBILE MONEY → POVERTY REGRESSION
# ─────────────────────────────────────────────

def mobile_money_poverty_model(mm_df: pd.DataFrame) -> dict:
    """
    Regression: Does mobile money penetration predict poverty reduction?
    Uses multiple features: MPesa users, financial inclusion, GDP growth.
    """
    df = mm_df.dropna().copy()
    features = ["MPesa_Users_M", "Financial_Inclusion_Pct", "GDP_Growth",
                "Mobile_Money_Volume_B_KES", "Remittances_B_USD"]
    target   = "Poverty_Rate_National"

    X = df[features]
    y = df[target]

    if len(X) < 6:
        return {}

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )

    models = {
        "Ridge Regression":        Ridge(alpha=1.0),
        "Gradient Boosting":       GradientBoostingRegressor(n_estimators=100, random_state=42),
        "Random Forest":           RandomForestRegressor(n_estimators=100, random_state=42),
    }

    results = {}
    best_model = None
    best_r2    = -999

    for name, mdl in models.items():
        mdl.fit(X_train, y_train)
        preds = mdl.predict(X_test)
        r2    = r2_score(y_test, preds)
        mae   = mean_absolute_error(y_test, preds)
        results[name] = {"r2": round(r2, 3), "mae": round(mae, 3), "model": mdl}
        if r2 > best_r2:
            best_r2    = r2
            best_model = mdl

    # Feature importance (from best tree-based model)
    gb_model = results["Gradient Boosting"]["model"]
    importance = dict(zip(features, np.round(gb_model.feature_importances_ * 100, 2)))

    # Full predictions with best model
    best_model.fit(X, y)
    df["Predicted_Poverty"] = np.round(best_model.predict(X), 2)

    return {
        "model_results":   results,
        "best_r2":         best_r2,
        "feature_importance": importance,
        "predictions_df":  df,
        "best_model":      best_model,
        "features":        features
    }


# ─────────────────────────────────────────────
#  YOUTH UNEMPLOYMENT FORECASTER & SIMULATOR
# ─────────────────────────────────────────────

def youth_unemployment_model(yu_df: pd.DataFrame) -> dict:
    """
    Gradient Boosting model for youth unemployment prediction.
    Includes scenario simulation.
    """
    df = yu_df.dropna().copy()
    features = ["GDP_Growth", "University_Enrollment_K",
                "FDI_Inflows_B_USD", "Internet_Users_Pct", "Inflation_Rate"]
    target   = "Youth_Unemployment_Pct"

    X = df[features]
    y = df[target]

    model = GradientBoostingRegressor(
        n_estimators=200, learning_rate=0.05,
        max_depth=3, random_state=42
    )
    model.fit(X, y)
    preds = model.predict(X)

    importance = dict(zip(features, np.round(model.feature_importances_ * 100, 2)))

    # Forecast: project features forward 5 years using linear trend
    last_row = df[features].iloc[-1].copy()
    trend = df[features].diff().mean()
    future_rows = []
    for i in range(1, 6):
        row = last_row + trend * i
        future_rows.append(row.values)
    future_X = pd.DataFrame(future_rows, columns=features)
    future_preds = model.predict(future_X)
    future_years = list(range(df["Year"].max() + 1, df["Year"].max() + 6))

    return {
        "model":           model,
        "features":        features,
        "feature_importance": importance,
        "historical_preds": preds,
        "forecast_years":  future_years,
        "forecast_values": future_preds,
        "df":              df
    }


def simulate_scenario(
    yu_model_result: dict,
    gdp_growth: float,
    fdi: float,
    university_k: float,
    internet_pct: float,
    inflation: float
) -> float:
    """Scenario simulation: predict youth unemployment given user-supplied macro parameters."""
    model    = yu_model_result["model"]
    features = yu_model_result["features"]
    X = pd.DataFrame([[gdp_growth, university_k, fdi, internet_pct, inflation]],
                     columns=features)
    return round(float(model.predict(X)[0]), 1)


# ─────────────────────────────────────────────
#  INEQUALITY DECOMPOSITION
# ─────────────────────────────────────────────

def compute_regional_stats(county_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate county data by region."""
    return (
        county_df
        .groupby("Region")
        .agg(
            Counties=("County", "count"),
            Avg_Poverty=("Poverty_Rate", "mean"),
            Avg_Unemployment=("Unemployment_Rate", "mean"),
            Avg_Mobile=("Mobile_Penetration", "mean"),
            Avg_Electricity=("Electricity_Access", "mean"),
            Avg_HDI=("HDI_Score", "mean"),
            Total_Population=("Population_2019", "sum")
        )
        .round(2)
        .reset_index()
    )
