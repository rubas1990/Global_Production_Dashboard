# app.py
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import os
# ============================
# 1. Cargar y normalizar datos (robusto)
# ============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "production_data.csv")

# Leer CSV
df_raw = pd.read_csv(DATA_PATH)

# --- Normalizar headers ---
df_raw.columns = (
    df_raw.columns
    .str.strip()        # quitar espacios
    .str.lower()        # pasar a minúsculas
)

# Mapeo canónico de columnas
COLUMN_MAP = {
    "plant_id": "Planta",
    "line_id": "Linea",
    "timestamp": "Fecha",
    "units_produced": "Produccion",
    "defects": "Defectos",
}

# Ver qué columnas están realmente presentes
present = set(df_raw.columns)
expected = set(COLUMN_MAP.keys())

missing_raw = expected - present
if missing_raw:
    raise ValueError(
        f"CSV schema mismatch. Missing columns in raw data: {missing_raw}. "
        f"Found columns: {list(df_raw.columns)}"
    )

# Renombrar a modelo interno
df = df_raw.rename(columns=COLUMN_MAP)

# --- Tipos ---
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

if df["Fecha"].isna().any():
    raise ValueError("Some timestamps could not be parsed into datetime.")

# --- Enriquecimiento ---
df["Paros_min"] = (df["Defectos"] * 5).clip(0, 120)
df["Disponibilidad_%"] = (100 - df["Paros_min"] * 0.5).clip(70, 100)

# Turno derivado (industrial)
df["Turno"] = df["Fecha"].dt.hour.apply(
    lambda h: "Mañana" if 6 <= h < 14 else "Tarde" if 14 <= h < 22 else "Noche"
)

# --- Validación final ---
required_cols = [
    "Planta", "Linea", "Fecha", "Produccion",
    "Defectos", "Paros_min", "Disponibilidad_%", "Turno"
]

missing = set(required_cols) - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns after normalization: {missing}")

# ============================
# 2. Inicializar la app
# ============================
app = dash.Dash(__name__)
app.title = "Dashboard Producción Global"

# ============================
# 3. Layout del dashboard
# ============================
app.layout = html.Div([
    html.H1("🏭 Dashboard de Producción Global", style={"textAlign": "center"}),

    # --------------------------
    # Filtros
    # --------------------------
    html.Div([
        html.Div([
            html.Label("Selecciona Planta:"),
            dcc.Dropdown(
                id="planta-dropdown",
                options=[{"label": p, "value": p} for p in df["Planta"].unique()],
                value=df["Planta"].unique()[0],
                multi=False
            )
        ], style={"width": "45%", "display": "inline-block", "padding": "10px"}),

        html.Div([
            html.Label("Rango de Fechas:"),
            dcc.DatePickerRange(
                id="fecha-picker",
                start_date=df["Fecha"].min(),
                end_date=df["Fecha"].max(),
                display_format="YYYY-MM-DD"
            )
        ], style={"width": "45%", "display": "inline-block", "padding": "10px"})
    ], style={"textAlign": "center"}),

    html.Hr(),

    # --------------------------
    # KPIs
    # --------------------------
    html.Div(id="kpi-cards", style={
        "display": "flex",
        "justifyContent": "space-around",
        "marginTop": "20px"
    }),

    html.Hr(),

    # --------------------------
    # Fila 1 de gráficos
    # --------------------------
    html.Div([
        html.Div([dcc.Graph(id="grafico-produccion")],
                 style={"width": "48%", "display": "inline-block", "padding": "10px"}),

        html.Div([dcc.Graph(id="grafico-defectos")],
                 style={"width": "48%", "display": "inline-block", "padding": "10px"})
    ]),

    # --------------------------
    # Fila 2 de gráficos
    # --------------------------
    html.Div([
        html.Div([dcc.Graph(id="grafico-paros")],
                 style={"width": "48%", "display": "inline-block", "padding": "10px"}),

        html.Div([dcc.Graph(id="grafico-dispersion")],
                 style={"width": "48%", "display": "inline-block", "padding": "10px"})
    ])
])

# ============================
# 4. Callbacks
# ============================
@app.callback(
    [Output("kpi-cards", "children"),
     Output("grafico-produccion", "figure"),
     Output("grafico-defectos", "figure"),
     Output("grafico-paros", "figure"),
     Output("grafico-dispersion", "figure")],
    [Input("planta-dropdown", "value"),
     Input("fecha-picker", "start_date"),
     Input("fecha-picker", "end_date")]
)
def update_dashboard(planta, start_date, end_date):
    # Filtrar datos según planta y rango de fechas
    dff = df[(df["Planta"] == planta) &
             (df["Fecha"] >= start_date) &
             (df["Fecha"] <= end_date)]

    # ============================
    # KPIs
    # ============================
    total_prod = dff["Produccion"].sum()
    total_def = dff["Defectos"].sum()
    prom_disp = round(dff["Disponibilidad_%"].mean(), 2)
    
    # OEE simulado = Disponibilidad * (1 - Defectos/Producción) * 100
    if total_prod > 0:
        calidad = 1 - (total_def / total_prod)
    else:
        calidad = 0
    oee = round((prom_disp/100) * calidad * 100, 2)

    kpis = [
        html.Div([
            html.H3("Producción Total", style={"color": "#2E86C1"}),
            html.H2(f"{total_prod:,}")
        ], style={"border": "1px solid #ccc", "padding": "15px", "borderRadius": "10px", "width": "22%", "textAlign": "center"}),

        html.Div([
            html.H3("Defectos Totales", style={"color": "#C0392B"}),
            html.H2(f"{total_def:,}")
        ], style={"border": "1px solid #ccc", "padding": "15px", "borderRadius": "10px", "width": "22%", "textAlign": "center"}),

        html.Div([
            html.H3("Disponibilidad Promedio", style={"color": "#27AE60"}),
            html.H2(f"{prom_disp}%")
        ], style={"border": "1px solid #ccc", "padding": "15px", "borderRadius": "10px", "width": "22%", "textAlign": "center"}),

        html.Div([
            html.H3("OEE (simulado)", style={"color": "#8E44AD"}),
            html.H2(f"{oee}%")
        ], style={"border": "1px solid #ccc", "padding": "15px", "borderRadius": "10px", "width": "22%", "textAlign": "center"})
    ]

    # ============================
    # Gráfico Producción (línea)
    # ============================
    fig_prod = px.line(dff, x="Fecha", y="Produccion",
                       title=f"Producción en el tiempo - {planta}",
                       markers=True)

    # ============================
    # Gráfico Defectos (barras)
    # ============================
    fig_def = px.bar(dff, x="Fecha", y="Defectos",
                     title=f"Defectos en el tiempo - {planta}")

    # ============================
    # Gráfico Paros (boxplot)
    # ============================
    fig_paros = px.box(dff, y="Paros_min",
                       title=f"Distribución de Paros (min) - {planta}")

    # ============================
    # Gráfico Disponibilidad vs Producción (scatter)
    # ============================
    fig_disp = px.scatter(dff, x="Produccion", y="Disponibilidad_%", size="Defectos",
                          title=f"Disponibilidad vs Producción - {planta}",
                          hover_data=["Turno"])

    return kpis, fig_prod, fig_def, fig_paros, fig_disp


# ============================
# 5. Ejecutar servidor
# ============================
if __name__ == "__main__":
    app.run_server(debug=True)
