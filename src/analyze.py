# ============================================================
# src/analyze.py
# Step 5 — Analysis
#
# Answers the 3 core research questions from the project brief:
#
#   Q1 (Regional):  Which states/zones have the highest incident density?
#   Q2 (Temporal):  Are violent events escalating, or are they seasonal?
#   Q3 (Severity):  Which event categories produce the most fatalities per incident?
#
# Input:  data/clean_conflict_data.csv   (saved by clean_data.py)
# Output: 4 CSV files in outputs/
#         - regional_by_state.csv
#         - regional_by_zone.csv
#         - temporal_trends.csv
#         - severity_ratios.csv
#
# To run this file alone (from the project root):
#   python -m src.analyze
# ============================================================

import pandas as pd
import os


# ============================================================
# FILE PATHS
# ============================================================

CLEAN_PATH  = "data/clean_conflict_data.csv"
OUTPUT_DIR  = "outputs"


# ============================================================
# LOAD
# ============================================================

def load_clean_data():
    """
    Reads the cleaned CSV produced by clean_data.py.
    Exits with a clear message if the file is missing.
    """
    if not os.path.exists(CLEAN_PATH):
        print(f"ERROR: '{CLEAN_PATH}' not found. Run clean_data.py first.")
        exit()

    df = pd.read_csv(CLEAN_PATH)

    # Re-cast event_date to datetime (CSV loses the type when saved)
    df["event_date"] = pd.to_datetime(df["event_date"])

    print(f"[Load] Loaded {len(df)} clean records for analysis.")
    return df


# ============================================================
# Q1 — REGIONAL ANALYSIS
# Which states and geopolitical zones have the highest incident density?
# ============================================================

def analyze_regional(df):
    """
    Groups data by state (inside each zone) and by zone.
    Counts total incidents and sums fatalities for each group.
    Sorted by incident count (most active states/zones first).
    """

    # Group by zone + state, count rows (= incidents), sum fatalities
    # reset_index() flattens the grouped result back into a regular DataFrame
    state_summary = df.groupby(["geopolitical_zone", "state"]).agg(
        total_incidents  = ("event_type", "count"),
        total_fatalities = ("fatalities", "sum")
    ).reset_index().sort_values("total_incidents", ascending=False)

    # Same aggregation but at the zone level (ignores state detail)
    zone_summary = df.groupby("geopolitical_zone").agg(
        total_incidents  = ("event_type", "count"),
        total_fatalities = ("fatalities", "sum")
    ).reset_index().sort_values("total_incidents", ascending=False)

    print("\n--- Q1: REGIONAL ANALYSIS — Top 10 States by Incident Count ---")
    print(state_summary.head(10).to_string(index=False))

    print("\n--- Q1: ZONE SUMMARY ---")
    print(zone_summary.to_string(index=False))

    return state_summary, zone_summary


# ============================================================
# Q2 — TEMPORAL ANALYSIS
# Are violent events escalating month-over-month, or seasonal?
# ============================================================

def analyze_temporal(df):
    """
    Groups data by month_year (e.g. '2024-01') and counts incidents
    and fatalities per month.
    Sorted chronologically so the trend is easy to read.
    """

    monthly = df.groupby("month_year").agg(
        total_incidents  = ("event_type", "count"),
        total_fatalities = ("fatalities", "sum")
    ).reset_index().sort_values("month_year")

    print("\n--- Q2: TEMPORAL ANALYSIS — Monthly Trend ---")
    print(monthly.to_string(index=False))

    return monthly


# ============================================================
# Q3 — SEVERITY ANALYSIS
# Which event categories produce the highest casualty-to-incident ratio?
# ============================================================

def analyze_severity(df):
    """
    Groups data by event_type and calculates the casualty ratio:
        casualty_ratio = total_fatalities / total_incidents

    A high ratio means that type of event kills more people per occurrence.
    This is more informative than raw fatality counts alone.
    """

    severity = df.groupby("event_type").agg(
        total_incidents  = ("event_type", "count"),
        total_fatalities = ("fatalities", "sum")
    ).reset_index()

    # Avoid division by zero: if total_incidents is 0, ratio stays 0
    severity["casualty_ratio"] = (
        severity["total_fatalities"] / severity["total_incidents"]
    ).round(2)

    severity = severity.sort_values("casualty_ratio", ascending=False)

    print("\n--- Q3: SEVERITY ANALYSIS — Casualty-to-Incident Ratio ---")
    print(severity.to_string(index=False))

    return severity


# ============================================================
# SAVE RESULTS
# ============================================================

def save_analysis_results(state_summary, zone_summary, monthly, severity):
    """
    Saves each result DataFrame as a CSV in the outputs/ folder.
    visualize.py reads these files to build the PNG charts.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    state_summary.to_csv(f"{OUTPUT_DIR}/regional_by_state.csv",  index=False)
    zone_summary.to_csv(f"{OUTPUT_DIR}/regional_by_zone.csv",    index=False)
    monthly.to_csv(f"{OUTPUT_DIR}/temporal_trends.csv",          index=False)
    severity.to_csv(f"{OUTPUT_DIR}/severity_ratios.csv",         index=False)

    print(f"\n[Save] All analysis CSVs saved to '{OUTPUT_DIR}/'.")


# ============================================================
# PIPELINE ORCHESTRATOR
# ============================================================

def run_analysis():
    """
    Runs all 3 research question analyses in sequence.
    Returns all result DataFrames so main.py can track them.
    """
    df = load_clean_data()
    state_summary, zone_summary = analyze_regional(df)
    monthly                     = analyze_temporal(df)
    severity                    = analyze_severity(df)
    save_analysis_results(state_summary, zone_summary, monthly, severity)
    return df, state_summary, zone_summary, monthly, severity


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print("Running analysis...")
    print("-" * 50)
    run_analysis()
    print("-" * 50)
    print("Analysis complete.")