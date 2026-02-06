#!/usr/bin/env python
# coding: utf-8
"""
Script to ingest lookup tables (taxi zones, colors) from NYC TLC misc release.

The script:
1. Connects to PostgreSQL database
2. Downloads lookup CSV files from GitHub
3. Inserts them into separate tables for reference
4. Replaces existing tables if they exist
"""

import pandas as pd
from sqlalchemy import create_engine
import click
import sys

# Lookup data from misc release
LOOKUP_FILES = {
    'taxi_zone_lookup': {
        'url': 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv',
        'table_name': 'taxi_zone_lookup'
    },
    'taxi_colors': {
        'url': 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_colors.csv',
        'table_name': 'taxi_colors'
    }
}

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL username')
@click.option('--pg-password', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--data-type', default='all', type=click.Choice(['all', 'zones', 'colors']), help='Which lookup data to ingest')
def run(pg_user, pg_password, pg_host, pg_db, pg_port, data_type):
    """
    Ingest lookup data from NYC TLC misc release into PostgreSQL.
    
    Logic flow:
    1. Test database connection
    2. Based on --data-type option, select which files to ingest
    3. Download and parse each CSV file
    4. Replace existing tables with fresh data
    """
    
    print(f"\n{'='*60}")
    print(f"NYC TLC Lookup Data Ingestion")
    print(f"{'='*60}\n")
    
    # Build connection string
    connection_string = f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}'
    engine = create_engine(connection_string)
    
    # Test connection
    print(f"Connecting to: {pg_host}:{pg_port}/{pg_db}...")
    try:
        with engine.connect() as conn:
            print("✓ Database connection successful!\n")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        sys.exit(1)
    
    # Determine which files to ingest
    files_to_ingest = {}
    
    if data_type == 'all' or data_type == 'zones':
        files_to_ingest['taxi_zone_lookup'] = LOOKUP_FILES['taxi_zone_lookup']
    
    if data_type == 'all' or data_type == 'colors':
        files_to_ingest['taxi_colors'] = LOOKUP_FILES['taxi_colors']
    
    # Ingest each lookup file
    for file_key, file_info in files_to_ingest.items():
        print(f"Processing: {file_key}")
        print(f"URL: {file_info['url']}")
        
        try:
            # Download the CSV
            df = pd.read_csv(file_info['url'])
            print(f"  ✓ Downloaded: {len(df)} rows, {len(df.columns)} columns")
            
            # Ingest to database (replace existing table)
            df.to_sql(
                name=file_info['table_name'],
                con=engine,
                if_exists='replace',
                index=False
            )
            print(f"  ✓ Ingested to table: '{file_info['table_name']}'\n")
            
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            continue
    
    print(f"{'='*60}")
    print("Ingestion complete!")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    run()
