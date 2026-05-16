# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from pyspark.sql import functions as F

df = spark.read.format("bigquery").load("bigquery-public-data.breathe.nature")
data = df.where(F.length("body") > 100).sample(0.1).collect()
