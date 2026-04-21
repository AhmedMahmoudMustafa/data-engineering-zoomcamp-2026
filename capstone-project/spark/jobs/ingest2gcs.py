from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when

spark = SparkSession.builder \
    .appName("Capstone-Finance") \
    .config("spark.jars", "/opt/spark/gcp/gcs-connector-hadoop3-latest.jar") \
    .getOrCreate()

#  GCS Authentication
spark._jsc.hadoopConfiguration().set(
    "fs.gs.impl", 
    "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem"
)
spark._jsc.hadoopConfiguration().set(
    "google.cloud.auth.service.account.json.keyfile", 
    "/opt/spark/gcp/keys/gcp_key.json"
)

# 1. Read data
df = spark.read.csv("/opt/spark/data/transactions.csv", header=True, inferSchema=True)

# 2. Rename columns
df = df.withColumnRenamed("nameOrig", "customer_id") \
       .withColumnRenamed("nameDest", "recipient_id") \
       .withColumnRenamed("oldbalanceOrg", "old_balance_origin") \
       .withColumnRenamed("newbalanceOrig", "new_balance_origin") \
       .withColumnRenamed("oldbalanceDest", "old_balance_dest") \
       .withColumnRenamed("newbalanceDest", "new_balance_dest")

# 3. Cleaning
df_clean = df.fillna({
    "old_balance_origin": 0,
    "new_balance_origin": 0,
    "old_balance_dest": 0,
    "new_balance_dest": 0
})

# 4. Feature engineering
df_enriched = df_clean.withColumn(
    "is_large_transaction",
    when(col("amount") > 200000, 1).otherwise(0)
).withColumn(
    "balance_mismatch",
    when(
        col("old_balance_origin") - col("amount") != col("new_balance_origin"),
        1
    ).otherwise(0)
)

# 5. Repartition
df_enriched = df_enriched.repartition(16)

# 6. Write directly to GCS (commented out local write below)
df_enriched.write \
    .mode("overwrite") \
    .parquet("gs://de-capstone-bucket-findata/raw/transactions/")

print("✅ DONE - Data written to GCS")