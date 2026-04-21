from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when

spark = SparkSession.builder \
    .appName("Capstone-Finance") \
    .getOrCreate()

# 1. Read data
df = spark.read.csv("/opt/spark/data/transactions.csv", header=True, inferSchema=True)

# 2. Rename columns
df = df.withColumnRenamed("nameOrig", "customer_id") \
       .withColumnRenamed("nameDest", "recipient_id") \
       .withColumnRenamed("oldbalanceOrg", "old_balance_origin") \
       .withColumnRenamed("newbalanceOrig", "new_balance_origin") \
       .withColumnRenamed("oldbalanceDest", "old_balance_dest") \
       .withColumnRenamed("newbalanceDest", "new_balance_dest")

# 3. EDA (optional logs)
df.printSchema()
df.show(5, truncate=False)

print("Total rows:", df.count())

df.groupBy("type").count().show()
df.groupBy("isFraud").count().show()

df.describe(["amount"]).show()

# Null check
df.select([
    count(when(col(c).isNull(), c)).alias(c)
    for c in df.columns
]).show()

df.groupBy("type", "isFraud").count().show()

# 4. Cleaning
df_clean = df.fillna({
    "old_balance_origin": 0,
    "new_balance_origin": 0,
    "old_balance_dest": 0,
    "new_balance_dest": 0
})

# 5. Feature engineering
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

# 6. FIX: repartition BEFORE write
df_enriched = df_enriched.repartition(4)

# 7. Write parquet
df_enriched.write \
    .mode("overwrite") \
    .parquet("/opt/spark/output/transactions_parquet")

print("DONE")