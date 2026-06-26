# ============================================================
# src/visualize.py
# Step 6 — Visualization
#
# Reads the analysis CSVs and produces 4 PNG charts:
#
#   Chart 1: Top 15 states by incident count (horizontal bar)
#   Chart 2: Incidents and fatalities per geopolitical zone (side-by-side bar)
#   Chart 3: Monthly trend of incidents and fatalities (dual line chart)
#   Chart 4: Casualty-to-incident ratio by event type (bar chart)
#
# All charts are saved as PNG files in outputs/charts/
# PNG format keeps the charts permanently and makes them easy to
# include in the GitHub README or a project report.
#
# Input:  4 CSV files in outputs/
# Output: 4 PNG files in outputs/charts/
#
# To run this file alone (from the project root):
#   python -m src.visualize
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import os


# ============================================================
# GLOBAL SETTINGS
# ============================================================

# darkgrid gives us a clean dark background with gridlines
# which makes the bars and lines easier to read
sns.set_theme(style="darkgrid")

# All PNG files go here
CHART_DIR = "outputs/charts"
os.makedirs(CHART_DIR, exist_ok=True)


# ============================================================
# LOAD
# ============================================================

def load_results():
    """
    Reads all 4 analysis CSVs that analyze.py saved.
    Exits with a helpful message if any file is missing.
    """
    paths = {
        "state":    "outputs/regional_by_state.csv",
        "zone":     "outputs/regional_by_zone.csv",
        "monthly":  "outputs/temporal_trends.csv",
        "severity": "outputs/severity_ratios.csv",
    }

    for label, path in paths.items():
        if not os.path.exists(path):
            print(f"ERROR: '{path}' not found. Run analyze.py first.")
            exit()

    state_summary = pd.read_csv(paths["state"])
    zone_summary  = pd.read_csv(paths["zone"])
    monthly       = pd.read_csv(paths["monthly"])
    severity      = pd.read_csv(paths["severity"])

    print("[Load] All analysis CSVs loaded.")
    return state_summary, zone_summary, monthly, severity


# ============================================================
# CHART 1 — Top 15 States by Total Incident Count
# Answers: Q1 (Regional) at the state level
# ============================================================

def chart_top_states(state_summary):
    """
    Horizontal bar chart showing the 15 most affected states.
    Horizontal layout makes long state names readable.
    The bar length = total number of incidents in that state.
    """
    # Take only the top 15 rows (already sorted by total_incidents desc)
    top15 = state_summary.head(15).copy()

    fig, ax = plt.subplots(figsize=(12, 7))

    # barh = horizontal bar chart
    bars = ax.barh(top15["state"], top15["total_incidents"], color="firebrick")

    ax.set_xlabel("Total Incidents")
    ax.set_title("Top 15 Nigerian States by Violent Incident Count")
    # invert_yaxis puts the highest bar at the top (more intuitive)
    ax.invert_yaxis()

    # Add the count label at the end of each bar for quick reading
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 0.3,
            bar.get_y() + bar.get_height() / 2,
            str(int(width)),
            va="center",
            fontsize=9
        )

    plt.tight_layout()
    output_path = f"{CHART_DIR}/top_states_incidents.png"
    plt.savefig(output_path, dpi=150)
    plt.close()  # close the figure to free memory before the next chart
    print(f"[Chart 1] Saved: {output_path}")


# ============================================================
# CHART 2 — Incidents and Fatalities by Geopolitical Zone
# Answers: Q1 (Regional) at the zone level
# ============================================================

def chart_zones(zone_summary):
    """
    Two side-by-side bar charts:
      Left:  total incidents per zone (tells us where violence is most frequent)
      Right: total fatalities per zone (tells us where violence is most deadly)
    Comparing these two lets policy makers see if frequency and lethality align.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left chart — incident count
    axes[0].bar(zone_summary["geopolitical_zone"], zone_summary["total_incidents"], color="steelblue")
    axes[0].set_title("Incidents by Geopolitical Zone")
    axes[0].set_xlabel("Zone")
    axes[0].set_ylabel("Total Incidents")
    axes[0].tick_params(axis="x", rotation=30)

    # Right chart — fatality count
    axes[1].bar(zone_summary["geopolitical_zone"], zone_summary["total_fatalities"], color="darkred")
    axes[1].set_title("Fatalities by Geopolitical Zone")
    axes[1].set_xlabel("Zone")
    axes[1].set_ylabel("Total Fatalities")
    axes[1].tick_params(axis="x", rotation=30)

    plt.suptitle("Conflict Distribution Across Nigerian Geopolitical Zones", fontsize=13)
    plt.tight_layout()
    output_path = f"{CHART_DIR}/zones_comparison.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[Chart 2] Saved: {output_path}")


# ============================================================
# CHART 3 — Monthly Trend of Incidents and Fatalities
# Answers: Q2 (Temporal)
# ============================================================

def chart_monthly_trend(monthly):
    """
    Dual line chart showing incidents and fatalities over time.
    - Solid orange line = incident count per month
    - Dashed red line   = fatality count per month
    If both lines rise together, violence is escalating.
    If they diverge, some months have more incidents but fewer deaths (or vice versa).
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(
        monthly["month_year"], monthly["total_incidents"],
        marker="o", color="darkorange", linewidth=2, label="Incidents"
    )
    ax.plot(
        monthly["month_year"], monthly["total_fatalities"],
        marker="s", color="crimson", linewidth=2, linestyle="--", label="Fatalities"
    )

    ax.set_title("Monthly Trend of Incidents and Fatalities")
    ax.set_xlabel("Month")
    ax.set_ylabel("Count")
    ax.legend()

    # Show roughly one label per month on the x-axis to avoid crowding
    step = max(1, len(monthly) // 12)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(step))
    ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    output_path = f"{CHART_DIR}/monthly_trend.png"
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"[Chart 3] Saved: {output_path}")


# ============================================================
# CHART 4 — Casualty-to-Incident Ratio by Event Type
# Answers: Q3 (Severity)
# ============================================================

def chart_severity(severity):
    """
    Bar chart ranking each event type by its casualty ratio
    (average fatalities per incident).
    A high ratio means that event type kills more people per occurrence —
    useful for knowing which conflict categories are most dangerous.
    """
    # Red gradient — darker = more deadly
    colors = ["#8B0000", "#B22222", "#CD5C5C", "#E9967A", "#F08080"]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(
        severity["event_type"],
        severity["casualty_ratio"],
        color=colors[:len(severity)]
    )

    ax.set_title("Casualty-to-Incident Ratio by Event Type")
    ax.set_xlabel("Event Type")
    ax.set_ylabel("Avg Fatalities per Incident")
    ax.tick_params(axis="x", rotation=20)

    # Add the ratio value on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.05,
            f"{height:.2f}",
            ha="center",
            fontsize=10
        )

    plt.tight_layout()
    output_path = f"{CHART_DIR}/severity_ratio.png"
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"[Chart 4] Saved: {output_path}")


# ============================================================
# PIPELINE ORCHESTRATOR
# ============================================================

def run_visualizations():
    """
    Loads all analysis results and generates all 4 PNG charts.
    """
    state_summary, zone_summary, monthly, severity = load_results()

    print("Generating charts...")
    chart_top_states(state_summary)
    chart_zones(zone_summary)
    chart_monthly_trend(monthly)
    chart_severity(severity)

    print(f"\n[Done] All charts saved to '{CHART_DIR}/'.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_visualizations()