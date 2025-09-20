# -*- coding: utf-8 -*-
"""
Inventory Data Processing Script
Fetches data from Zambeel API and uploads to Google Sheets with error handling and logging.

Original file is located at:
    https://colab.research.google.com/drive/1peuajyInnS2Lh7L1LCm-V86fdiAVpln5
"""

import logging
import sys
import time
import os
import pandas as pd
import requests
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging with timestamp-based filename
log_filename = f"inventory_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
API_URL = 'https://zambeel.metabaseapp.com/public/question/ed44bf75-b9e2-42be-b5ff-28aaf54b999d.json'
CREDENTIALS_FILE = os.path.join("conf", "testing-addam-api-f66ba39e4c8c.json")
SHEET_NAME = "testing-addam-api"
WORKSHEET_NAME = "inventory"
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Google Sheets positioning
START_ROW = 1  # Row A
START_COL = 4  # Column D





def fetch_api_data(url: str, max_retries: int = MAX_RETRIES) -> Optional[Dict[Any, Any]]:
    """
    Fetch data from API with retry logic and error handling.
    
    Args:
        url: API endpoint URL
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dict containing API response data or None if failed
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching data from API (attempt {attempt + 1}/{max_retries})...")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()  # Raises HTTPError for bad responses
            
            data = response.json()
            logger.info(f"Successfully fetched {len(data)} records from API")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"API request failed (attempt {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error("Max retries reached. API fetch failed.")
                
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            break
        except Exception as e:
            logger.error(f"Unexpected error during API fetch: {e}")
            break
    
    return None


def process_dataframe(data: Dict[Any, Any]) -> Optional[pd.DataFrame]:
    """
    Convert API data to DataFrame and apply data type conversions.
    
    Args:
        data: Raw data from API
        
    Returns:
        Processed pandas DataFrame or None if processing failed
    """
    try:
        logger.info("Converting data to DataFrame...")
        df = pd.DataFrame(data)
        
        if df.empty:
            logger.warning("DataFrame is empty")
            return None
        
        logger.info(f"DataFrame created with shape: {df.shape}")
        logger.info(f"Columns: {list(df.columns)}")
        
        # Apply data type conversions with error handling
        conversions = {
            'store_id': int,
            'quantity': int
        }
        
        for column, dtype in conversions.items():
            if column in df.columns:
                try:
                    df[column] = df[column].astype(dtype)
                    logger.info(f"Successfully converted {column} to {dtype.__name__}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to convert {column} to {dtype.__name__}: {e}")
                    # Continue with original data type
            else:
                logger.info(f"Column '{column}' not found in data")
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing DataFrame: {e}")
        return None


def upload_to_google_sheets(df: pd.DataFrame, credentials_file: str, 
                          sheet_name: str, worksheet_name: str, 
                          start_row: int = START_ROW, start_col: int = START_COL) -> bool:
    """
    Upload DataFrame to Google Sheets with error handling.
    
    Args:
        df: DataFrame to upload
        credentials_file: Path to Google Sheets credentials JSON file
        sheet_name: Name of the Google Sheet
        worksheet_name: Name of the worksheet within the sheet
        start_row: Starting row position (A=1)
        start_col: Starting column position (D=4)
        
    Returns:
        True if upload successful, False otherwise
    """
    try:
        logger.info("Importing Google Sheets libraries...")
        import gspread
        from gspread_dataframe import set_with_dataframe
        
        # Validate credentials file path
        abs_credentials_path = os.path.abspath(credentials_file)
        logger.info(f"Checking credentials file: {abs_credentials_path}")
        
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
        
        logger.info(f"Using credentials file: {credentials_file}")
        logger.info("Authenticating with Google Sheets...")
        gc = gspread.service_account(filename=credentials_file)
        
        logger.info(f"Opening Google Sheet: {sheet_name}")
        sh = gc.open(sheet_name)
        
        # Try to get the specific worksheet, create if it doesn't exist
        try:
            worksheet = sh.worksheet(worksheet_name)
            logger.info(f"Found existing worksheet: {worksheet_name}")
        except gspread.WorksheetNotFound:
            logger.info(f"Worksheet '{worksheet_name}' not found. Creating new worksheet...")
            worksheet = sh.add_worksheet(title=worksheet_name, rows=1000, cols=20)
        
        logger.info("Clearing existing data...")
        worksheet.clear()
        
        logger.info(f"Uploading DataFrame to Google Sheets at row {start_row} (A), column {start_col} (D)...")
        set_with_dataframe(worksheet, df, row=start_row, col=start_col)
        
        logger.info(f"✅ DataFrame successfully uploaded to Google Sheet '{sheet_name}' -> '{worksheet_name}'")
        logger.info(f"   Uploaded {len(df)} rows and {len(df.columns)} columns")
        
        return True
        
    except gspread.exceptions.APIError as e:
        logger.error(f"Google Sheets API error: {e}")
        return False
    except gspread.exceptions.SpreadsheetNotFound:
        logger.error(f"Spreadsheet '{sheet_name}' not found. Please check the name and permissions.")
        return False
    except FileNotFoundError as e:
        logger.error(f"Credentials file not found: {e}")
        logger.info(f"Expected path: {os.path.abspath(credentials_file)}")
        logger.info(f"Current working directory: {os.getcwd()}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during Google Sheets upload: {e}")
        logger.info(f"Credentials file path being used: {repr(os.path.abspath(credentials_file))}")
        logger.info(f"Current working directory: {os.getcwd()}")
        return False


def main():
    """Main execution function with comprehensive error handling."""
    try:
        logger.info("=" * 80)
        logger.info("STARTING INVENTORY DATA PROCESSING")
        logger.info("=" * 80)
        logger.info(f"Script started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Fetch data from API
        data = fetch_api_data(API_URL)
        if data is None:
            logger.error("Failed to fetch data from API. Exiting.")
            return False
        
        # Process data into DataFrame
        df = process_dataframe(data)
        if df is None:
            logger.error("Failed to process data. Exiting.")
            return False
        
        # Upload to Google Sheets
        success = upload_to_google_sheets(
            df=df,
            credentials_file=CREDENTIALS_FILE,
            sheet_name=SHEET_NAME,
            worksheet_name=WORKSHEET_NAME
        )
        
        if success:
            logger.info("✅ Inventory data processing completed successfully!")
            logger.info(f"Script completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 80)
            return True
        else:
            logger.error("❌ Failed to upload data to Google Sheets")
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
    success = main()
    logger.info(f"Check detailed logs at: {os.path.abspath(log_filepath)}")
    sys.exit(0 if success else 1)