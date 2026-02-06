# Module 1 Homework: Docker & SQL

This repository contains my solutions for **Module 1 Homework – Docker & SQL** from the Data Engineering Zoomcamp 2026.

---

## Question 1. Understanding Docker images

Run docker with the `python:3.13` image and check the pip version.

```bash
docker run -it --rm --entrypoint=bash python:3.13
pip -V
```

**Answer:**  
✅ **25.3**

---

## Question 2. Understanding Docker networking and docker-compose

Given the provided `docker-compose.yaml`, what hostname and port should pgAdmin use to connect to Postgres?

**Answer:**  
✅ **db:5432**

---

## Prepare the Data

Download the datasets:

```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

Project setup using `uv`:

```bash
uv init --python=3.13
uv add pandas pyarrow sqlalchemy psycopg2-binary tqdm click
uv run python homework/data_ingestion.py
```

---

## Question 3. Counting short trips

For trips in November 2025, how many trips had a `trip_distance <= 1` mile?

```sql
SELECT COUNT(*)
FROM green_taxi_trips
WHERE lpep_pickup_datetime BETWEEN '2025-11-01' AND '2025-12-01'
  AND trip_distance <= 1;
```

**Answer:**  
✅ **8,007**

---

## Question 4. Longest trip for each day

Which pickup day had the longest trip distance (excluding trips ≥ 100 miles)?

```sql
SELECT DATE_TRUNC('DAY', lpep_pickup_datetime)
FROM green_taxi_trips
WHERE trip_distance < 100
ORDER BY trip_distance DESC
LIMIT 1;
```

**Answer:**  
✅ **2025-11-14**

---

## Question 5. Biggest pickup zone

Which pickup zone had the largest total amount on **November 18th, 2025**?

```sql
SELECT z."Zone", SUM(g.fare_amount) AS total_amount
FROM green_taxi_trips g
LEFT JOIN Zones z
  ON g."PULocationID" = z."LocationID"
WHERE lpep_pickup_datetime >= '2025-11-18'
  AND lpep_pickup_datetime <  '2025-11-19'
GROUP BY z."Zone"
ORDER BY total_amount DESC
LIMIT 1;
```

**Answer:**  
✅ **East Harlem North**

---

## Question 6. Largest tip

For passengers picked up in **East Harlem North** in November 2025, which drop-off zone had the largest tip?

```sql
SELECT
  pz."Zone" AS pickup_zone,
  dz."Zone" AS dropoff_zone,
  MAX(g.tip_amount) AS largest_tip
FROM green_taxi_trips g
JOIN Zones pz ON g."PULocationID" = pz."LocationID"
JOIN Zones dz ON g."DOLocationID" = dz."LocationID"
WHERE pz."Zone" = 'East Harlem North'
  AND lpep_pickup_datetime >= '2025-11-01'
  AND lpep_pickup_datetime <  '2025-12-01'
GROUP BY pickup_zone, dropoff_zone
ORDER BY largest_tip DESC
LIMIT 1;
```

**Answer:**  
✅ **Yorkville West**

---

## Question 7. Terraform Workflow

Correct Terraform workflow:

**Answer:**  
✅ **terraform init → terraform apply -auto-approve → terraform destroy**

---

## Submission

- GitHub repository contains all code and SQL used for this homework.
- SQL queries and shell commands are included directly in this README as required.
