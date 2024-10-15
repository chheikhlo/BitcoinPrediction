from flask import Flask, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Charger le modèle ARIMA
with open('/home/jovyan/work/arima_model3.pkl', 'rb') as f:
    model = pickle.load(f)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json['data']
        # Convertir les données en format approprié pour le modèle
        data = np.array(data).reshape(1, -1)
        prediction = model.predict(data)
        return jsonify({'prediction': prediction.tolist()})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(port=5000)  # Lancer l'API Flask sur le port 5000
