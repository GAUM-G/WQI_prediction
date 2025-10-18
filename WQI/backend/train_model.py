import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import numpy as np


# Load dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), "../dataset/water_quality.csv")
data = pd.read_csv(DATA_PATH)


# Columns to average
cols = [
    ("Temperature", "Min Temperature", "Max Temperature"),
    ("Dissolved_Oxygen", "Min Dissolved Oxygen", "Max Dissolved Oxygen"),
    ("pH", "Min pH", "Max pH"),
    ("Conductivity", "Min Conductivity", "Max Conductivity"),
    ("BOD", "Min BOD", "Max BOD"),
    ("Nitrate", "Min Nitrate N + Nitrite N", "Max Nitrate N + Nitrite N")
]


# Convert to numeric and average
for new_col, min_col, max_col in cols:
    data[min_col] = pd.to_numeric(data[min_col], errors='coerce')
    data[max_col] = pd.to_numeric(data[max_col], errors='coerce')
    data[new_col] = (data[min_col] + data[max_col]) / 2


# Drop rows with NaN in any of the averaged columns
data = data.dropna(subset=[new_col for new_col,_,_ in cols])


# COMPLETE WQI Calculation with ALL parameters verified
def calculate_wqi(row):
    """
    Calculate WQI based on BIS IS 10500:2012, WHO, and CPCB standards
    
    Safe Limits (from JS and standards):
    - Temperature: ≤25°C (optimal 15-25°C)
    - Dissolved Oxygen: 6.5-8 mg/L (minimum 6 mg/L)
    - pH: 6.5-8.5 (ideal 7.0-7.5)
    - Conductivity: ≤500 µS/cm (max 2250 µS/cm)
    - BOD: ≤2 mg/L (max 6 mg/L)
    - Nitrate: ≤45 mg/L (no relaxation)
    """
    
    weights = {
        "Temperature": 0.1, 
        "Dissolved_Oxygen": 0.25, 
        "pH": 0.15, 
        "Conductivity": 0.1, 
        "BOD": 0.2, 
        "Nitrate": 0.2
    }


    q = {}
    
    # 1. TEMPERATURE (Lower is better, ≤25°C ideal)
    temp_value = row["Temperature"]
    if temp_value <= 15:
        q["Temperature"] = 100  # Very cold but acceptable
    elif temp_value <= 25:
        # Linear decrease from 15°C (100) to 25°C (90)
        q["Temperature"] = 100 - ((temp_value - 15) / 10) * 10
    elif temp_value <= 30:
        # Acceptable but not ideal
        q["Temperature"] = 90 - ((temp_value - 25) / 5) * 40
    else:
        # Poor quality - high temperature
        q["Temperature"] = max(0, 50 - ((temp_value - 30) / 10) * 50)
    
    # 2. DISSOLVED OXYGEN (6.5-10 mg/L ideal, >10 = supersaturation penalty)
    do_value = row["Dissolved_Oxygen"]
    if do_value >= 6.5 and do_value <= 10:
        q["Dissolved_Oxygen"] = 100  # Ideal range
    elif do_value > 10:
        # Supersaturation penalty (unnatural/artificial)
        if do_value <= 14:
            q["Dissolved_Oxygen"] = 100 - ((do_value - 10) / 4) * 30
        else:
            # Extremely high - significant penalty
            q["Dissolved_Oxygen"] = max(0, 70 - ((do_value - 14) / 10) * 70)
    elif do_value >= 5:
        # Below ideal but acceptable (5-6.5 mg/L)
        q["Dissolved_Oxygen"] = 50 + ((do_value - 5) / 1.5) * 50
    else:
        # Critical - very low DO
        q["Dissolved_Oxygen"] = max(0, (do_value / 5) * 50)
    
    # 3. pH (6.5-8.5 acceptable, 7.0-7.5 ideal)
    ph_value = row["pH"]
    if ph_value >= 7.0 and ph_value <= 7.5:
        q["pH"] = 100  # Ideal neutral range
    elif ph_value >= 6.5 and ph_value <= 8.5:
        # Acceptable but not ideal
        if ph_value < 7.0:
            deviation = 7.0 - ph_value
        else:
            deviation = ph_value - 7.5
        q["pH"] = 100 - (deviation / 1.0) * 20
    else:
        # Outside acceptable range
        if ph_value < 6.5:
            deviation = 6.5 - ph_value
        else:
            deviation = ph_value - 8.5
        q["pH"] = max(0, 80 - (deviation / 1.5) * 80)
    
    # 4. CONDUCTIVITY (≤500 ideal, 500-1500 acceptable, >1500 poor)
    cond_value = row["Conductivity"]
    if cond_value <= 500:
        q["Conductivity"] = 100  # Desirable limit
    elif cond_value <= 1500:
        # Acceptable range
        q["Conductivity"] = 100 - ((cond_value - 500) / 1000) * 50
    elif cond_value <= 2250:
        # Poor but within maximum permissible
        q["Conductivity"] = 50 - ((cond_value - 1500) / 750) * 40
    else:
        # Exceeds maximum limit
        q["Conductivity"] = max(0, 10 - ((cond_value - 2250) / 1000) * 10)
    
    # 5. BOD (≤2 ideal, 2-5 acceptable, >5 poor)
    bod_value = row["BOD"]
    if bod_value <= 2:
        q["BOD"] = 100  # Class A drinking water
    elif bod_value <= 5:
        # Acceptable but not ideal
        q["BOD"] = 100 - ((bod_value - 2) / 3) * 30
    elif bod_value <= 10:
        # Poor quality
        q["BOD"] = 70 - ((bod_value - 5) / 5) * 60
    else:
        # Very poor - highly polluted
        q["BOD"] = max(0, 10 - ((bod_value - 10) / 10) * 10)
    
    # 6. NITRATE (Lower is better, ≤45 mg/L BIS standard)
    nitrate_value = row["Nitrate"]
    if nitrate_value <= 10:
        q["Nitrate"] = 100  # Very low contamination
    elif nitrate_value <= 45:
        # Acceptable - linear decrease to BIS limit
        q["Nitrate"] = 100 - ((nitrate_value - 10) / 35) * 50
    elif nitrate_value <= 50:
        # Near/at WHO limit (50 mg/L)
        q["Nitrate"] = 50 - ((nitrate_value - 45) / 5) * 30
    else:
        # Exceeds safe limits
        q["Nitrate"] = max(0, 20 - ((nitrate_value - 50) / 50) * 20)
    
    # Ensure all scores are within 0-100
    for param in q:
        q[param] = max(min(q[param], 100), 0)
    
    # Calculate weighted WQI
    WQI = sum(q[param] * weights[param] for param in weights) / sum(weights.values())
    
    return WQI


# Add WQI column
print("Calculating WQI for all samples...")
data["WQI"] = data.apply(calculate_wqi, axis=1)


# Print WQI statistics
print("\nWQI Statistics:")
print(f"Mean WQI: {data['WQI'].mean():.2f}")
print(f"Min WQI: {data['WQI'].min():.2f}")
print(f"Max WQI: {data['WQI'].max():.2f}")
print(f"Median WQI: {data['WQI'].median():.2f}")


# Features and target
X = data[["Temperature","Dissolved_Oxygen","pH","Conductivity","BOD","Nitrate"]]
y = data["WQI"]


# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# Train model
print("\nTraining Random Forest model...")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)


# Evaluate
y_pred = model.predict(X_test)
print("\n=== Model Performance ===")
print(f"R2 Score: {r2_score(y_test, y_pred):.4f}")
print(f"MAE: {mean_absolute_error(y_test, y_pred):.4f}")


# Save model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "water_quality_model.pkl")
joblib.dump(model, MODEL_PATH)
print(f"\n✅ Model saved at: {MODEL_PATH}")


# ==================== INTERACTIVE WEB VISUALIZATION ====================
print("\n📊 Generating Interactive Web Visualizations...")

# Create subplots with 2 rows and 3 columns
fig = make_subplots(
    rows=2, cols=3,
    subplot_titles=(
        'Actual vs Predicted WQI',
        'Residual Plot',
        'Feature Importance',
        'Distribution: Actual vs Predicted',
        'Error Distribution',
        'Sorted Absolute Errors'
    ),
    specs=[[{"type": "scatter"}, {"type": "scatter"}, {"type": "bar"}],
           [{"type": "histogram"}, {"type": "histogram"}, {"type": "scatter"}]]
)

# Calculate residuals and errors
residuals = y_test.values - y_pred
error = np.abs(residuals)

# 1. Actual vs Predicted Scatter Plot
fig.add_trace(
    go.Scatter(
        x=y_test,
        y=y_pred,
        mode='markers',
        marker=dict(size=8, color='blue', opacity=0.6, line=dict(width=1, color='black')),
        name='Predictions',
        hovertemplate='<b>Actual</b>: %{x:.2f}<br><b>Predicted</b>: %{y:.2f}<extra></extra>'
    ),
    row=1, col=1
)

# Add perfect prediction line
min_val, max_val = y_test.min(), y_test.max()
fig.add_trace(
    go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        line=dict(color='red', dash='dash', width=2),
        name='Perfect Prediction',
        showlegend=False
    ),
    row=1, col=1
)

# 2. Residual Plot
fig.add_trace(
    go.Scatter(
        x=y_pred,
        y=residuals,
        mode='markers',
        marker=dict(size=8, color='green', opacity=0.6, line=dict(width=1, color='black')),
        name='Residuals',
        hovertemplate='<b>Predicted</b>: %{x:.2f}<br><b>Residual</b>: %{y:.2f}<extra></extra>'
    ),
    row=1, col=2
)

# Add zero line
fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=2)

# 3. Feature Importance
feature_importance = model.feature_importances_
features = X.columns.tolist()
sorted_idx = np.argsort(feature_importance)[::-1]

fig.add_trace(
    go.Bar(
        y=[features[i] for i in sorted_idx],
        x=[feature_importance[i] for i in sorted_idx],
        orientation='h',
        marker=dict(color='skyblue', line=dict(width=1, color='black')),
        name='Importance',
        hovertemplate='<b>%{y}</b><br>Importance: %{x:.4f}<extra></extra>'
    ),
    row=1, col=3
)

# 4. Distribution Comparison
fig.add_trace(
    go.Histogram(
        x=y_test,
        name='Actual WQI',
        marker=dict(color='blue', opacity=0.6, line=dict(width=1, color='black')),
        nbinsx=30,
        hovertemplate='<b>WQI Range</b>: %{x}<br><b>Count</b>: %{y}<extra></extra>'
    ),
    row=2, col=1
)

fig.add_trace(
    go.Histogram(
        x=y_pred,
        name='Predicted WQI',
        marker=dict(color='orange', opacity=0.6, line=dict(width=1, color='black')),
        nbinsx=30,
        hovertemplate='<b>WQI Range</b>: %{x}<br><b>Count</b>: %{y}<extra></extra>'
    ),
    row=2, col=1
)

# 5. Error Distribution
fig.add_trace(
    go.Histogram(
        x=residuals,
        name='Error Distribution',
        marker=dict(color='coral', opacity=0.7, line=dict(width=1, color='black')),
        nbinsx=30,
        hovertemplate='<b>Error</b>: %{x:.2f}<br><b>Count</b>: %{y}<extra></extra>'
    ),
    row=2, col=2
)

fig.add_vline(x=0, line_dash="dash", line_color="red", row=2, col=2)

# 6. Sorted Absolute Errors
sorted_error = np.sort(error)
mean_error = np.mean(error)

fig.add_trace(
    go.Scatter(
        x=list(range(len(sorted_error))),
        y=sorted_error,
        mode='lines',
        line=dict(color='purple', width=2),
        name='Absolute Error',
        hovertemplate='<b>Sample</b>: %{x}<br><b>Error</b>: %{y:.2f}<extra></extra>'
    ),
    row=2, col=3
)

fig.add_hline(y=mean_error, line_dash="dash", line_color="red", 
              annotation_text=f"Mean Error: {mean_error:.2f}", row=2, col=3)

# Update layout
fig.update_xaxes(title_text="Actual WQI", row=1, col=1)
fig.update_yaxes(title_text="Predicted WQI", row=1, col=1)

fig.update_xaxes(title_text="Predicted WQI", row=1, col=2)
fig.update_yaxes(title_text="Residuals", row=1, col=2)

fig.update_xaxes(title_text="Importance", row=1, col=3)
fig.update_yaxes(title_text="Features", row=1, col=3)

fig.update_xaxes(title_text="WQI Value", row=2, col=1)
fig.update_yaxes(title_text="Frequency", row=2, col=1)

fig.update_xaxes(title_text="Residuals (Error)", row=2, col=2)
fig.update_yaxes(title_text="Frequency", row=2, col=2)

fig.update_xaxes(title_text="Sample Index (Sorted)", row=2, col=3)
fig.update_yaxes(title_text="Absolute Error", row=2, col=3)

# Update overall layout
fig.update_layout(
    title={
        'text': f'<b>Water Quality Model Performance Dashboard</b><br><sup>R² Score: {r2_score(y_test, y_pred):.4f} | MAE: {mean_absolute_error(y_test, y_pred):.4f}</sup>',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 24}
    },
    height=900,
    width=1800,
    showlegend=True,
    template='plotly_white',
    hovermode='closest'
)

# Save as HTML file
HTML_PATH = os.path.join(os.path.dirname(__file__), "model_visualization_dashboard.html")
fig.write_html(HTML_PATH)
print(f"✅ Interactive dashboard saved at: {HTML_PATH}")

# Automatically open in web browser
print("\n🌐 Opening visualization dashboard in web browser...")
webbrowser.open('file://' + os.path.abspath(HTML_PATH))

print("\n✅ All visualizations generated and opened in browser successfully!")
