import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API URLs
ORDERS_API_URL = os.getenv('ORDERS_API_URL')
INVENTORY_API_URL = os.getenv('INVENTORY_API_URL')

# Google Sheets Configuration
CREDENTIALS_FILE_NAME = os.getenv('CREDENTIALS_FILE_NAME')
SHEET_NAME = os.getenv('SHEET_NAME')
ORDERS_WORKSHEET_NAME = os.getenv('ORDERS_WORKSHEET_NAME')
INVENTORY_WORKSHEET_NAME = os.getenv('INVENTORY_WORKSHEET_NAME')

# Retry Configuration
MAX_RETRIES = int(os.getenv('MAX_RETRIES'))
RETRY_DELAY = int(os.getenv('RETRY_DELAY'))

# Spreadsheet positioning
ORDERS_START_ROW = int(os.getenv('ORDERS_START_ROW'))      
ORDERS_START_COL = int(os.getenv('ORDERS_START_COL'))      
INVENTORY_START_ROW = int(os.getenv('INVENTORY_START_ROW')) 
INVENTORY_START_COL = int(os.getenv('INVENTORY_START_COL')) 

# Validation function (optional)
def validate_config():
    """Validate that required environment variables are set."""
    required_vars = ['ORDERS_API_URL', 'INVENTORY_API_URL']
    missing_vars = []
    
    for var in required_vars:
        if not globals().get(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True

# Optional: Validate on import
# validate_config()