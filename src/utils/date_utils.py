
from datetime import datetime

def extract_date():
    # Assuming file name contains date in YYYYMMDD format
    return datetime.now().strftime("%Y-%m-%d")
