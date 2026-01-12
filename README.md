# Global Production Dashboard  
### Real-Time Manufacturing Intelligence Platform (Industry 4.0)

🚀 An interactive production intelligence dashboard designed to monitor, analyze, and forecast manufacturing performance across multiple plants.

This project demonstrates how raw production data can be transformed into **actionable operational intelligence**, combining data analytics, KPI engineering, and interactive visualization.

---

## 🧠 System Architecture

The dashboard follows a modular, industry-inspired architecture:

- **Data Simulation Layer**  
  Realistic manufacturing data with noise, downtime, defects, and shift variability.

- **Data & Analytics Layer**  
  KPI computation (Production, Defects, Availability, OEE) using Pandas.

- **Forecasting Layer**  
  Explainable time-series forecasting using linear regression.

- **Visualization Layer**  
  Interactive dashboards built with Dash and Plotly.

---

## 🎯 Business Problem

Manufacturing organizations often struggle with:
- Fragmented visibility across plants
- Delayed reaction to quality and downtime issues
- KPI dashboards that report the past instead of supporting decisions

This project simulates a **centralized production intelligence system** aligned with Industry 4.0 principles.

---

## ⚙️ Key Features

- Multi-plant production monitoring
- Dynamic date and plant filtering
- KPI cards:
  - Total Production
  - Defects
  - Availability
  - OEE (simulated)
- Interactive charts:
  - Production trends
  - Defect evolution
  - Downtime distribution
  - Availability vs Production
- Short-term production forecasting (7 days)

---

## 📊 Dashboard Preview

> Screenshots generated using simulated production data.

*(Add screenshots here)*

---

## 🔍 How It Works (Technical Overview)

1. Production data is loaded from a simulated CSV dataset.
2. KPIs are calculated dynamically based on user-selected filters.
3. Dash callbacks update KPIs and charts in real time.
4. A simple, explainable regression model forecasts short-term production trends.

---

## 🧪 Data Simulation

The dataset is generated using realistic manufacturing assumptions:
- 3 plants (A, B, C)
- 3 shifts (Morning, Afternoon, Night)
- Production variability, defects, downtime
- Missing values to simulate real industrial noise

This allows testing analytics logic under near-real conditions.

---

## 🔮 Forecasting Approach

- Linear regression on time-indexed production data
- Focus on **interpretability**, not black-box ML
- Designed as a baseline for future ML-based forecasting

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
python app.py

