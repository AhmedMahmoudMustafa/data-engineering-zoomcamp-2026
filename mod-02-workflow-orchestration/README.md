# 📊 Data Engineering Zoomcamp – Kestra Orchestration (Module 2)

This repository contains my work for **Module 2 – Orchestration** of the Data Engineering Zoomcamp.  
The focus of this module is using **Kestra** to orchestrate data workflows and understand execution order, inputs, variables, triggers, and scheduling.

---

## 🧱 Tech Stack (This Module)

- **Kestra** – Workflow orchestration
- **Docker & Docker Compose** – Local environment
- **PostgreSQL** – Kestra metadata backend
- **GCP (Cloud Storage & BigQuery)** – Dataset inspection and validation

---


## 🔄 Kestra Flows

### 01_hello_world
A basic Kestra flow to understand:
- Inputs
- Variables
- Task execution order
- Outputs
- Scheduling (disabled)

---

### 02_python
Demonstrates running a task inside a Docker container using Kestra.
The flow produces outputs that can be reused by downstream tasks.

---

### 03_getting_started_data_pipeline
A simple end-to-end flow that shows:
- Downloading external data
- Transforming files between tasks
- Executing queries as part of a workflow

---

## 📝 Homework Questions & Answers

### Question 1  
**Uncompressed file size of Yellow Taxi data for December 2020**

✅ **Answer:** 134.5 MiB

---

### Question 2  
**Rendered value of `file` when `taxi=green`, `year=2020`, `month=04`**

✅ **Answer:**

---

### Question 3  
**Total rows for Yellow Taxi data in 2020**

✅ **Answer:** 24,648,499

---

### Question 4  
**Total rows for Green Taxi data in 2020**

✅ **Answer:** 1,734,051

---

### Question 5  
**Rows in Yellow Taxi data for March 2021**

✅ **Answer:** 1,925,152

---

### Question 6  
**Timezone configuration for New York in a Schedule trigger**

✅ **Answer:**  
Use: America/New_York


**Notes on Validation & Queries**
**Row counts and file sizes were obtained from:**
**GCP Cloud Storage bucket details**
**BigQuery dataset metadata**
**No SQL queries were required for validation, as the information was available directly from dataset and file details.**
