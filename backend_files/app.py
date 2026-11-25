import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize the Flask app
superkart_api = Flask("SuperKart Sales Forecaster")
# Keeping JSON keys in row order (As Flask sorts keys alphabetically by default)
superkart_api.json.sort_keys = False

# Load the serialized pipeline (preprocessing + tuned Random Forest)
model = joblib.load("superkart_model.joblib")

# Features the model expects, in training order
FEATURES = [
    "Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area", "Product_MRP",
    "Store_Size", "Store_Location_City_Type", "Store_Type",
    "Product_Id_char", "Store_Age_Years", "Product_Type_Category",
]


@superkart_api.get("/")
def home():
    """Health-check / landing endpoint."""
    return "Welcome to the SuperKart Sales Forecasting API!"


@superkart_api.post("/v1/predict")
def predict_sales():
    """Online inference: one JSON record in, one prediction out."""
    data = request.get_json(silent=True) or {}
    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    input_df = pd.DataFrame([{f: data[f] for f in FEATURES}])
    prediction = model.predict(input_df)[0]
    return jsonify({"Predicted_Sales": round(float(prediction), 2)})


@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """Batch inference: CSV file in, {row_index: prediction} JSON out."""
    if "file" not in request.files:
        return jsonify({"error": "Upload a CSV file under the key 'file'"}), 400

    input_df = pd.read_csv(request.files["file"])
    missing = [f for f in FEATURES if f not in input_df.columns]
    if missing:
        return jsonify({"error": f"Missing columns: {missing}"}), 400

    predictions = model.predict(input_df[FEATURES])
    return jsonify({str(i): round(float(p), 2) for i, p in zip(input_df.index, predictions)})


if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
