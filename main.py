# ============================================================
# main.py
# Pipeline Orchestrator
#
# Runs all 4 stages of the project in order:
#
#   Step 3: fetch_data.py   — download/mock Nigerian conflict data
#   Step 4: clean_data.py   — clean and standardize the raw CSV
#   Step 5: analyze.py      — answer the 3 research questions
#   Step 6: visualize.py    — generate and save 4 PNG charts
#
# Run this from the project root folder:
#   python main.py
# ============================================================

from src.fetch_data  import fetch_nigeria_conflict_data
from src.clean_data  import run_cleaning_pipeline
from src.analyze     import run_analysis
from src.visualize   import run_visualizations


def main():
    print("=" * 55)
    print("  CPE CLUB — Spatiotemporal Analysis of Insecurity")
    print("  in Nigeria")
    print("=" * 55)

    print("\n[Step 3] Fetching data...")
    print("-" * 40)
    fetch_nigeria_conflict_data()

    print("\n[Step 4] Cleaning data...")
    print("-" * 40)
    run_cleaning_pipeline()

    print("\n[Step 5] Running analysis...")
    print("-" * 40)
    run_analysis()

    print("\n[Step 6] Generating visualizations...")
    print("-" * 40)
    run_visualizations()

    print("\n" + "=" * 55)
    print("  Pipeline complete.")
    print("  Raw data    -> data/raw_nigeria_conflict.csv")
    print("  Clean data  -> data/clean_conflict_data.csv")
    print("  Analysis    -> outputs/*.csv")
    print("  Charts      -> outputs/charts/*.png")
    print("=" * 55)


if __name__ == "__main__":
    main()