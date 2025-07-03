import os
from io import StringIO
import pandas as pd
import pickle
from flask import Flask, request, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from db import (
    add_user, get_users, authenticate_user, get_diseases, update_diseases,
    initialize_db, update_users as db_update_users, update_user_password
)

# Constants
NO_DATA_PROVIDED_MESSAGE = "No data provided"

app = Flask(__name__)

# Initialize the database
initialize_db()

# Swagger UI setup
SWAGGER_URL = '/swagger'
API_URL = '/static/openapi.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Disease Track API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/users', methods=['GET'])
def users():
    try:
        users = get_users()
        if not users:
            return jsonify({"message": "No users found"}), 404
        return jsonify({"users": users}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not name or not email or not password:
        return jsonify({"message": "All fields are required"}), 400
    try:
        add_user(name, email, password)
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    

@app.route('/update_users', methods=['PUT'])
def update_users_route():
    data = request.get_json()
    df = data.get('users')
    
    print("Received data for update:", df)  # Debugging line to check received data
    
    if df is None or not df:
        return jsonify({"message": NO_DATA_PROVIDED_MESSAGE}), 400
    if pd.read_json(StringIO(df)).isnull().values.any():
        return jsonify({"message": "Data contains null values"}), 400
    try:
        db_update_users(df)
        return jsonify({"message": "Users updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    
@app.route('/update_password', methods=['PUT'])
def update_password():
    data = request.get_json()
    email = data.get('email')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not email or not old_password or not new_password or not confirm_password:
        return jsonify({"message": "Tous les champs sont requis."}), 400

    if new_password != confirm_password:
        return jsonify({"message": "Les nouveaux mots de passe ne correspondent pas."}), 400

    success = update_user_password(email, old_password, new_password)
    if success:
        return jsonify({"message": "Mot de passe mis à jour avec succès."}), 200
    else:
        return jsonify({"message": "Ancien mot de passe incorrect."}), 401

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = authenticate_user(email, password)
    if user:
        return jsonify({"user": user}), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401

@app.route('/diseases', methods=['GET'])
def diseases():
    try:
        diseases = get_diseases()
        if not diseases:
            return jsonify({"message": "No diseases found"}), 404
        return jsonify({"diseases": diseases}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/update_diseases_route', methods=['PUT'])
def update_diseases_route():
    data = request.get_json()
    df = data.get('diseases')
    
    if df is None or not df:
        return jsonify({"message": NO_DATA_PROVIDED_MESSAGE}), 400
    if pd.read_json(StringIO(df)).isnull().values.any():
        return jsonify({"message": "Data contains null values"}), 400
    
    try:
        update_diseases(df)
        return jsonify({"message": "Diseases updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    
    if not data:
        return jsonify({"message": NO_DATA_PROVIDED_MESSAGE}), 400
    
    try:
        model = pickle.load(open(model_path, 'rb'))
        input_df = pd.DataFrame([{
            "Confirmed_lag1": data["cases"],
            "Deaths_lag1": data["deaths"],
            "Recovered_lag1": data["recovered"],
            "Country_encoded": data["country"]
        }])
        prediction = model.predict(input_df)
        return jsonify({"prediction": prediction.tolist()}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    
@app.route('/predict_v2', methods=['POST'])
def predict_v2():
    data = request.get_json()
    model_path = os.path.join(os.path.dirname(__file__), 'model_v2.pkl')
    
    if not data:
        return jsonify({"message": NO_DATA_PROVIDED_MESSAGE}), 400
    
    try:
        # Load model
        model = pickle.load(open(model_path, 'rb'))
        
        # Create input DataFrame with lag features
        input_df = pd.DataFrame([{
            "Confirmed_lag1": data["cases_lag1"],
            "Deaths_lag1": data["deaths_lag1"],
            "Recovered_lag1": data["recovered_lag1"],
            "Confirmed_lag2": data["cases_lag2"],
            "Deaths_lag2": data["deaths_lag2"],
            "Recovered_lag2": data["recovered_lag2"],
            "Confirmed_lag3": data["cases_lag3"],
            "Deaths_lag3": data["deaths_lag3"],
            "Recovered_lag3": data["recovered_lag3"],
            "Country_encoded": data["country"],
            "Population": data["population"]
        }])
        
        # Calculate per 100K metrics
        input_df['Confirmed_per_100K'] = input_df["Confirmed_lag1"] / (input_df["Population"] / 100000)
        input_df['Deaths_per_100K'] = input_df["Deaths_lag1"] / (input_df["Population"] / 100000)
        input_df['Recovered_per_100K'] = input_df["Recovered_lag1"] / (input_df["Population"] / 100000)
        
        # Calculate rolling averages (matching notebook approach)
        input_df['Confirmed_rolling_avg3'] = (input_df["Confirmed_lag1"] + 
                                            input_df["Confirmed_lag2"] + 
                                            input_df["Confirmed_lag3"]) / 3
        input_df['Deaths_rolling_avg3'] = (input_df["Deaths_lag1"] + 
                                            input_df["Deaths_lag2"] + 
                                            input_df["Deaths_lag3"]) / 3
        input_df['Recovered_rolling_avg3'] = (input_df["Recovered_lag1"] + 
                                            input_df["Recovered_lag2"] + 
                                            input_df["Recovered_lag3"]) / 3
        
        # Calculate trends (matching notebook approach)
        input_df['Confirmed_trend'] = (input_df["Confirmed_lag1"] - input_df["Confirmed_lag2"] + 
                                    input_df["Confirmed_lag2"] - input_df["Confirmed_lag3"]) / 2
        input_df['Deaths_trend'] = (input_df["Deaths_lag1"] - input_df["Deaths_lag2"] + 
                                    input_df["Deaths_lag2"] - input_df["Deaths_lag3"]) / 2
        input_df['Recovered_trend'] = (input_df["Recovered_lag1"] - input_df["Recovered_lag2"] + 
                                    input_df["Recovered_lag2"] - input_df["Recovered_lag3"]) / 2
        
        # Select only the features the model expects
        features = [
            'Confirmed_lag1', 'Deaths_lag1', 'Recovered_lag1', 'Country_encoded',
            'Confirmed_per_100K', 'Deaths_per_100K', 'Recovered_per_100K',
            'Confirmed_rolling_avg3', 'Deaths_rolling_avg3', 'Recovered_rolling_avg3',
            'Confirmed_trend', 'Deaths_trend', 'Recovered_trend'
        ]
        X = input_df[features]
        
        # Make prediction
        prediction = model.predict(X)
        
        # Return simple prediction results
        return jsonify({"prediction": prediction.tolist()}), 200
        
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
