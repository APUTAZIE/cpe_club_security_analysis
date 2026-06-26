# ============================================================
# fetch_data.py
# Step 3 — Data Gathering Script
# Branch: feature/data-gathering
#
# What this script does:
#   1. Connects to the ACLED API (or uses mock data if USE_MOCK = True)
#   2. Requests conflict data filtered to Nigeria
#   3. Saves the result as a CSV file in the data/ folder
#   4. If anything goes wrong, it logs the error and stops
# ============================================================

# --- Import the libraries we need ---

import requests   # used to make HTTP requests (like a browser, but in Python)
import logging    # used to print log messages with timestamps and levels
import os         # used to check if folders exist and create them
import sys        # used to exit the script if there is a fatal error

# pandas helps us work with tabular data (like a spreadsheet in Python)
import pandas as pd

# io lets us treat a string of text as if it were a file
# we need this to read the CSV text the API sends back
import io


# ============================================================
# MOCK SWITCH — Change this one line to switch modes
# ============================================================

# Set USE_MOCK = True  → runs without credentials (uses fake data)
# Set USE_MOCK = False → hits the real ACLED API (needs real credentials)
USE_MOCK = True


# ============================================================
# CONFIGURATION — Put your ACLED credentials here
# ============================================================

# Your registered ACLED email address
ACLED_EMAIL = "your_email@example.com"

# Your ACLED API key (get it from: https://developer.acleddata.com/)
ACLED_API_KEY = "your_api_key_here"

# The base URL for the ACLED API
# All requests go to this endpoint
ACLED_API_URL = "https://api.acleddata.com/acled/read"

# The country we want data for
TARGET_COUNTRY = "Nigeria"

# Where we want to save the downloaded file
# The folder "data/" will be created if it does not exist yet
OUTPUT_FOLDER = "data"
OUTPUT_FILENAME = "raw_nigeria_conflict.csv"

# Build the full file path by joining the folder and filename
# Result: "data/raw_nigeria_conflict.csv"
OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, OUTPUT_FILENAME)


# ============================================================
# MOCK DATA — Fake Nigeria conflict rows for testing
# ============================================================

# This is a small sample that looks exactly like real ACLED CSV output
# It is only used when USE_MOCK = True
# When you switch to USE_MOCK = False, this block is completely ignored
MOCK_CSV_DATA = """event_id_cnty,event_date,year,event_type,sub_event_type,actor1,country,admin1,admin2,location,latitude,longitude,fatalities,notes
NGA2024001,2024-01-15,2024,Violence against civilians,Attack,Boko Haram,Nigeria,Borno,Bama,Bama,11.5204,13.6903,3,Armed group attacked a civilian settlement in Bama
NGA2024002,2024-01-20,2024,Battles,Armed clash,Nigerian Military,Nigeria,Zamfara,Gusau,Gusau,12.1704,6.6649,12,Clash between military and bandits near Gusau
NGA2024003,2024-02-01,2024,Explosions/Remote violence,Suicide bomb,ISWAP,Nigeria,Adamawa,Yola,Yola,9.2035,12.4954,5,Suicide bombing at a market in Yola
NGA2024004,2024-02-14,2024,Riots,Violent demonstration,Protesters,Nigeria,Lagos,Lagos Island,Lagos,6.4541,3.3947,0,Protest turned violent near Lagos Island
NGA2024005,2024-03-05,2024,Violence against civilians,Abduction/forced disappearance,Unknown,Nigeria,Kaduna,Zaria,Zaria,11.1112,7.7227,1,Gunmen abducted several farmers outside Zaria
"""


# ============================================================
# LOGGING SETUP
# ============================================================

# basicConfig sets up the logging system for us
# - level=INFO means we see INFO, WARNING, and ERROR messages
# - format includes the time, log level, and the message
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Create a logger for this script
# Using __name__ means the logger is named after this file
logger = logging.getLogger(__name__)


# ============================================================
# HELPER FUNCTION — Make sure the output folder exists
# ============================================================

def ensure_output_folder(folder_path):
    """
    Check if the output folder exists.
    If it does not exist, create it.

    Args:
        folder_path (str): The path to the folder we want to use.
    """

    # os.path.exists() returns True if the folder is already there
    if not os.path.exists(folder_path):
        # The folder is missing, so we create it
        logger.info(f"Output folder '{folder_path}' not found. Creating it now...")

        # os.makedirs() creates the folder (and any parent folders needed)
        os.makedirs(folder_path)

        logger.info(f"Folder '{folder_path}' created successfully.")
    else:
        # Folder already exists, nothing to do
        logger.info(f"Output folder '{folder_path}' already exists. OK.")


# ============================================================
# MOCK FUNCTION — Return fake data instead of calling the API
# ============================================================

def get_mock_response():
    """
    Simulates what the ACLED API would return.
    Returns the mock CSV string so the rest of the script
    can process it exactly the same way as real data.
    """

    logger.info("--------------------------------------------------")
    logger.info("  MOCK MODE IS ON (USE_MOCK = True)")
    logger.info("  Skipping real API call — using fake data instead")
    logger.info("  To use the real API, set USE_MOCK = False")
    logger.info("--------------------------------------------------")

    # Return the fake CSV data defined at the top of this file
    return MOCK_CSV_DATA


# ============================================================
# REAL FETCH FUNCTION — Hit the actual ACLED API
# ============================================================

def get_real_response():
    """
    Sends a real GET request to the ACLED API.
    Returns the response text (CSV string) if successful.
    Logs an error and exits if the request fails.
    """

    logger.info("--------------------------------------------------")
    logger.info("  LIVE MODE IS ON (USE_MOCK = False)")
    logger.info("  Sending real request to the ACLED API...")
    logger.info("--------------------------------------------------")

    # Build the query parameters for the API request
    # Each key maps to a field the API understands
    params = {
        "email":       ACLED_EMAIL,      # your account email
        "key":         ACLED_API_KEY,    # your API key for authentication
        "country":     TARGET_COUNTRY,   # filter: only Nigeria events
        "export_type": "csv",            # tell the API we want CSV format back
        "limit":       0,                # limit=0 means "give me ALL records"
    }

    logger.info(f"Query parameters: country={TARGET_COUNTRY}, export_type=csv, limit=0")
    logger.info(f"Sending GET request to: {ACLED_API_URL}")

    # We wrap the request in a try/except block
    # If anything goes wrong, the except block catches it, logs it, and exits
    try:
        # requests.get() sends the HTTP GET request
        # timeout=60 means give up if the server doesn't respond in 60 seconds
        response = requests.get(ACLED_API_URL, params=params, timeout=60)

        # raise_for_status() throws an error if we got a 4xx or 5xx response
        response.raise_for_status()

    except requests.exceptions.ConnectionError as e:
        # Cannot reach the server at all (no internet, wrong URL, DNS failure)
        logger.error(f"Connection error — could not reach the ACLED API: {e}")
        logger.error("Check your internet connection and try again.")
        sys.exit(1)

    except requests.exceptions.Timeout as e:
        # Server took too long to respond
        logger.error(f"Request timed out after 60 seconds: {e}")
        logger.error("The ACLED server might be slow. Try again later.")
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        # Server responded but with an error code (401, 403, 500, etc.)
        logger.error(f"HTTP error from ACLED API: {e}")
        logger.error(f"Response status code: {response.status_code}")
        logger.error(f"Response body: {response.text[:500]}")
        sys.exit(1)

    except requests.exceptions.RequestException as e:
        # Catch-all for any other requests-related error
        logger.error(f"Unexpected error during the API request: {e}")
        sys.exit(1)

    # Request was successful
    logger.info(f"API request successful. HTTP status: {response.status_code}")
    logger.info(f"Response size: {len(response.content)} bytes")

    # Return the raw CSV text so the main function can process it
    return response.text


# ============================================================
# MAIN FUNCTION — Orchestrates everything
# ============================================================

def fetch_nigeria_conflict_data():
    """
    Main function that runs the full pipeline:
      1. Decides whether to use mock data or the real API
      2. Gets the CSV text (from mock or real source)
      3. Parses it into a DataFrame
      4. Saves it to data/raw_nigeria_conflict.csv
    """

    logger.info("Starting ACLED data fetch for Nigeria...")

    # ----------------------------------------------------------
    # Step A — Get the CSV text (mock or real, depending on switch)
    # ----------------------------------------------------------

    # This is the only place where USE_MOCK is checked
    # Everything after this point works the same regardless of the mode
    if USE_MOCK:
        # Call the mock function — no internet or credentials needed
        response_text = get_mock_response()
    else:
        # Call the real API function — needs valid credentials above
        response_text = get_real_response()

    # ----------------------------------------------------------
    # Step B — Parse the CSV text into a pandas DataFrame
    # ----------------------------------------------------------

    logger.info("Parsing response content as CSV...")

    try:
        # io.StringIO() wraps the text string so pd.read_csv() can read it
        # as if it were an actual file on disk
        dataframe = pd.read_csv(io.StringIO(response_text))

    except Exception as e:
        # If pandas cannot parse it as CSV, log the error and exit
        logger.error(f"Failed to parse the response as CSV: {e}")
        logger.error(f"First 500 characters of response: {response_text[:500]}")
        sys.exit(1)

    # Log a quick summary of what we parsed
    row_count, col_count = dataframe.shape   # .shape gives us (rows, columns)
    logger.info(f"CSV parsed successfully: {row_count} rows, {col_count} columns.")
    logger.info(f"Columns in dataset: {list(dataframe.columns)}")

    # ----------------------------------------------------------
    # Step C — Make sure the output folder exists, then save
    # ----------------------------------------------------------

    # Create the data/ folder if it does not exist yet
    ensure_output_folder(OUTPUT_FOLDER)

    logger.info(f"Saving data to: {OUTPUT_PATH}")

    try:
        # to_csv() writes the DataFrame to a CSV file
        # index=False means we skip the auto-generated row numbers
        dataframe.to_csv(OUTPUT_PATH, index=False)

    except Exception as e:
        # Could not write the file (e.g. permission denied)
        logger.error(f"Failed to save CSV file to '{OUTPUT_PATH}': {e}")
        sys.exit(1)

    # All done
    logger.info(f"Data saved successfully to '{OUTPUT_PATH}'.")
    logger.info(f"Mode used: {'MOCK' if USE_MOCK else 'LIVE'}")
    logger.info("fetch_data.py completed with no errors.")


# ============================================================
# ENTRY POINT
# ============================================================

# This block runs only when we execute the script directly:
#   python fetch_data.py
#
# It does NOT run if another script imports this file as a module.

if __name__ == "__main__":
    fetch_nigeria_conflict_data()

