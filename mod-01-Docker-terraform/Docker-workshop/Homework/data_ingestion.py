import click
import pandas as pd
from sqlalchemy import create_engine


@click.command()
@click.option('--pg-user', default='postgres')
@click.option('--pg-password', default='postgres')
@click.option('--pg-host', default='localhost')
@click.option('--pg-port', default=5433, type=int)
@click.option('--pg-db', default='ny_taxi')
@click.option('--chunksize', default=100_000, type=int)
@click.option('--data-dir', default='data')
def run(pg_user, pg_password, pg_host, pg_port, pg_db, chunksize, data_dir):
    """
    Load green taxi parquet and taxi zone lookup CSV into Postgres
    """

    engine = create_engine(
        f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
    )

    # -------------------------
    # Green taxi trips
    # -------------------------
    parquet_path = f"{data_dir}/green_tripdata_2025-11.parquet"
    print(f"Reading parquet file: {parquet_path}")

    df = pd.read_parquet(parquet_path)

    # REQUIRED datetime conversions
    df["lpep_pickup_datetime"] = pd.to_datetime(df["lpep_pickup_datetime"])
    df["lpep_dropoff_datetime"] = pd.to_datetime(df["lpep_dropoff_datetime"])

    print("Creating table green_taxi_trips")
    df.head(0).to_sql(
        name="green_taxi_trips",
        con=engine,
        if_exists="replace",
        index=False
    )

    print("Inserting green taxi data")
    for start in range(0, len(df), chunksize):
        chunk = df.iloc[start:start + chunksize]
        chunk.to_sql(
            name="green_taxi_trips",
            con=engine,
            if_exists="append",
            index=False
        )
        print(f"Inserted {len(chunk)} rows")

    # -------------------------
    # Taxi zones lookup
    # -------------------------
    zones_path = f"{data_dir}/taxi_zone_lookup.csv"
    print(f"Reading zones file: {zones_path}")

    df_zones = pd.read_csv(zones_path)

    print("Creating table zones")
    df_zones.to_sql(
        name="zones",
        con=engine,
        if_exists="replace",
        index=False
    )

    print("✅ Data ingestion completed successfully")


if __name__ == "__main__":
    run()
