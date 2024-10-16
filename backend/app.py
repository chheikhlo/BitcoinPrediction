from flask import Flask, request, jsonify
from kafka import KafkaProducer
from flask_cors import CORS
import json
from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegressionModel
from pyspark.ml.linalg import Vectors

app = Flask(__name__)

# Activer CORS pour toutes les routes, avec les origines spécifiques
CORS(app)

# Configuration de Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Créer une session Spark
spark = SparkSession.builder \
    .appName("BitcoinPricePredictionAPI") \
    .getOrCreate()

# Charger le modèle de régression linéaire enregistré
model_path = "/shared_volume_model/bitcoin_model/"  # Chemin du modèle
lr_model = LinearRegressionModel.load(model_path)

@app.route('/api/send_trade_data', methods=['POST'])
def send_trade_data():
    trade_data = request.json
    producer.send('bitcoin_data', trade_data)
    return jsonify({"status": "success", "message": "Trade data sent to Kafka"}), 200

@app.route('/api/get_predictions', methods=['POST'])
def get_predictions():
    request_data = request.json

    # Affiche les données reçues pour vérifier le volume
    print(f"Données reçues pour prédiction : {request_data}")

    volume = request_data.get('volume')
    if volume is None:
        return jsonify({"error": "No volume data provided"}), 400

    # Affiche le volume utilisé pour la prédiction
    print(f"Volume utilisé pour la prédiction : {volume}")

    # Convertir en vecteur pour Spark ML
    features = Vectors.dense([volume])

    # Créer un DataFrame Spark avec ces caractéristiques
    data = spark.createDataFrame([(features, )], ["features"])

    # Faire des prédictions
    prediction = lr_model.transform(data).collect()[0].prediction

    return jsonify({"prediction": prediction})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5551, debug=True)
