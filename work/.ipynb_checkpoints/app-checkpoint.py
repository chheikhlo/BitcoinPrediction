from flask import Flask, request, jsonify
import numpy as np
import pickle
import os

app = Flask(__name__)

# Chemin vers le modèle de prédiction
model_path = './best_digit_recognition_model.pkl'

# Charger le modèle de prédiction des chiffres
def load_model():
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

# Route pour prédire le chiffre
@app.route('/api/predict_digit', methods=['POST'])
def predict_digit():
    # Récupérer les données de pixels à partir du corps de la requête JSON
    data = request.get_json()
    pixels = data['pixels']

    # Charger le modèle
    model = load_model()

    # Convertir les pixels en un tableau numpy et redimensionner
    input_data = np.array(pixels).reshape(1, -1)

    # Faire la prédiction
    prediction = model.predict(input_data)

    # Renvoyer la prédiction au format JSON
    return jsonify({'prediction': int(prediction[0])})

if __name__ == '__main__':
    app.run(port=9006)
