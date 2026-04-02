"""
src.data.loader
================
Functions to load Kenya Economic Pulse datasets from the /data directory
or fetch live data from the World Bank API.
Author: Stephen Muema
"""

import os
import pandas as pd
import sys

_THIS_DIR     = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
_DATA_DIR     = os.path.join(_PROJECT_ROOT, "data")

CSV_FILES = {
    "macro":        "kenya_macro_indicators.csv",
    "county":       "kenya_county_data.csv",
    "mobile_money": "kenya_mobile_money.csv",
    "youth":        "kenya_youth_unemployment.csv",
    "sector":       "kenya_sector_employment.csv",
    "regional":     "kenya_regional_stats.csv",
}


def load_dataset(name: str, data_dir: str = None) -> pd.DataFrame:
    """Load a single dataset by name key."""
    d = data_dir or _DATA_DIR
    fname = CSV_FILES.get(name)
    if fname is None:
        raise ValueError(f"Unknown dataset: '{name}'. Valid keys: {list(CSV_FILES)}")
    fpath = os.path.join(d, fname)
    if not os.path.exists(fpath):
        raise FileNotFoundError(f"CSV not found: {fpath}")
    return pd.read_csv(fpath)


def load_all_datasets(data_dir: str = None) -> dict:
    """Load all 6 datasets into a dict keyed by short name."""
    return {name: load_dataset(name, data_dir) for name in CSV_FILES}


def get_data_dir() -> str:
    """Return the resolved data directory path."""
    return _DATA_DIR
