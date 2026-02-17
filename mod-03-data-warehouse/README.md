# Data Engineering Zoomcamp 2026 - Module 3 (Data Warehouse)

## 📌 Overview

This project demonstrates the use of Google BigQuery for:

- External tables
- Native (materialized) tables
- Columnar storage behavior
- Partitioning
- Clustering
- Query cost optimization

Dataset used:
Yellow Taxi Trip Records (Jan–Jun 2024) stored in Google Cloud Storage.

---

## 🏗 BigQuery Setup

### 1️⃣ Create External Table (GCS → BigQuery)

```sql
CREATE OR REPLACE EXTERNAL TABLE zoomcamp_mod3.yellow_taxi_external
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://dezoomcamp-ass3-2026/yellow_tripdata_2024-*.parquet']
);
```

Data is stored in:
- Google Cloud Storage (GCS)
- BigQuery only references the files

---

### 2️⃣ Create Native (Materialized) Table

```sql
CREATE OR REPLACE TABLE zoomcamp_mod3.yellow_taxi_native AS
SELECT *
FROM zoomcamp_mod3.yellow_taxi_external;
```

This copies data into BigQuery storage.

---

## 📊 Questions & Results

### ✅ Q1 - Counting Records

```sql
SELECT COUNT(*)
FROM zoomcamp_mod3.yellow_taxi_external;
```

---

### ✅ Q2 - Data Read Estimation

```sql
SELECT COUNT(DISTINCT PULocationID)
FROM zoomcamp_mod3.yellow_taxi_external;
```

→ Processes **0 MB** (metadata-only optimization)

```sql
SELECT COUNT(DISTINCT PULocationID)
FROM zoomcamp_mod3.yellow_taxi_native;
```

→ Processes **155.12 MB**

---

### ✅ Q3 - Columnar Storage Behavior

```sql
SELECT DISTINCT PULocationID
FROM zoomcamp_mod3.yellow_taxi_native;
```

→ 155.12 MB

```sql
SELECT DISTINCT PULocationID, DOLocationID
FROM zoomcamp_mod3.yellow_taxi_native;
```

→ 310.24 MB

BigQuery scans only the columns referenced in the query.

---

### ✅ Q4 - Zero Fare Trips

```sql
SELECT COUNT(fare_amount)
FROM zoomcamp_mod3.yellow_taxi_external
WHERE fare_amount = 0;
```

Result:
8,333 trips

---

### ✅ Q5 - Partitioning & Clustering Strategy

Best Strategy:
Partition by `tpep_dropoff_datetime`  
Cluster by `VendorID`

```sql
CREATE OR REPLACE TABLE zoomcamp_mod3.yellow_taxi_partitioned
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID AS
SELECT *
FROM zoomcamp_mod3.yellow_taxi_external;
```

---

### ✅ Q6 - Partition Benefits

```sql
SELECT DISTINCT VendorID
FROM zoomcamp_mod3.yellow_taxi_native
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01'
AND '2024-03-15';
```

→ 310.24 MB processed

```sql
SELECT DISTINCT VendorID
FROM zoomcamp_mod3.yellow_taxi_partitioned
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01'
AND '2024-03-15';
```

→ 26.84 MB processed

Partition pruning significantly reduces query cost.

---

### ✅ Q7 - External Table Storage

Data is stored in:
Google Cloud Storage (GCS)

---

### ✅ Q8 - Clustering Best Practice

Statement:
"It is best practice to always cluster your data"

Answer:
False

Clustering should only be used when query patterns justify it. It adds storage overhead and may slow writes.

---

### ✅ Q9 - Table Scan Understanding

```sql
SELECT COUNT(*)
FROM zoomcamp_mod3.yellow_taxi_native;
```

Estimated bytes: ~0 B

Reason:
BigQuery uses metadata optimization for COUNT(*) without filters.

---

## 🚀 Key Learnings

- BigQuery is columnar
- Partitioning reduces scan cost
- Clustering improves filtering and sorting performance
- External tables store data in GCS
- Query cost depends on bytes processed

---

## 🛠 Technologies Used

- Google Cloud Storage
- BigQuery
- SQL
- Parquet

---

## 👨‍💻 Author

Ahmed Mustafa  
Data Engineering Zoomcamp 2026
