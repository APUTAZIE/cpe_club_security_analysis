# Must Read File

# Data Gathering

The data gathering module fetches armed conflict event records for Nigeria from the ACLED API and stores the raw dataset locally for further processing.
The script accepts credentials via configuration constants and constructs a parameterized GET request targeting Nigeria as the country filter with no record limit, ensuring the full dataset is retrieved. On a successful response, the data is parsed and written to data/raw_nigeria_conflict.csv. The data/ directory is created automatically if it does not already exist.
Error handling is implemented at every stage of the request lifecycle. Network failures, timeouts, and non-2xx HTTP responses are each caught separately, logged with a descriptive message, and cause the script to exit with a non-zero status code rather than fail silently.
A USE_MOCK flag is provided for development and testing environments where API credentials are unavailable. When enabled, the script substitutes a locally defined sample dataset that mirrors the structure of a real ACLED response, allowing the full pipeline to be exercised without an active API connection.

# Usage

`python3 -m venv venv
source venv/bin/activate
pip install requests pandas
python3 fetch_data.py`

# Output
data/raw_nigeria_conflict.csv — raw conflict event records for Nigeria.
