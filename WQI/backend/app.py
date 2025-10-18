from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import joblib
import os


app = Flask(__name__)
CORS(app)  # Enable CORS for compatibility


# Load the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "water_quality_model.pkl")
model = joblib.load(MODEL_PATH)


# Serve the HTML frontend
@app.route("/")
def home():
    return render_template("index.html")


# API endpoint for prediction
@app.route("/predict", methods=["POST"])
def predict_wqi():
    try:
        data = request.json
        print("Received data:", data)


        # Helper function for safe conversion
        def to_float(value, default=0.0):
            try:
                return float(str(value).replace(',', '').strip())
            except:
                return default


        # Calculate averages safely
        Temperature = (to_float(data.get("Min_Temperature")) + to_float(data.get("Max_Temperature"))) / 2
        Dissolved_Oxygen = (to_float(data.get("Min_Dissolved_Oxygen")) + to_float(data.get("Max_Dissolved_Oxygen"))) / 2
        pH = (to_float(data.get("Min_pH")) + to_float(data.get("Max_pH"))) / 2
        Conductivity = (to_float(data.get("Min_Conductivity")) + to_float(data.get("Max_Conductivity"))) / 2
        BOD = (to_float(data.get("Min_BOD")) + to_float(data.get("Max_BOD"))) / 2
        Nitrate = (to_float(data.get("Min_Nitrate")) + to_float(data.get("Max_Nitrate"))) / 2


        # Prepare DataFrame
        df = pd.DataFrame([{
            "Temperature": Temperature,
            "Dissolved_Oxygen": Dissolved_Oxygen,
            "pH": pH,
            "Conductivity": Conductivity,
            "BOD": BOD,
            "Nitrate": Nitrate
        }])


        prediction = model.predict(df)[0]


        return jsonify({"WQI": round(prediction, 2)})


    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
