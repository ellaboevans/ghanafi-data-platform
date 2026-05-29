from pathlib import Path
from dotenv import load_dotenv
from os import getenv


load_dotenv()  # Load environment variables from .env file

CONFIG = {
    # Paths
    'input_dir': Path('data/raw'),
    'output_dir': Path('data/processed'),
    'warehouse_dir': Path('data/warehouse'),
    'log_dir': Path('logs'),
    
    # Database Connection
     'database': {
        'host':getenv('DB_HOST', 'localhost'),
        'port': int(getenv('DB_PORT', 3306)),
        'user': getenv('DB_USER'),
        'password':getenv('DB_PASSWORD'),
        'dbname': getenv('DB_NAME', 'ghanafi_db'),
    },
    
    # GhanaFi Business Rules
    'product_lines': [
        'mobile_money',
        'micro_loans',
        'bill_payments',
    ],
    
    'transaction_statuses': [
       "success",
        "failed",
        "pending",
        "reversed",
    ],
    
    # Ghana Regions
    'valid_regions_in_ghana':[
        'Ashanti',
        'Bono',
        'Bono East',
        'Ahafo',
        'Central',
        'Eastern',
        'Greater Accra',
        'Northern',
        'Oti',
        'Upper East',
        'Upper West',
        'Volta',
        'Western',
        'Western North',
        'Savannah',
        'North East'
    ],
    
    # Validation
    'email_regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'phone_regex': r'^\+233\d{9}$',
    'quality_threshold': 0.95,
    
    # Source Priority (lower = more trusted)
    'source_priority': {
        'crm':        1,
        'transaction': 2,
        'loans':       3,
        'app_events':  4,
    },
    
    # Pipeline
    'batch_size': 1000,
    'pipeline_name': "ghanafi_daily_pipeline",
    
}