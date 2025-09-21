# -*- coding: utf-8 -*-
"""
Inventory and Orders Data Processing Script
Fetches data from Zambeel API for both orders and inventory, then uploads to Google Sheets 
with error handling and logging.

Original file is located at:
    https://colab.research.google.com/drive/1peuajyInnS2Lh7L1LCm-V86fdiAVpln5
"""

import logging
import sys
import time
import os
import pandas as pd
import requests
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

try:
    from conf import config
    
    # Validate configuration on startup
    config.validate_config()
    
except ImportError as e:
    print(f"Error: Could not import config from conf folder: {e}")
    print("Please ensure config.py exists in the conf/ directory")
    sys.exit(1)
except ValueError as e:
    print(f"Configuration error: {e}")
    print("Please check your .env file and ensure all required variables are set")
    sys.exit(1)


# Configure logging with timestamp-based filename
log_filename = f"data_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_directory = os.path.join("content", "logs")

# Create logs directory if it doesn't exist
os.makedirs(log_directory, exist_ok=True)
log_filepath = os.path.join(log_directory, log_filename)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler(log_filepath, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Log the log file location at startup
logger.info(f"Log file created at: {log_filepath}")

# Configuration constants
ORDERS_API_URL = config.ORDERS_API_URL
INVENTORY_API_URL = config.INVENTORY_API_URL
CREDENTIALS_FILE = os.path.join("conf", config.CREDENTIALS_FILE_NAME)
SHEET_NAME = config.SHEET_NAME
ORDERS_WORKSHEET_NAME = config.ORDERS_WORKSHEET_NAME
INVENTORY_WORKSHEET_NAME = config.INVENTORY_WORKSHEET_NAME
MAX_RETRIES = config.MAX_RETRIES
RETRY_DELAY = config.RETRY_DELAY 

ORDERS_START_ROW = config.ORDERS_START_ROW      
ORDERS_START_COL = config.ORDERS_START_COL      
INVENTORY_START_ROW = config.INVENTORY_START_ROW   
INVENTORY_START_COL = config.INVENTORY_START_COL   


def fetch_api_data(url: str, data_type: str, max_retries: int = MAX_RETRIES) -> Optional[Dict[Any, Any]]:
    """
    Fetch data from API with retry logic and error handling.
    
    Args:
        url: API endpoint URL
        data_type: Type of data being fetched (for logging)
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dict containing API response data or None if failed
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching {data_type} data from API (attempt {attempt + 1}/{max_retries})...")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()  # Raises HTTPError for bad responses
            
            data = response.json()
            logger.info(f"Successfully fetched {len(data)} {data_type} records from API")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"{data_type} API request failed (attempt {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"Max retries reached. {data_type} API fetch failed.")
                
        except ValueError as e:
            logger.error(f"Failed to parse JSON response for {data_type}: {e}")
            break
        except Exception as e:
            logger.error(f"Unexpected error during {data_type} API fetch: {e}")
            break
    
    return None


def process_orders_dataframe(data: Dict[Any, Any]) -> Optional[pd.DataFrame]:
    """
    Convert orders API data to DataFrame and apply data type conversions.
    
    Args:
        data: Raw orders data from API
        
    Returns:
        Processed pandas DataFrame or None if processing failed
    """
    try:
        logger.info("Converting orders data to DataFrame...")
        df = pd.DataFrame(data)
        
        if df.empty:
            logger.warning("Orders DataFrame is empty")
            return None
        
        logger.info(f"Orders DataFrame created with shape: {df.shape}")
        logger.info(f"Orders columns: {list(df.columns)}")
        
        # Apply data type conversions with error handling for orders
        conversions = {
            'order_id': str,
            'store_id': int,
            'quantity': int
        }
        
        for column, dtype in conversions.items():
            if column in df.columns:
                try:
                    df[column] = df[column].astype(dtype)
                    logger.info(f"Successfully converted orders {column} to {dtype.__name__}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to convert orders {column} to {dtype.__name__}: {e}")
                    # Continue with original data type
            else:
                logger.info(f"Orders column '{column}' not found in data")
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing orders DataFrame: {e}")
        return None


def process_inventory_dataframe(data: Dict[Any, Any]) -> Optional[pd.DataFrame]:
    """
    Convert inventory API data to DataFrame and apply data type conversions.
    
    Args:
        data: Raw inventory data from API
        
    Returns:
        Processed pandas DataFrame or None if processing failed
    """
    try:
        logger.info("Converting inventory data to DataFrame...")
        df = pd.DataFrame(data)
        
        if df.empty:
            logger.warning("Inventory DataFrame is empty")
            return None
        
        logger.info(f"Inventory DataFrame created with shape: {df.shape}")
        logger.info(f"Inventory columns: {list(df.columns)}")
        
        # Apply data type conversions with error handling for inventory
        conversions = {
            'store_id': int,
            'quantity': int
        }
        
        for column, dtype in conversions.items():
            if column in df.columns:
                try:
                    df[column] = df[column].astype(dtype)
                    logger.info(f"Successfully converted inventory {column} to {dtype.__name__}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to convert inventory {column} to {dtype.__name__}: {e}")
                    # Continue with original data type
            else:
                logger.info(f"Inventory column '{column}' not found in data")
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing inventory DataFrame: {e}")
        return None


def upload_to_google_sheets(df: pd.DataFrame, credentials_file: str, 
                          sheet_name: str, worksheet_name: str, 
                          start_row: int, start_col: int, data_type: str) -> bool:
    """
    Upload DataFrame to Google Sheets with error handling.
    
    Args:
        df: DataFrame to upload
        credentials_file: Path to Google Sheets credentials JSON file
        sheet_name: Name of the Google Sheet
        worksheet_name: Name of the worksheet within the sheet
        start_row: Starting row position (A=1)
        start_col: Starting column position
        data_type: Type of data being uploaded (for logging)
        
    Returns:
        True if upload successful, False otherwise
    """
    try:
        logger.info(f"Importing Google Sheets libraries for {data_type}...")
        import gspread
        from gspread_dataframe import set_with_dataframe
        
        # Validate credentials file path
        abs_credentials_path = os.path.abspath(credentials_file)
        logger.info(f"Checking credentials file for {data_type}: {abs_credentials_path}")
        
        if not os.path.exists(abs_credentials_path):
            logger.error(f"Credentials file not found at: {abs_credentials_path}")
            logger.info("Please ensure the credentials file exists and the path is correct")
            
            # Also check in current directory
            current_dir_path = os.path.join(os.getcwd(), os.path.basename(credentials_file))
            logger.info(f"Checking in current directory: {current_dir_path}")
            
            if os.path.exists(current_dir_path):
                logger.info(f"Found credentials file in current directory: {current_dir_path}")
                credentials_file = current_dir_path
            else:
                logger.error("Credentials file not found in current directory either")
                return False
        else:
            credentials_file = abs_credentials_path
        
        logger.info(f"Using credentials file for {data_type}: {credentials_file}")
        logger.info(f"Authenticating with Google Sheets for {data_type}...")
        gc = gspread.service_account(filename=credentials_file)
        
        logger.info(f"Opening Google Sheet for {data_type}: {sheet_name}")
        sh = gc.open(sheet_name)
        
        # Try to get the specific worksheet, create if it doesn't exist
        try:
            worksheet = sh.worksheet(worksheet_name)
            logger.info(f"Found existing worksheet: {worksheet_name}")
        except gspread.WorksheetNotFound:
            logger.info(f"Worksheet '{worksheet_name}' not found. Creating new worksheet...")
            worksheet = sh.add_worksheet(title=worksheet_name, rows=1000, cols=20)
        
        logger.info(f"Clearing existing {data_type} data...")
        worksheet.clear()
        
        # Convert column number to letter for logging
        col_letter = chr(64 + start_col)  # A=1, B=2, etc.
        logger.info(f"Uploading {data_type} DataFrame to Google Sheets at row {start_row}, column {start_col} ({col_letter})...")
        set_with_dataframe(worksheet, df, row=start_row, col=start_col)
        
        logger.info(f"✅ {data_type} DataFrame successfully uploaded to Google Sheet '{sheet_name}' -> '{worksheet_name}'")
        logger.info(f"   Uploaded {len(df)} {data_type} rows and {len(df.columns)} columns")
        
        return True
        
    except gspread.exceptions.APIError as e:
        logger.error(f"Google Sheets API error for {data_type}: {e}")
        return False
    except gspread.exceptions.SpreadsheetNotFound:
        logger.error(f"Spreadsheet '{sheet_name}' not found. Please check the name and permissions.")
        return False
    except FileNotFoundError as e:
        logger.error(f"Credentials file not found for {data_type}: {e}")
        logger.info(f"Expected path: {os.path.abspath(credentials_file)}")
        logger.info(f"Current working directory: {os.getcwd()}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during {data_type} Google Sheets upload: {e}")
        logger.info(f"Credentials file path being used: {repr(os.path.abspath(credentials_file))}")
        logger.info(f"Current working directory: {os.getcwd()}")
        return False


def process_orders() -> bool:
    """
    Process orders data: fetch, convert to DataFrame, and upload to Google Sheets.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("🔄 STARTING ORDERS PROCESSING")
    logger.info("-" * 50)
    
    # Fetch orders data from API
    orders_data = fetch_api_data(ORDERS_API_URL, "orders")
    if orders_data is None:
        logger.error("Failed to fetch orders data from API")
        return False
    
    # Process orders data into DataFrame
    orders_df = process_orders_dataframe(orders_data)
    if orders_df is None:
        logger.error("Failed to process orders data")
        return False
    
    # Upload orders to Google Sheets
    orders_success = upload_to_google_sheets(
        df=orders_df,
        credentials_file=CREDENTIALS_FILE,
        sheet_name=SHEET_NAME,
        worksheet_name=ORDERS_WORKSHEET_NAME,
        start_row=ORDERS_START_ROW,
        start_col=ORDERS_START_COL,
        data_type="orders"
    )
    
    if orders_success:
        logger.info("✅ Orders processing completed successfully!")
        logger.info("-" * 50)
        return True
    else:
        logger.error("❌ Failed to upload orders data to Google Sheets")
        logger.info("-" * 50)
        return False


def process_inventory() -> bool:
    """
    Process inventory data: fetch, convert to DataFrame, and upload to Google Sheets.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("🔄 STARTING INVENTORY PROCESSING")
    logger.info("-" * 50)
    
    # Fetch inventory data from API
    inventory_data = fetch_api_data(INVENTORY_API_URL, "inventory")
    if inventory_data is None:
        logger.error("Failed to fetch inventory data from API")
        return False
    
    # Process inventory data into DataFrame
    inventory_df = process_inventory_dataframe(inventory_data)
    if inventory_df is None:
        logger.error("Failed to process inventory data")
        return False
    
    # Upload inventory to Google Sheets
    inventory_success = upload_to_google_sheets(
        df=inventory_df,
        credentials_file=CREDENTIALS_FILE,
        sheet_name=SHEET_NAME,
        worksheet_name=INVENTORY_WORKSHEET_NAME,
        start_row=INVENTORY_START_ROW,
        start_col=INVENTORY_START_COL,
        data_type="inventory"
    )
    
    if inventory_success:
        logger.info("✅ Inventory processing completed successfully!")
        logger.info("-" * 50)
        return True
    else:
        logger.error("❌ Failed to upload inventory data to Google Sheets")
        logger.info("-" * 50)
        return False


def main():
    """Main execution function with comprehensive error handling."""
    try:
        logger.info("=" * 80)
        logger.info("STARTING ORDERS AND INVENTORY DATA PROCESSING")
        logger.info("=" * 80)
        logger.info(f"Script started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Process orders first
        orders_success = process_orders()
        
        # Process inventory second
        inventory_success = process_inventory()
        
        # Final status
        if orders_success and inventory_success:
            logger.info("🎉 ALL DATA PROCESSING COMPLETED SUCCESSFULLY!")
            logger.info("   ✅ Orders data updated successfully")
            logger.info("   ✅ Inventory data updated successfully")
            logger.info(f"Script completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 80)
            return True
        else:
            logger.error("❌ DATA PROCESSING COMPLETED WITH ERRORS:")
            logger.info(f"   Orders: {'✅ Success' if orders_success else '❌ Failed'}")
            logger.info(f"   Inventory: {'✅ Success' if inventory_success else '❌ Failed'}")
            logger.info(f"Script completed with errors at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 80)
            return False
            
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        logger.info(f"Script interrupted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")
        logger.info(f"Script failed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return False


if __name__ == "__main__":
    from time import time
    start = time()
    success = main()
    end = time()
    logger.info(f"Total execution time: {end - start:.2f} seconds")
    logger.info(f"Check detailed logs at: {os.path.abspath(log_filepath)}")
    sys.exit(0 if success else 1)