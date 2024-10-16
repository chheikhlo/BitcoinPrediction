# -*- coding: utf-8 -*-

from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

# Créer une session Spark
spark = SparkSession.builder.appName("BitcoinPricePredictionModel").getOrCreate()

# Charger les données depuis HDFS (parquet files)
data_df = spark.read.parquet("hdfs://namenode:9000/bitcoin_data/")

# Échantillonnage aléatoire des données (10% des données)
sampled_df = data_df.sample(withReplacement=False, fraction=0.1, seed=42)

# Sélectionner les colonnes pertinentes pour l'entraînement du modèle (ex: volume et prix)
assembler = VectorAssembler(inputCols=["volume"], outputCol="features")

# Créer le DataFrame avec les caractéristiques et l'étiquette (le prix à prédire)
assembled_df = assembler.transform(sampled_df).select("features", "price")

# Diviser les données en ensemble d'entraînement (80%) et de test (20%)
train_df, test_df = assembled_df.randomSplit([0.8, 0.2], seed=1234)

# Créer un modèle de régression linéaire
lr = LinearRegression(featuresCol="features", labelCol="price")

# Entraîner le modèle sur l'ensemble d'entraînement
lr_model = lr.fit(train_df)

# Faire des prédictions sur l'ensemble de test
predictions = lr_model.transform(test_df)

# Évaluer les performances du modèle à l'aide de l'erreur quadratique moyenne (RMSE)
evaluator = RegressionEvaluator(labelCol="price", predictionCol="prediction", metricName="rmse")
rmse = evaluator.evaluate(predictions)
print("Root Mean Squared Error (RMSE) on test data: {}".format(rmse))

# Sauvegarder le modèle entraîné dans backend
lr_model.save("/shared_volume_model/bitcoin_model")
