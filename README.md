Here’s your **final corrected README.md text** 👇

---

# 🌊 Water Quality Index (WQI) Prediction System

## 📌 Overview

This project predicts **Water Quality Index (WQI)** based on important water quality parameters.
It uses **Machine Learning (Python)** for prediction and a **Flask web interface** for user interaction and visualization.
👉 **Note:** The model takes *Min* and *Max* ranges for each parameter.

---

## ⚙️ Inputs (From Web Form)

Each parameter is entered as **minimum and maximum** values:

| Parameter               | Min Input              | Max Input              |
| ----------------------- | ---------------------- | ---------------------- |
| Temperature (°C)        | `Min_Temperature`      | `Max_Temperature`      |
| Dissolved Oxygen (mg/L) | `Min_Dissolved_Oxygen` | `Max_Dissolved_Oxygen` |
| pH Level                | `Min_pH`               | `Max_pH`               |
| Conductivity (µS/cm)    | `Min_Conductivity`     | `Max_Conductivity`     |
| BOD (mg/L)              | `Min_BOD`              | `Max_BOD`              |
| Nitrate (mg/L)          | `Min_Nitrate`          | `Max_Nitrate`          |

---

## 🧩 Project Structure

```
WQI/
├── backend/
│   ├── app.py                      # Flask app – handles form inputs and prediction
│   ├── train_model.py              # Model training logic
│   ├── water_quality_model.pkl     # Trained model
│   ├── requirements.txt            # Dependencies
│   ├── model_visualization_dashboard.html  # Visualization dashboard
│   ├── static/
│   │   ├── script.js               # Frontend logic
│   │   └── style.css               # Styling
│   └── templates/
│       └── index.html              # Main web interface (form with min/max inputs)
│
├── dataset/
│   ├── water_quality.csv           # Main dataset
│   ├── 2017_lake_data.csv ... 2022_lake_data.csv  # Historical data
│
└── download_dataset.py             # Dataset fetching script
```

---

## 🧠 Model Information

* **Algorithm:** Random Forest Classifier
* **Features Used:** Min/Max Temperature, Dissolved Oxygen, pH, Conductivity, BOD, Nitrate
* **Target:** Water Quality Index (WQI)
* **Output:** Numerical WQI and category label (e.g., *Good*, *Moderate*, *Poor*)

---

## 🚀 How to Run

### 1️⃣ Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2️⃣ (Optional) Train the Model

```bash
python train_model.py
```

### 3️⃣ Run the Web App

```bash
python app.py
```

Then open your browser at 👉 **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

---

## 📊 Output

After entering the input values, the model predicts:

* The **Water Quality Index (WQI)** value
* A **category label** indicating whether the water is *Good*, *Moderate*, or *Poor* quality.

---

## 🧾 Notes & Customization

* If you want to add more parameters (like Hardness, Solids, etc.), edit:

  * `index.html` → add input fields
  * `app.py` → read new form fields using `request.form[...]`
  * `train_model.py` → include those columns for training
* Use `model_visualization_dashboard.html` to visualize accuracy, feature importance, and yearly trends.

---

## 🧰 Tech Stack

* **Backend:** Flask (Python)
* **Frontend:** HTML, CSS, JavaScript
* **ML Libraries:** scikit-learn, pandas, numpy, matplotlib

---

---
