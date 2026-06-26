# ============================================================
# src/fetch_data.py
# Step 3 — Data Gathering Script
# Branch: feature/data-gathering
#
# Two modes controlled by USE_MOCK:
#
#   USE_MOCK = True  → uses the 10-row fake sample below (no files needed)
#   USE_MOCK = False → reads the real ACLED CSV you downloaded manually
#                      from acleddata.com/conflict-data/data-export-tool/
#                      and placed in data/raw_nigeria_conflict.csv
#
# We switched to local CSV mode because ACLED migrated to a new API
# and the old key-based endpoint is deprecated. The downloaded CSV
# contains the same real data the API would have returned.
#
# To run this file alone (from the project root):
#   python -m src.fetch_data
# ============================================================

import logging    # prints log messages with timestamps
import os         # checks folders and file paths
import sys        # lets us exit early if something goes wrong

import pandas as pd  # handles tabular data


# ============================================================
# MOCK SWITCH
# ============================================================

# True  = use the 10-row fake sample below (safe to run immediately)
# False = read the real ACLED CSV from data/raw_nigeria_conflict.csv
USE_MOCK = False


# ============================================================
# FILE PATHS
# ============================================================

# Where the real downloaded CSV should be placed
# Download from: acleddata.com/conflict-data/data-export-tool/
# Filter: Nigeria, 2023-01-01 to 2024-12-31, then export
REAL_CSV_PATH = "data/raw_nigeria_conflict.csv"

# Where we save the output for clean_data.py to pick up
OUTPUT_FOLDER   = "data"
OUTPUT_FILENAME = "raw_nigeria_conflict.csv"
OUTPUT_PATH     = os.path.join(OUTPUT_FOLDER, OUTPUT_FILENAME)


# ============================================================
# MOCK DATA — 10 fake rows that mirror real ACLED CSV structure
# Only used when USE_MOCK = True
# ============================================================

MOCK_CSV_DATA = """event_id_cnty,event_date,year,event_type,sub_event_type,actor1,country,admin1,admin2,location,latitude,longitude,fatalities,notes
NGA2024001,2024-01-15,2024,Violence Against Civilians,Attack,Boko Haram,Nigeria,Borno,Bama,Bama,11.5204,13.6903,3,Armed group attacked a civilian settlement in Bama
NGA2024002,2024-01-20,2024,Battles,Armed clash,Nigerian Military,Nigeria,Zamfara,Gusau,Gusau,12.1704,6.6649,12,Clash between military and bandits near Gusau
NGA2024003,2024-02-01,2024,Explosions/Remote Violence,Suicide bomb,ISWAP,Nigeria,Adamawa,Yola,Yola,9.2035,12.4954,5,Suicide bombing at a market in Yola
NGA2024004,2024-02-14,2024,Riots,Violent demonstration,Protesters,Nigeria,Lagos,Lagos Island,Lagos,6.4541,3.3947,0,Protest turned violent near Lagos Island
NGA2024005,2024-03-05,2024,Violence Against Civilians,Abduction/forced disappearance,Unknown,Nigeria,Kaduna,Zaria,Zaria,11.1112,7.7227,1,Gunmen abducted several farmers outside Zaria
NGA2024006,2024-03-18,2024,Battles,Armed clash,Bandits,Nigeria,Katsina,Jibia,Jibia,13.0833,7.2000,8,Bandits attacked a military convoy near Jibia
NGA2024007,2024-04-02,2024,Explosions/Remote Violence,IED,Boko Haram,Nigeria,Borno,Maiduguri,Maiduguri,11.8311,13.1510,6,IED detonated near a marketplace in Maiduguri
NGA2024008,2024-04-20,2024,Violence Against Civilians,Attack,Unknown,Nigeria,Plateau,Jos,Jos,9.8965,8.8583,4,Gunmen attacked a farming community near Jos
NGA2024009,2024-05-10,2024,Strategic Developments,Headquarters established,Nigerian Military,Nigeria,Borno,Monguno,Monguno,13.6167,13.6167,0,Military established new forward operating base in Monguno
NGA2024010,2024-05-25,2024,Riots,Violent demonstration,Youth group,Nigeria,Rivers,Port Harcourt,Port Harcourt,4.8156,7.0498,2,Violent clashes between youth groups in Port Harcourt
"""


# ============================================================
# LOGGING SETUP
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# ============================================================
# MOCK MODE — returns the fake 10-row sample
# ============================================================

def get_mock_data():
    """
    Returns the mock CSV string as a DataFrame.
    No files or internet needed. Used for quick testing.
    """
    import io
    logger.info("--------------------------------------------------")
    logger.info("  MOCK MODE IS ON (USE_MOCK = True)")
    logger.info("  Using fake 10-row sample data.")
    logger.info("  Set USE_MOCK = False to use the real ACLED CSV.")
    logger.info("--------------------------------------------------")
    return pd.read_csv(io.StringIO(MOCK_CSV_DATA))


# ============================================================
# REAL MODE — reads the downloaded ACLED CSV from disk
# ============================================================

def get_real_data():
    """
    Reads the real ACLED CSV that you downloaded manually from:
    acleddata.com/conflict-data/data-export-tool/

    The file must be placed at: data/raw_nigeria_conflict.csv
    before running this script.
    """
    logger.info("--------------------------------------------------")
    logger.info("  LIVE MODE IS ON (USE_MOCK = False)")
    logger.info(f"  Reading real ACLED CSV from: {REAL_CSV_PATH}")
    logger.info("--------------------------------------------------")

    # Check the file exists before trying to read it
    if not os.path.exists(REAL_CSV_PATH):
        logger.error(f"File not found: '{REAL_CSV_PATH}'")
        logger.error("Download the CSV from acleddata.com/conflict-data/data-export-tool/")
        logger.error("Filter by Nigeria, 2023-2024, then export and rename it to:")
        logger.error(f"  {REAL_CSV_PATH}")
        sys.exit(1)

    try:
        # Read the CSV — pandas auto-detects column types
        df = pd.read_csv(REAL_CSV_PATH, low_memory=False)
    except Exception as e:
        logger.error(f"Failed to read CSV file: {e}")
        sys.exit(1)

    logger.info(f"CSV loaded successfully: {len(df)} rows, {len(df.columns)} columns.")
    logger.info(f"Columns found: {list(df.columns)}")
    return df


# ============================================================
# MAIN FUNCTION
# ============================================================

def fetch_nigeria_conflict_data():
    """
    Loads the conflict data (mock or real) and saves it to
    data/raw_nigeria_conflict.csv for clean_data.py to process.

    In real mode, the file is already in the right place so we
    just read it, log the summary, and confirm it is ready.
    """
    logger.info("Starting data fetch for Nigeria conflict data...")

    # Choose data source based on the USE_MOCK flag
    if USE_MOCK:
        df = get_mock_data()
    else:
        df = get_real_data()

    rows, cols = df.shape
    logger.info(f"Dataset ready: {rows} rows, {cols} columns.")

    # In real mode the file is already saved where we need it
    # In mock mode we write the fake data to the same location
    if USE_MOCK:
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        df.to_csv(OUTPUT_PATH, index=False)
        logger.info(f"Mock data saved to: {OUTPUT_PATH}")
    else:
        logger.info(f"Real data already at: {OUTPUT_PATH} — no copy needed.")

    logger.info(f"Mode: {'MOCK' if USE_MOCK else 'LIVE (local CSV)'}")
    logger.info("fetch_data.py completed with no errors.")
    return df


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    fetch_nigeria_conflict_data()