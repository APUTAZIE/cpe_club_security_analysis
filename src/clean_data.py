# ============================================================
# src/clean_data.py
# Step 4 — Data Cleaning Pipeline
# Branch: feature/data-cleaning
#
# What this script does (4 steps from the project flowchart):
#   4a. Drop records missing critical geographic keys (admin1 / admin2)
#   4b. Cast fatalities to integer and event_date to datetime
#   4c. Standardize Nigerian state names (ACLED can have messy spellings)
#   4d. Derive a Month_Year column for temporal analysis
#
# Extra step (needed for analysis):
#   - Rename ACLED columns to friendlier names (admin1 -> state, admin2 -> lga)
#   - Add geopolitical_zone column (ACLED does not include this; we map it ourselves)
#
# Input:  data/raw_nigeria_conflict.csv   (saved by fetch_data.py)
# Output: data/clean_conflict_data.csv
#
# To run this file alone (from the project root):
#   python -m src.clean_data
# ============================================================

import pandas as pd
import os


# ============================================================
# FILE PATHS
# ============================================================

# The raw CSV that fetch_data.py saved
RAW_PATH = "data/raw_nigeria_conflict.csv"

# Where we save the cleaned version for analyze.py to pick up
CLEAN_PATH = "data/clean_conflict_data.csv"


# ============================================================
# STEP 4c — State name standardization dictionary
#
# ACLED entries are typed by humans and can have inconsistent spellings.
# This dictionary maps known variants to the official Nigerian state name.
# Add more entries here as you find new variants in the real dataset.
# ============================================================

STATE_NAME_MAP = {
    # FCT variants
    "Abuja":                       "FCT",
    "Federal Capital Territory":   "FCT",
    "F.C.T":                       "FCT",

    # Cross River variants
    "Cross-River":                 "Cross River",
    "Cross River State":           "Cross River",
    "Crossriver":                  "Cross River",

    # Akwa Ibom variants
    "Akwa-Ibom":                   "Akwa Ibom",
    "AkwaIbom":                    "Akwa Ibom",
    "Akwa Ibom State":             "Akwa Ibom",

    # Other common variants
    "Rivers State":                "Rivers",
    "Lagos State":                 "Lagos",
    "Kano State":                  "Kano",
    "Nassarawa":                   "Nasarawa",   # common typo in ACLED
    "Nasarawa":                    "Nasarawa",

    # Add more here if you discover new if you wish
}


# ============================================================
# GEOPOLITICAL ZONE MAPPING
#
# Nigeria's 36 states + FCT are grouped into 6 geopolitical zones.
# ACLED does not include this grouping, so we build it ourselves.
# This is what powers the "Regional Analysis" in analyze.py.
# ============================================================

ZONE_MAP = {
    # North West
    "Kano":       "North West",
    "Kaduna":     "North West",
    "Katsina":    "North West",
    "Zamfara":    "North West",
    "Sokoto":     "North West",
    "Kebbi":      "North West",
    "Jigawa":     "North West",

    # North East
    "Borno":      "North East",
    "Yobe":       "North East",
    "Adamawa":    "North East",
    "Gombe":      "North East",
    "Bauchi":     "North East",
    "Taraba":     "North East",

    # North Central
    "Niger":      "North Central",
    "Kwara":      "North Central",
    "Kogi":       "North Central",
    "Benue":      "North Central",
    "Plateau":    "North Central",
    "Nasarawa":   "North Central",
    "FCT":        "North Central",

    # South West
    "Lagos":      "South West",
    "Ogun":       "South West",
    "Oyo":        "South West",
    "Osun":       "South West",
    "Ondo":       "South West",
    "Ekiti":      "South West",

    # South East
    "Enugu":      "South East",
    "Anambra":    "South East",
    "Imo":        "South East",
    "Abia":       "South East",
    "Ebonyi":     "South East",

    # South South
    "Rivers":     "South South",
    "Delta":      "South South",
    "Bayelsa":    "South South",
    "Edo":        "South South",
    "Cross River":"South South",
    "Akwa Ibom":  "South South",
}


# ============================================================
# PIPELINE FUNCTIONS
# ============================================================

def load_raw_data():
    """
    Reads the raw CSV that fetch_data.py saved.
    Exits with a helpful message if the file is missing.
    """
    if not os.path.exists(RAW_PATH):
        print(f"ERROR: '{RAW_PATH}' not found. Run fetch_data.py first.")
        exit()

    df = pd.read_csv(RAW_PATH)
    print(f"[Load]    Loaded {len(df)} raw records from '{RAW_PATH}'.")
    print(f"          Columns: {list(df.columns)}")
    return df


def rename_acled_columns(df):
    """
    ACLED uses 'admin1' for state and 'admin2' for LGA.
    We rename them so the rest of our pipeline uses clearer names.
    """
    df = df.rename(columns={
        "admin1": "state",
        "admin2": "lga"
    })
    print("[Rename]  Renamed 'admin1' -> 'state', 'admin2' -> 'lga'.")
    return df


def step_4a_drop_missing_geo(df):
    """
    Step 4a: Drop any row that is missing its state or LGA.
    We cannot place these on a map or assign them to a zone,
    so they are useless for our regional and temporal analysis.
    """
    before = len(df)

    # dropna removes rows where either of these two columns is empty
    df = df.dropna(subset=["state", "lga"])

    dropped = before - len(df)
    print(f"[Step 4a] Dropped {dropped} records missing geographic keys (state/lga).")
    print(f"          Remaining: {len(df)} records.")
    return df


def step_4b_cast_types(df):
    """
    Step 4b: Fix data types so math and sorting work correctly.
    - fatalities: ACLED stores this as a number but it can arrive as string
    - event_date: must be datetime so we can extract month and year from it
    """
    # pd.to_numeric coerces bad values to NaN instead of crashing
    # fillna(0) replaces any NaN fatality with 0 (event happened, nobody died)
    df["fatalities"] = pd.to_numeric(df["fatalities"], errors="coerce").fillna(0).astype(int)

    # errors="coerce" turns unparseable dates into NaT (Not a Time)
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")

    # Drop rows whose date could not be parsed — we cannot place them on a timeline
    bad_dates = df["event_date"].isna().sum()
    df = df.dropna(subset=["event_date"])

    print(f"[Step 4b] Cast 'fatalities' to int, 'event_date' to datetime.")
    if bad_dates > 0:
        print(f"          Dropped {bad_dates} rows with unparseable dates.")
    return df


def step_4c_standardize_states(df):
    """
    Step 4c: Standardize Nigerian state names.
    ACLED data is entered by different analysts and can have spelling variants.
    We map known variants to their official name using STATE_NAME_MAP above.

    After standardizing, we also strip extra whitespace from all state names
    to catch cases like " Borno" or "Lagos " that the map might miss.
    """
    # Strip leading/trailing whitespace first
    df["state"] = df["state"].str.strip()

    # Replace any key in STATE_NAME_MAP with its correct official name
    df["state"] = df["state"].replace(STATE_NAME_MAP)

    print(f"[Step 4c] Standardized state names using mapping dictionary.")
    print(f"          Unique states after cleaning: {sorted(df['state'].unique())}")
    return df


def add_geopolitical_zone(df):
    """
    Maps each state to one of Nigeria's 6 geopolitical zones.
    ACLED does not include this column — we derive it ourselves.
    Rows with unrecognized state names get 'Unknown' so we don't lose data.
    """
    # .map() looks up each state in ZONE_MAP; returns NaN if not found
    df["geopolitical_zone"] = df["state"].map(ZONE_MAP)

    # Count and report any states that did not match the map
    unknown = df["geopolitical_zone"].isna().sum()
    if unknown > 0:
        unmatched = df[df["geopolitical_zone"].isna()]["state"].unique()
        print(f"[Zone]    WARNING: {unknown} rows have unrecognized states: {unmatched}")
        print(f"          Add them to STATE_NAME_MAP or ZONE_MAP to fix this.")

    # Fill unmatched states with 'Unknown' so the pipeline continues
    df["geopolitical_zone"] = df["geopolitical_zone"].fillna("Unknown")
    print(f"[Zone]    Geopolitical zone column added.")
    return df


def step_4d_add_month_year(df):
    """
    Step 4d: Derive a Month_Year column from event_date.
    This is what the temporal analysis groups data by (e.g. '2024-01').
    dt.to_period('M') extracts just the year and month from a full datetime.
    """
    df["month_year"] = df["event_date"].dt.to_period("M").astype(str)
    print(f"[Step 4d] Derived 'month_year' column from 'event_date'.")
    return df


def save_clean_data(df):
    """
    Saves the cleaned DataFrame to data/clean_conflict_data.csv.
    This file is what analyze.py reads next.
    """
    os.makedirs("data", exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    print(f"[Save]    Cleaned data saved: {len(df)} records -> '{CLEAN_PATH}'.")


# ============================================================
# PIPELINE ORCHESTRATOR
# ============================================================

def run_cleaning_pipeline():
    """
    Runs all 4 cleaning steps in order.
    Returns the cleaned DataFrame so main.py can pass it to analyze.py.
    """
    df = load_raw_data()
    df = rename_acled_columns(df)
    df = step_4a_drop_missing_geo(df)
    df = step_4b_cast_types(df)
    df = step_4c_standardize_states(df)
    df = add_geopolitical_zone(df)
    df = step_4d_add_month_year(df)
    save_clean_data(df)
    return df


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print("Starting data cleaning pipeline...")
    print("-" * 50)
    run_cleaning_pipeline()
    print("-" * 50)
    print("Cleaning complete.")