from flask import Flask, jsonify
from kafka import KafkaProducer, KafkaConsumer
import joblib
import json

app = Flask(__name__)

# Charger le modèle sauvegardé
model = joblib.load('')

# Configuration de Kafka
KAFKA_BROKER_URL = 'localhost:9092'  # Changez cela selon votre configuration Kafka
TOPIC_NAME = 'predictions_topic'

# Initialisation du producteur Kafka
producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER_URL,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Initialisation du consommateur Kafka
consumer = KafkaConsumer(TOPIC_NAME,
                         bootstrap_servers=KAFKA_BROKER_URL,
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                         auto_offset_reset='earliest',
                         enable_auto_commit=True)

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    # Supposons que tu utilises les dernières données pour la prédiction
    # Ajuste ceci pour obtenir les données réelles de trading
    sample_data = [[timestamp, prix_achat, prix_vente, volume]]

    # Envoyer les données au topic Kafka
    producer.send(TOPIC_NAME, {'data': sample_data})
    producer.flush()  # Assurez-vous que les données sont envoyées

    # Attendre la réponse de Kafka (vous pouvez le faire de manière asynchrone dans un vrai projet)
    for message in consumer:
        predictions = model.predict(message.value['data'])
        return jsonify(predictions.tolist())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5551)
