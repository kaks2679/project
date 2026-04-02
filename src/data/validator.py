"""
src.data.validator
===================
Data validation utilities — checks completeness, value ranges, and
column presence for Kenya Economic Pulse datasets.
Author: Stephen Muema
"""

import pandas as pd
import numpy as np

SCHEMA = {
    "macro": {
        "required_cols": ["Year"],
        "year_range": (2000, 2024),
    },
    "county": {
        "required_cols": ["County", "Poverty_Rate", "Latitude", "Longitude"],
        "value_ranges": {"Poverty_Rate": (0, 100), "HDI_Score": (0, 1)},
    },
    "mobile_money": {
        "required_cols": ["Year", "MPesa_Users_M", "Poverty_Rate_National"],
        "year_range": (2007, 2024),
    },
    "youth": {
        "required_cols": ["Year", "Youth_Unemployment_Pct"],
        "value_ranges": {"Youth_Unemployment_Pct": (0, 100)},
    },
    "sector": {
        "required_cols": ["Year", "Agriculture"],
    },
    "regional": {
        "required_cols": ["Region"],
    },
}


def validate_dataset(df: pd.DataFrame, name: str) -> dict:
    """
    Validate a dataframe against its schema.
    Returns a dict with keys: valid (bool), errors (list), warnings (list).
    """
    schema  = SCHEMA.get(name, {})
    errors  = []
    warnings_ = []

    # Required columns
    for col in schema.get("required_cols", []):
        if col not in df.columns:
            errors.append(f"Missing required column: '{col}'")

    # Missing values
    total_missing = df.isnull().sum().sum()
    if total_missing > 0:
        warnings_.append(f"{total_missing} missing values detected (interpolation recommended)")

    # Value ranges
    for col, (lo, hi) in schema.get("value_ranges", {}).items():
        if col in df.columns:
            out_of_range = ((df[col] < lo) | (df[col] > hi)).sum()
            if out_of_range > 0:
                errors.append(f"Column '{col}': {out_of_range} values outside [{lo}, {hi}]")

    # Year range
    yr = schema.get("year_range")
    if yr and "Year" in df.columns:
        bad_years = df[(df["Year"] < yr[0]) | (df["Year"] > yr[1])]
        if len(bad_years) > 0:
            warnings_.append(f"{len(bad_years)} rows outside expected year range {yr}")

    return {
        "valid":    len(errors) == 0,
        "errors":   errors,
        "warnings": warnings_,
        "shape":    df.shape,
        "missing":  int(df.isnull().sum().sum()),
    }


def validate_all(datasets: dict) -> dict:
    """Validate all datasets, returns summary dict."""
    return {name: validate_dataset(df, name) for name, df in datasets.items()}
