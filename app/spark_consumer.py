from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp
from pyspark.sql.types import StructType, StringType, FloatType

# Créer une session Spark
spark = SparkSession.builder \
    .appName("KafkaBitcoinStream") \
    .getOrCreate()

# Schéma des données Kafka (ce sont les données envoyées par le WebSocket de Binance)
schema = StructType() \
    .add("timestamp", StringType()) \
    .add("price", FloatType()) \
    .add("volume", FloatType())

# Lire les données depuis Kafka
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "bitcoin_data") \
    .load()

# Les données venant de Kafka sont en format binaire, donc il faut les décoder
value_df = kafka_df.selectExpr("CAST(value AS STRING)")

# Appliquer le schéma JSON aux données
parsed_df = value_df.select(from_json(col("value"), schema).alias("data")).select("data.*")

# Nettoyer les données (exemple : convertir le timestamp en format timestamp Spark et gérer les valeurs nulles)
cleaned_df = parsed_df.withColumn("timestamp", to_timestamp(col("timestamp") / 1000)) \
    .na.drop()  # Supprimer les lignes avec des valeurs nulles

# Afficher les données traitées dans la console (pour le debug)
query_console = cleaned_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .trigger(processingTime='10 seconds').start()  # Micro-batches de 10 secondes

# Enregistrer les données nettoyées dans HDFS au format Parquet
query_hdfs = cleaned_df.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "hdfs://namenode:9000/bitcoin_data/") \
    .option("checkpointLocation", "hdfs://namenode:9000/bitcoin_data/checkpoint/") \
    .trigger(processingTime='10 seconds').start()  # Micro-batches de 10 secondes

# Attendre que le traitement se termine
query_console.awaitTermination()
query_hdfs.awaitTermination()
