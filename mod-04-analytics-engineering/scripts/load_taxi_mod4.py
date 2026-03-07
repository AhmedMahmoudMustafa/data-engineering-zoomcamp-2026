import os
import sys
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage, bigquery
from google.api_core.exceptions import NotFound

# ==============================
# CONFIGURATION
# ==============================
BUCKET_NAME = "dezoomcamp-ass3-2026"
DATASET_NAME = "nytaxi"
LOCATION = "europe-west2" # <--- This will now be used!
CREDENTIALS_FILE = "gcs.json"

DOWNLOAD_DIR = "data"
CHUNK_SIZE = 8 * 1024 * 1024
TAXI_TYPES = ["yellow", "green"]

# ==============================
# CLIENTS - Added location to the client
# ==============================
storage_client = storage.Client.from_service_account_json(CREDENTIALS_FILE)
bq_client = bigquery.Client.from_service_account_json(CREDENTIALS_FILE, location=LOCATION)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
bucket = storage_client.bucket(BUCKET_NAME)

def create_bucket(bucket_name):
    try:
        storage_client.get_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' exists.")
    except NotFound:
        # Create bucket in the specific region
        new_bucket = storage_client.bucket(bucket_name)
        new_bucket.location = LOCATION
        storage_client.create_bucket(new_bucket)
        print(f"Created bucket '{bucket_name}' in {LOCATION}")

def create_dataset_if_not_exists():
    dataset_id = f"{bq_client.project}.{DATASET_NAME}"
    dataset = bigquery.Dataset(dataset_id)
    
    # 🔥 FIXED: Explicitly setting the physical location of the dataset
    dataset.location = LOCATION 
    
    # exists_ok=True prevents errors if it's already there
    bq_client.create_dataset(dataset, exists_ok=True) 
    print(f"Dataset '{DATASET_NAME}' is confirmed in {LOCATION}.")

# ==============================
# UPLOAD TO GCS (Unchanged)
# ==============================
def upload_to_gcs(file_path):
    blob_name = os.path.basename(file_path)
    blob = bucket.blob(blob_name)
    blob.chunk_size = CHUNK_SIZE
    print(f"Uploading {blob_name} to GCS...")
    blob.upload_from_filename(file_path)

# ==============================
# LOAD TO BIGQUERY (Unchanged logic)
# ==============================
def load_to_bigquery(taxi_type):
    table_id = f"{bq_client.project}.{DATASET_NAME}.{taxi_type}_tripdata"
    uri = f"gs://{BUCKET_NAME}/{taxi_type}_tripdata_*.parquet"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    print(f"Starting BigQuery bulk load for {taxi_type}...")
    try:
        # Client initialized with location will handle the job in europe-west2
        load_job = bq_client.load_table_from_uri(uri, table_id, job_config=job_config)
        load_job.result() 
        
        table = bq_client.get_table(table_id)
        print(f"SUCCESS: Loaded {taxi_type}. Rows: {table.num_rows} in {table.location}")
    except Exception as e:
        print(f"ERROR: Failed to load {taxi_type}: {e}")

if __name__ == "__main__":
    create_bucket(BUCKET_NAME)
    create_dataset_if_not_exists()

    # Get local files from your existing 'data' folder
    file_paths = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".parquet")]
    
    if not file_paths:
        print("Error: No .parquet files found in the 'data' folder!")
    else:
        print(f"Found {len(file_paths)} local files. Starting upload...")
        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(upload_to_gcs, file_paths)

        print("All uploads finished. Starting BigQuery ingestion...")
        for taxi_type in TAXI_TYPES:
            load_to_bigquery(taxi_type)

    print("Pipeline complete.")