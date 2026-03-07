import os
import pandas as pd
from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- CONFIGURATION ---
PROJECT_ID = "module3-datawarehouse" 
DATASET_ID = "nytaxi"
LOCATION = "europe-west2"  # London Region
TABLE_ID = "fhv_tripdata"
BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/"
YEAR = 2019
MONTHS = range(1, 13)
MAX_WORKERS = 4 

client = bigquery.Client(project=PROJECT_ID, location=LOCATION)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

def create_dataset_if_not_exists():
    dataset_ref = client.dataset(DATASET_ID)
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {DATASET_ID} already exists.")
    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = LOCATION
        dataset = client.create_dataset(dataset)
        print(f"Created dataset {DATASET_ID} in {LOCATION}")

def load_month(month):
    file_name = f"fhv_tripdata_{YEAR}-{month:02d}.csv.gz"
    url = f"{BASE_URL}{file_name}"
    
    try:
        print(f"Processing {file_name}...")
        # Force string/float for IDs to prevent BigQuery schema mismatches
        df = pd.read_csv(url, compression='gzip', dtype={
            'PUlocationID': 'float64', 
            'DOlocationID': 'float64',
            'SR_Flag': 'float64'
        })
        
        # Load to BigQuery
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
        client.load_table_from_dataframe(df, table_ref, job_config=job_config).result()
        return f"✅ Finished {file_name}"
    except Exception as e:
        return f"❌ Failed {file_name}: {e}"

def main():
    create_dataset_if_not_exists()
    print(f"Starting upload for {YEAR} FHV data to {table_ref}...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(load_month, m) for m in MONTHS]
        for future in as_completed(futures):
            print(future.result())

if __name__ == "__main__":
    main()