# 🔍 Fraud Detection Data Pipeline
### End-to-End Data Engineering Capstone Project

---

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Dataset](#dataset)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Pipeline Steps](#pipeline-steps)
- [dbt Models](#dbt-models)
- [Dashboard](#dashboard)
- [How to Reproduce](#how-to-reproduce)
- [Key Findings](#key-findings)

---

## 🎯 Overview

This project implements a **production-grade batch data pipeline** for fraud detection analytics using the PaySim synthetic financial dataset. The pipeline ingests raw transaction data, processes it with Apache Spark, stores it in Google Cloud Storage as a data lake, loads it into BigQuery as a data warehouse, and transforms it using dbt into analytics-ready tables — all orchestrated by Apache Airflow.

The goal is to enable fraud analysts and business stakeholders to answer questions like:
- Which transaction types are most vulnerable to fraud?
- Who are the highest-risk customers?
- How much money is lost to fraud across transaction types?
- What patterns distinguish fraudulent from legitimate transactions?

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA PIPELINE                                │
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌─────────────┐  │
│  │  PaySim  │───▶│  Spark   │───▶│   GCS    │───▶│  BigQuery   │  │
│  │   CSV    │    │ (Docker) │    │ (Parquet)│    │  Raw Table  │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────┬──────┘  │
│                                                          │         │
│                                                     ┌────▼─────┐  │
│                                                     │   dbt    │  │
│                                                     │Transform │  │
│                                                     └────┬─────┘  │
│                                                          │         │
│                  ┌───────────────────────────────────────▼──────┐  │
│                  │            BigQuery Analytics Tables          │  │
│                  │  stg_transactions │ fct_transactions          │  │
│                  │  fct_fraud_by_type│ dim_customers             │  │
│                  └───────────────────────────────────────────────┘  │
│                                       │                            │
│                              ┌────────▼────────┐                  │
│                              │  Looker Studio  │                  │
│                              │   Dashboard     │                  │
│                              └─────────────────┘                  │
│                                                                     │
│  🔄 Orchestrated by Apache Airflow                                 │
│  🏗️  Infrastructure provisioned by Terraform                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Dataset

**PaySim — Synthetic Financial Fraud Dataset**

| Property | Value |
|----------|-------|
| Source | [Kaggle - PaySim](https://www.kaggle.com/datasets/ealaxi/paysim1) |
| Size | ~471 MB |
| Rows | 6,362,620 transactions |
| Fraud Cases | 8,213 (0.13%) |
| Transaction Types | CASH_IN, CASH_OUT, TRANSFER, PAYMENT, DEBIT |

PaySim simulates mobile money transactions based on real transaction logs from a financial company in Africa. Fraud only occurs in `TRANSFER` and `CASH_OUT` transaction types by design.

**Schema:**

| Column | Type | Description |
|--------|------|-------------|
| step | INT | Time unit (1 step = 1 hour) |
| type | STRING | Transaction type |
| amount | FLOAT | Transaction amount |
| customer_id | STRING | Origin account ID |
| recipient_id | STRING | Destination account ID |
| old_balance_origin | FLOAT | Balance before transaction (origin) |
| new_balance_origin | FLOAT | Balance after transaction (origin) |
| old_balance_dest | FLOAT | Balance before transaction (destination) |
| new_balance_dest | FLOAT | Balance after transaction (destination) |
| isFraud | INT | Ground truth fraud label (1=fraud) |
| isFlaggedFraud | INT | System flagged as fraud |

---

## 🛠️ Tech Stack

| Tool | Purpose | Version |
|------|---------|---------|
| **Terraform** | Infrastructure as Code — provisions GCS bucket and BigQuery dataset | 7.17.0 |
| **Apache Spark** | Distributed data processing — reads CSV, cleans, feature engineers, writes Parquet | 3.5.1 |
| **Docker** | Containerization for Spark and Airflow | Latest |
| **Google Cloud Storage** | Data lake — stores processed Parquet files | - |
| **Google BigQuery** | Data warehouse — stores raw and transformed tables | - |
| **dbt** | Data transformation — staging, intermediate, and marts layers | 1.8.7 |
| **Apache Airflow** | Pipeline orchestration — schedules and monitors the pipeline | 2.8.1 |
| **Looker Studio** | Business intelligence dashboard | - |
| **WSL2 / Ubuntu** | Local development environment | Ubuntu 24 |

---

## 📁 Project Structure

```
capstone-project/
├── terraform/                  # Infrastructure as Code
│   ├── main.tf                 # GCS bucket + BigQuery dataset
│   └── variables.tf            # Project variables
│
├── spark/                      # Data ingestion & processing
│   ├── docker-compose.yml      # Spark container config
│   ├── jobs/
│   │   └── ingest2gcs.py       # Main Spark job (CSV → GCS)
│   └── gcp/
│       └── gcs-connector-hadoop3-latest.jar
│
├── fraud_analytics/            # dbt project
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_transactions.sql
│   │   │   ├── stg_transactions.yml
│   │   │   └── sources.yml
│   │   ├── intermediate/
│   │   │   └── int_transactions_enriched.sql
│   │   └── marts/
│   │       ├── fct_transactions.sql
│   │       ├── fct_fraud_by_type.sql
│   │       ├── fct_risk_summary.sql
│   │       └── dim_customers.sql
│   └── dbt_project.yml
│
├── airflow/                    # Pipeline orchestration
│   ├── docker-compose.yml      # Airflow services
│   ├── dags/
│   │   └── fraud_pipeline.py   # Main DAG
│   └── .env
│
├── data/
│   └── transactions.csv        # Raw PaySim dataset
│
└── keys/
    └── gcp_key.json            # GCP service account (not committed)
```

---

## 🔄 Pipeline Steps

### Step 1 — Infrastructure (Terraform)
Provisions all GCP resources:
```bash
cd terraform
terraform init
terraform apply
```
Creates:
- GCS bucket: `de-capstone-bucket-findata`
- BigQuery dataset: `capsone_findata_dataset`

### Step 2 — Data Ingestion (Spark)
Reads raw CSV, renames columns, engineers features, writes 16 Parquet files to GCS:
```bash
cd spark
docker-compose up -d
docker exec -it spark /opt/spark/bin/spark-submit \
  --jars /opt/spark/gcp/gcs-connector-hadoop3-latest.jar \
  --driver-memory 2g \
  --executor-memory 2g \
  --conf spark.hadoop.fs.gs.io.buffersize=8388608 \
  --conf spark.hadoop.fs.gs.outputstream.upload.chunk.size=8388608 \
  /opt/spark/jobs/ingest2gcs.py
```

**Feature engineering added by Spark:**
- `is_large_transaction` — transactions over $200,000
- `balance_mismatch` — origin balance doesn't reconcile after transaction

### Step 3 — Load to BigQuery
```bash
bq load \
  --source_format=PARQUET \
  --location=EU \
  capsone-project-492612:capsone_findata_dataset.transactions_raw \
  "gs://de-capstone-bucket-findata/raw/transactions/*.parquet"
```

### Step 4 — dbt Transformations
```bash
cd fraud_analytics
source ../dbt-env/bin/activate
dbt run
dbt test
```

### Step 5 — Airflow Orchestration
```bash
cd airflow
docker-compose up -d
```
Access UI at `http://localhost:8081` (credentials: `airflow/airflow`)

Trigger the `fraud_detection_pipeline` DAG which runs:
1. `load_gcs_to_bigquery` — loads Parquet from GCS to BigQuery
2. `dbt_run` — runs all transformation models
3. `dbt_test` — validates data quality
4. `notify_done` — logs pipeline completion

---

## 🔷 dbt Models

```
transactions_raw (BigQuery source)
        │
        ▼
stg_transactions          [VIEW]   — cleaned types, renamed columns
        │
        ▼
int_transactions_enriched [VIEW]   — risk scoring, balance analysis
        │
        ├──▶ fct_transactions      [TABLE]  — 6.4M rows, full fact table
        ├──▶ fct_fraud_by_type     [TABLE]  — fraud stats by payment type
        ├──▶ fct_risk_summary      [TABLE]  — risk level distribution
        └──▶ dim_customers         [TABLE]  — customer risk profiles
```

**Risk Scoring Logic:**

| Risk Level | Condition |
|------------|-----------|
| `CONFIRMED_FRAUD` | `is_fraud = TRUE` |
| `HIGH_RISK` | Balance mismatch + large transaction |
| `MEDIUM_RISK` | Balance mismatch only |
| `LOW_RISK` | No suspicious indicators |

**Data Quality Tests (all passing ✅):**
- `customer_id` — not null
- `amount` — not null
- `transaction_type` — not null + accepted values only
- `transaction_type` — accepted values: CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER

---

## 📈 Dashboard

Built in **Looker Studio** connected directly to BigQuery.

**Page 1 — Executive Overview:**
- Total transactions, fraud cases, fraud amount KPIs
- Fraud cases by transaction type
- Transaction risk distribution
- Fraud rate % by type
- Top fraud transactions table

**Page 2 — Customer & Transaction Analysis:**
- Fraud amount over time (by simulation step)
- Transaction size distribution
- Customer risk label breakdown
- Top fraudulent customers

---

## 🚀 How to Reproduce

### Prerequisites
- GCP account with billing enabled
- Docker + Docker Compose installed
- Terraform installed
- Python 3.10+
- WSL2 (if on Windows)

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/fraud-detection-pipeline
cd fraud-detection-pipeline
```

2. **Add your GCP service account key:**
```bash
cp /path/to/your/key.json keys/gcp_key.json
```

3. **Provision infrastructure:**
```bash
cd terraform && terraform apply
```

4. **Download the dataset** from [Kaggle](https://www.kaggle.com/datasets/ealaxi/paysim1) and place it at `data/transactions.csv`

5. **Run Spark ingestion:**
```bash
cd spark && docker-compose up -d
docker exec -it spark /opt/spark/bin/spark-submit \
  --jars /opt/spark/gcp/gcs-connector-hadoop3-latest.jar \
  --driver-memory 2g --executor-memory 2g \
  /opt/spark/jobs/ingest2gcs.py
```

6. **Set up dbt:**
```bash
python3 -m venv dbt-env && source dbt-env/bin/activate
pip install dbt-bigquery
cd fraud_analytics && dbt run && dbt test
```

7. **Start Airflow:**
```bash
cd airflow && docker-compose up -d
# Access: http://localhost:8081
```

---

## 🔑 Key Findings

| Metric | Value |
|--------|-------|
| Total Transactions | 6,362,620 |
| Confirmed Fraud Cases | 8,213 |
| True Fraud Rate | 0.13% |
| Total Fraud Amount | $12.1 Billion |
| Fraud Transaction Types | TRANSFER, CASH_OUT only |
| High Risk Transactions | 1,653,851 (26%) |
| Fraudulent Customers | ~8,213 unique accounts |

**Key Insight:** Despite fraud occurring in only 0.13% of transactions, the financial impact is enormous — $12.1B lost — because fraudulent transactions tend to be very large amounts (averaging ~$1.47M per fraud case).

---

## ⚠️ Important Notes

- `keys/gcp_key.json` is excluded from version control via `.gitignore`
- The PaySim dataset must be downloaded separately from Kaggle
- GCS lifecycle rule is set to 90 days to prevent accidental data deletion
- In production, the Spark job would be triggered via Airflow's `DataprocSubmitJobOperator` on a shared network or cloud Dataproc cluster

---

## 👤 Author

**Ahmed** — Data Engineering Bootcamp Capstone Project

---

*Built as part of the DataTalks.Club Data Engineering Zoomcamp*
