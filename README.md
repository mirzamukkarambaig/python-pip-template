# Inventory and Orders Data Processing Script

A Python script that fetches inventory and orders data from Zambeel API endpoints and uploads the processed data to Google Sheets with comprehensive error handling and logging.

## Features

- **Dual Data Processing**: Handles both orders and inventory data from separate API endpoints
- **Robust Error Handling**: Includes retry logic, timeout handling, and graceful failure recovery
- **Comprehensive Logging**: Timestamped logs with detailed execution tracking
- **Google Sheets Integration**: Direct upload to specified worksheets with configurable positioning
- **Data Type Validation**: Automatic data type conversion with fallback handling
- **Configuration Management**: Centralized configuration with validation

## Prerequisites

### Python Dependencies

```bash
pip install pandas requests gspread gspread-dataframe python-dotenv
```

### Required Files

1. **Configuration Module**: `conf/config.py` - Contains all configuration settings
2. **Google Sheets Credentials**: JSON file with service account credentials
3. **Environment File**: `.env` file with required environment variables

## Project Structure

```
project/
├── main_script.py          # Main processing script
├── conf/
│   ├── config.py          # Configuration settings
│   └── credentials.json   # Google Sheets service account credentials
├── content/
│   └── logs/             # Generated log files
├── .env                  # Environment variables
└── README.md            # This file
```

## Configuration

### Environment Variables (.env)

Create a `.env` file in the project root with the following variables:

```env
ORDERS_API_URL=https://api.zambeel.com/orders
INVENTORY_API_URL=https://api.zambeel.com/inventory
SHEET_NAME=Your Google Sheet Name
ORDERS_WORKSHEET_NAME=Orders
INVENTORY_WORKSHEET_NAME=Inventory
CREDENTIALS_FILE_NAME=credentials.json
```

### Configuration Settings (conf/config.py)

The `config.py` file should include:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
ORDERS_API_URL = os.getenv('ORDERS_API_URL')
INVENTORY_API_URL = os.getenv('INVENTORY_API_URL')

# Google Sheets Configuration
SHEET_NAME = os.getenv('SHEET_NAME')
ORDERS_WORKSHEET_NAME = os.getenv('ORDERS_WORKSHEET_NAME', 'Orders')
INVENTORY_WORKSHEET_NAME = os.getenv('INVENTORY_WORKSHEET_NAME', 'Inventory')
CREDENTIALS_FILE_NAME = os.getenv('CREDENTIALS_FILE_NAME', 'credentials.json')

# Processing Configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Sheet Positioning
ORDERS_START_ROW = 1
ORDERS_START_COL = 1
INVENTORY_START_ROW = 1
INVENTORY_START_COL = 1

def validate_config():
    """Validate that all required configuration is present."""
    required_vars = [
        'ORDERS_API_URL', 'INVENTORY_API_URL', 'SHEET_NAME'
    ]
    
    for var in required_vars:
        if not globals().get(var):
            raise ValueError(f"Missing required configuration: {var}")
```

### Expected Data Schema

#### Orders Data Fields
The orders API returns comprehensive e-commerce order data including:
- **Order Information**: `id`, `order_number`, `Order_date`, `updatedAt`
- **Store Details**: `store_id`, `store_url`
- **Customer Info**: `full_name`, `country`, `city`, `shipping` address
- **Product Details**: `variant_id`, `title`, `sku`, `quantity`
- **Order Status**: `status`, `substatus`, `tag`, `payment_method`
- **Logistics**: `Courier_tracking_id`, `shipment_date`, `approved_date`, `shipment_date_log`
- **Operations**: `OP_remarks`, `Landing_Tag`

#### Inventory Data Fields
The inventory API returns simplified stock information:
- **Product Identifier**: `sku` (Stock Keeping Unit)
- **Stock Level**: `quantity` (Available inventory count)

## Google Sheets Setup

### 1. Create a Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API
4. Create service account credentials
5. Download the JSON credentials file

### 2. Share Your Google Sheet

Share your Google Sheet with the service account email address (found in the credentials JSON file) with "Editor" permissions.

### 3. Credentials File

Place the downloaded JSON credentials file in the `conf/` directory and name it according to your `CREDENTIALS_FILE_NAME` setting.

## Usage

### Basic Execution

```bash
python main_script.py
```

### Expected Data Formats

#### Orders API Response
```json
[
  {
    "id": "",
    "order_number": "",
    "store_id": "",
    "store_url": "",
    "country": "",
    "full_name": "",
    "shipping": "",
    "city": "",
    "variant_id": ,
    "title": "",
    "sku": "",
    "quantity": "",
    "payment_method": ,
    "Courier_tracking_id": "",
    "status": "",
    "substatus": "",
    "tag": "",
    "OP_remarks": "",
    "Order_date": "",
    "updatedAt": "",
    "shipment_date": "",
    "approved_date": "",
    "shipment_date_log": "",
    "Landing_Tag": ""
  }
]
```

#### Inventory API Response
```json
[
  {
    "sku": "",
    "quantity": ""
  }
]
```

## Data Processing Details

### Orders Processing
The script processes orders data with the following field transformations:
- Converts `id` to integer type (primary key)
- Converts `order_number` to string type
- Converts `store_id` to integer type
- Converts `variant_id` to integer type
- Converts `quantity` to integer type
- Preserves string fields: `store_url`, `country`, `full_name`, `shipping`, `city`, `title`, `sku`, `payment_method`, `status`, `substatus`, `tag`, `OP_remarks`
- Handles datetime fields: `Order_date`, `updatedAt`, `shipment_date`, `approved_date`, `shipment_date_log`
- Handles nullable fields: `Courier_tracking_id`, `Landing_Tag`

### Inventory Processing
The script processes inventory data with the following field transformations:
- Converts `sku` to string type (product identifier)
- Converts `quantity` to integer type (stock level)

### Data Validation
- **Orders**: Validates critical fields like `id`, `store_id`, `quantity`, and `variant_id` for proper integer conversion
- **Inventory**: Validates `quantity` field for integer conversion while preserving `sku` as string
- **Error Handling**: Data type conversion errors are logged but don't stop processing
- **Missing Fields**: Script continues processing even if some expected fields are missing

## Logging

### Log File Location
Logs are automatically created in `content/logs/` with timestamp-based filenames:
```
data_processing_YYYYMMDD_HHMMSS.log
```

### Log Levels
- **INFO**: Normal processing steps and status updates
- **WARNING**: Non-critical issues (e.g., data type conversion failures)
- **ERROR**: Critical errors that prevent processing

### Sample Log Output
```
2025-01-15 10:30:15 - INFO - main:45 - STARTING ORDERS AND INVENTORY DATA PROCESSING
2025-01-15 10:30:16 - INFO - fetch_api_data:78 - Fetching orders data from API (attempt 1/3)...
2025-01-15 10:30:17 - INFO - fetch_api_data:85 - Successfully fetched 150 orders records from API
2025-01-15 10:30:18 - INFO - upload_to_google_sheets:215 - ✅ orders DataFrame successfully uploaded to Google Sheet
```

## Troubleshooting

### Common Issues

#### 1. Configuration Errors
```
Error: Could not import config from conf folder
```
**Solution**: Ensure `conf/config.py` exists and contains all required settings.

#### 2. API Connection Issues
```
orders API request failed (attempt 1/3): Connection timeout
```
**Solution**: Check API URLs and network connectivity. The script will automatically retry.

#### 3. Google Sheets Authentication
```
Credentials file not found at: /path/to/credentials.json
```
**Solution**: 
- Verify credentials file exists in `conf/` directory
- Check file permissions
- Ensure service account has access to the Google Sheet

#### 4. Sheet Access Issues
```
Spreadsheet 'Your Sheet Name' not found
```
**Solution**:
- Verify sheet name in configuration
- Ensure service account email has access to the sheet
- Check sheet sharing permissions

### Debug Tips

1. **Check Log Files**: Always review the generated log files for detailed error information
2. **Verify Credentials**: Ensure the service account JSON file is valid and has proper permissions
3. **Test API Endpoints**: Manually test API URLs to verify they're accessible
4. **Environment Variables**: Double-check all environment variables are set correctly

## Advanced Configuration

### Custom Retry Logic
Modify these values in `config.py`:
```python
MAX_RETRIES = 5      # Number of retry attempts
RETRY_DELAY = 10     # Seconds between retries
```

### Custom Sheet Positioning
Position data in specific cells:
```python
ORDERS_START_ROW = 2      # Start at row 2 (skip header)
ORDERS_START_COL = 3      # Start at column C
INVENTORY_START_ROW = 1   # Start at row 1
INVENTORY_START_COL = 1   # Start at column A
```

## Performance Considerations

- **API Timeout**: Default 30-second timeout for API requests
- **Memory Usage**: Large datasets are processed in memory; monitor for very large files
- **Rate Limits**: Google Sheets API has rate limits; the script includes basic error handling

## Security Notes

- Store credentials securely and never commit to version control
- Use environment variables for sensitive configuration
- Regularly rotate service account credentials
- Limit service account permissions to minimum required access

## Support

For issues or questions:
1. Check the generated log files for detailed error information
2. Verify all configuration settings
3. Ensure proper Google Sheets setup and permissions
4. Test API endpoints independently

## License

This script is provided as-is for internal use. Ensure compliance with your organization's data handling policies.