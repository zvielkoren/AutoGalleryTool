
from datetime import datetime

def extract_date(filename):
    # Assuming file name contains date in YYYYMMDD format
    return datetime.now().strftime("%Y-%m-%d")
