import pandas as pd
import numpy as np
from datetime import timedelta

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# ============================
# 1. Cargar datos
# ============================
df = pd.read_csv("data/datos_produccion.csv", parse_dates=["Fecha"])

# ============================
# 2. Inicializar app
# ============================
app = dash.Dash(__name__)
app.title = "Dashboard Producción Global"

# ============================
# 3. Layout con Tabs
# ============================
app.layout = html.Div([
    html.H1("🏭 Dashboard de Producción Global", 
            style={"textAlign": "center", "color": "#2C3E50"}),

    dcc.Tabs(id="tabs", value="tab-operativa", children=[
        dcc.Tab(label="📊 Vista Operativa", value="tab-operativa"),
        dcc.Tab(label="🔮 Análisis Avanzado (Forecast)", value="tab-forecast")
    ]),

    html.Div(id="tabs-content")
])

# ============================
# 4. Layout de cada tab
# ============================

# -------- Vista operativa --------
operativa_layout = html.Div([
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

    html.Div(id="kpi-cards", style={
        "display": "flex",
        "justifyContent": "space-around",
        "marginTop": "20px"
    }),

    html.Hr(),

    html.Div([
        html.Div([dcc.Graph(id="grafico-produccion")],
                 style={"width": "48%", "display": "inline-block", "padding": "10px"}),

        html.Div([dcc.Graph(id="grafico-defectos")],
                 style={"width": "48%", "display": "inline-block", "padding": "10px"})
    ]),

    html.Div([
        html.Div([dcc.Graph(id="grafico-paros")],
                 style={"width": "48%", "display": "inline-block", "padding": "10px"}),

        html.Div([dcc.Graph(id="grafico-dispersion")],
                 style={"width": "48%", "display": "inline-block", "padding": "10px"})
    ])
])

# -------- Forecast --------
forecast_layout = html.Div([
    html.Div([
        html.Label("Selecciona Planta para Forecast:"),
        dcc.Dropdown(
            id="planta-forecast",
            options=[{"label": p, "value": p} for p in df["Planta"].unique()],
            value=df["Planta"].unique()[0],
            multi=False
        )
    ], style={"width": "50%", "margin": "0 auto", "padding": "20px"}),

    html.Div([dcc.Graph(id="grafico-forecast")])
])

# ============================
# 5. Callback para manejar Tabs
# ============================
@app.callback(Output("tabs-content", "children"),
              Input("tabs", "value"))
def render_content(tab):
    if tab == "tab-operativa":
        return operativa_layout
    elif tab == "tab-forecast":
        return forecast_layout


# ============================
# 6. Callbacks Vista Operativa
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
def update_operativa(planta, start_date, end_date):
    dff = df[(df["Planta"] == planta) &
             (df["Fecha"] >= start_date) &
             (df["Fecha"] <= end_date)]

    total_prod = dff["Produccion"].sum()
    total_def = dff["Defectos"].sum()
    prom_disp = round(dff["Disponibilidad_%"].mean(), 2)

    calidad = 1 - (total_def / total_prod) if total_prod > 0 else 0
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

    fig_prod = px.line(dff, x="Fecha", y="Produccion", markers=True,
                       title=f"Producción en el tiempo - {planta}",
                       template="plotly_white")

    fig_def = px.bar(dff, x="Fecha", y="Defectos",
                     title=f"Defectos en el tiempo - {planta}",
                     template="plotly_white")

    fig_paros = px.box(dff, y="Paros_min",
                       title=f"Distribución de Paros (min) - {planta}",
                       template="plotly_white")

    fig_disp = px.scatter(dff, x="Produccion", y="Disponibilidad_%", size="Defectos",
                          color="Turno", template="plotly_white",
                          title=f"Disponibilidad vs Producción - {planta}")

    return kpis, fig_prod, fig_def, fig_paros, fig_disp


# ============================
# 7. Callback Forecast
# ============================
@app.callback(
    Output("grafico-forecast", "figure"),
    Input("planta-forecast", "value")
)
def update_forecast(planta):
    dff = df[df["Planta"] == planta].sort_values("Fecha")

    # Preparar datos para regresión lineal simple
    dff["t"] = np.arange(len(dff))  # índice de tiempo
    X = dff["t"].values
    y = dff["Produccion"].values

    # Calcular regresión lineal (coeficientes)
    coef = np.polyfit(X, y, 1)  # grado 1 → recta
    poly = np.poly1d(coef)

    # Predicción para los próximos 7 días
    last_t = X[-1]
    future_t = np.arange(last_t+1, last_t+8)
    future_dates = [dff["Fecha"].max() + timedelta(days=i) for i in range(1, 8)]
    future_pred = poly(future_t)

    # Graficar histórico + forecast
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dff["Fecha"], y=dff["Produccion"],
                             mode="lines+markers", name="Histórico"))
    fig.add_trace(go.Scatter(x=future_dates, y=future_pred,
                             mode="lines+markers", name="Forecast",
                             line=dict(dash="dot", color="red")))

    fig.update_layout(title=f"Forecast de Producción (7 días) - {planta}",
                      template="plotly_white",
                      xaxis_title="Fecha", yaxis_title="Producción")
    return fig


# ============================
# 8. Ejecutar servidor
# ============================
if __name__ == "__main__":
    app.run_server(debug=True)
