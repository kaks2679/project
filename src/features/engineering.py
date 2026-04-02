"""
src.features.engineering
=========================
Feature engineering utilities for the Kenya Economic Pulse project.
Creates derived variables used in ML models and visualisations.
Author: Stephen Muema
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler


def engineer_features(df: pd.DataFrame, dataset_type: str = "macro") -> pd.DataFrame:
    """
    Create derived features for a given dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    dataset_type : str
        One of 'macro', 'mobile_money', 'county', 'youth'.

    Returns
    -------
    pd.DataFrame with additional engineered columns.
    """
    df = df.copy()

    if dataset_type == "macro":
        # Year-on-year change columns
        numeric = df.select_dtypes(include=np.number).columns.tolist()
        numeric = [c for c in numeric if c != "Year"]
        for col in numeric:
            df[f"{col}_YoY"] = df[col].pct_change() * 100
        # 3-year rolling average
        for col in ["GDP Growth (%)", "Inflation Rate (%)"]:
            if col in df.columns:
                df[f"{col}_3yr_avg"] = df[col].rolling(3, min_periods=1).mean()

    elif dataset_type == "mobile_money":
        df["User_Growth_YoY"] = df["MPesa_Users_M"].pct_change() * 100
        df["Vol_Growth_YoY"]  = df["Mobile_Money_Volume_B_KES"].pct_change() * 100
        df["Fin_Inc_Gap"]     = 100 - df["Financial_Inclusion_Pct"]  # un-banked %
        df["Poverty_Change"]  = df["Poverty_Rate_National"].diff()   # year delta

    elif dataset_type == "county":
        # Development composite score (0–100, higher = better)
        df["Dev_Score"] = (
            (100 - df["Poverty_Rate"]) * 0.35 +
            (100 - df["Unemployment_Rate"]) * 0.20 +
            df["Mobile_Penetration"] * 0.20 +
            df["Electricity_Access"] * 0.15 +
            df["HDI_Score"] * 100 * 0.10
        ).round(2)

    elif dataset_type == "youth":
        df["Unemp_vs_Global"] = df["Youth_Unemployment_Pct"] - 13.6  # vs ILO global avg
        df["Enroll_Growth"]   = df["University_Enrollment_K"].pct_change() * 100

    return df


def scale_features(X: pd.DataFrame, method: str = "standard") -> np.ndarray:
    """Scale features using StandardScaler or MinMaxScaler."""
    if method == "minmax":
        scaler = MinMaxScaler()
    else:
        scaler = StandardScaler()
    return scaler.fit_transform(X)


def interpolate_missing(df: pd.DataFrame, method: str = "linear") -> pd.DataFrame:
    """Fill missing values in numeric columns using interpolation."""
    df = df.copy()
    numeric = df.select_dtypes(include=np.number).columns.tolist()
    df[numeric] = df[numeric].interpolate(method=method, limit_direction="both")
    return df
