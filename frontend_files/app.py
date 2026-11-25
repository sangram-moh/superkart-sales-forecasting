import io
import os

import pandas as pd
import requests
import streamlit as st

# Backend URL: the backend container's name on the shared Docker network
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860")

# Store profiles exactly as they appear in the training data
# (size, city tier, store type, age in years as of 2025)
STORES = {
    "OUT001 - Supermarket Type1 (High, Tier 2)": ("High", "Tier 2", "Supermarket Type1", 38),
    "OUT002 - Food Mart (Small, Tier 3)": ("Small", "Tier 3", "Food Mart", 27),
    "OUT003 - Departmental Store (Medium, Tier 1)": ("Medium", "Tier 1", "Departmental Store", 26),
    "OUT004 - Supermarket Type2 (Medium, Tier 2)": ("Medium", "Tier 2", "Supermarket Type2", 16),
}

# Product type -> Product_Id prefix (FD = food, DR = drinks, NC = non-consumables)
DRINKS = ["Soft Drinks", "Hard Drinks"]
NON_CONSUMABLES = ["Household", "Health and Hygiene", "Others"]
PERISHABLES = ["Dairy", "Meat", "Fruits and Vegetables", "Breakfast", "Breads", "Seafood"]
PRODUCT_TYPES = sorted([
    "Baking Goods", "Breads", "Breakfast", "Canned", "Dairy", "Frozen Foods",
    "Fruits and Vegetables", "Hard Drinks", "Health and Hygiene", "Household",
    "Meat", "Others", "Seafood", "Snack Foods", "Soft Drinks", "Starchy Foods",
])

st.set_page_config(page_title="SuperKart Sales Forecaster", page_icon="🛒")
st.title("🛒 SuperKart Sales Forecaster")
st.write("Predict the total sales revenue of a product in a SuperKart store.")

online_tab, batch_tab = st.tabs(["Single prediction", "Batch prediction"])

# ---------------- Online (single) prediction ----------------
with online_tab:
    st.subheader("Store details")
    store = st.selectbox("Store", list(STORES.keys()))
    store_size, city_type, store_type, store_age = STORES[store]

    st.subheader("Product details")
    product_type = st.selectbox("Product Type", PRODUCT_TYPES)
    if product_type in NON_CONSUMABLES:
        sugar = st.selectbox("Product Sugar Content", ["No Sugar"])
    else:
        sugar = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    weight = st.number_input("Product Weight", min_value=4.0, max_value=22.0, value=12.66, step=0.1)
    area = st.number_input("Product Allocated Area (ratio)", min_value=0.004, max_value=0.298,
                           value=0.068, step=0.001, format="%.3f")
    mrp = st.number_input("Product MRP", min_value=31.0, max_value=266.0, value=147.0, step=1.0)

    if st.button("Predict Sales", type="primary"):
        payload = {
            "Product_Weight": weight,
            "Product_Sugar_Content": sugar,
            "Product_Allocated_Area": area,
            "Product_MRP": mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": city_type,
            "Store_Type": store_type,
            "Product_Id_char": "DR" if product_type in DRINKS else "NC" if product_type in NON_CONSUMABLES else "FD",
            "Store_Age_Years": store_age,
            "Product_Type_Category": "Perishables" if product_type in PERISHABLES else "Non Perishables",
        }
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            response.raise_for_status()
            st.success(f"Predicted Product Store Sales Total: **{response.json()['Predicted_Sales']:,.2f}**")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not get a prediction from the backend: {e}")

# ---------------- Batch prediction ----------------
with batch_tab:
    st.write("Upload a CSV with these columns: `Product_Weight`, `Product_Sugar_Content`, "
             "`Product_Allocated_Area`, `Product_MRP`, `Store_Size`, `Store_Location_City_Type`, "
             "`Store_Type`, `Product_Id_char`, `Store_Age_Years`, `Product_Type_Category`.")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file is not None and st.button("Predict Batch", type="primary"):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predictbatch",
                                     files={"file": uploaded_file.getvalue()}, timeout=120)
            response.raise_for_status()
            results = pd.read_csv(io.BytesIO(uploaded_file.getvalue()))
            results["Predicted_Sales"] = list(response.json().values())
            st.success(f"Predicted sales for {len(results)} products "
                       f"(total: {results['Predicted_Sales'].sum():,.2f})")
            st.dataframe(results)
            st.download_button("Download predictions", results.to_csv(index=False),
                               file_name="superkart_predictions.csv", mime="text/csv")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not get predictions from the backend: {e}")
