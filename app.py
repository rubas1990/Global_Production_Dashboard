import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# ============================
# 1. Cargar datos
# ============================
df = pd.read_csv("datos_produccion.csv", parse_dates=["Fecha"])

# ============================
# 2. Inicializar la app
# ============================
app = dash.Dash(__name__)
app.title = "Dashboard Producción Global"

# ============================
# 3. Layout del dashboard
# ============================
app.layout = html.Div([
    html.H1("📊 Dashboard Producción Global", style={"textAlign": "center"}),

    # --------------------------
    # Filtros
    # --------------------------
    html.Div([
        html.Label("Selecciona Planta:"),
        dcc.Dropdown(
            id="planta-dropdown",
            options=[{"label": p, "value": p} for p in df["Planta"].unique()],
            value=df["Planta"].unique()[0],
            multi=False
        ),

        html.Label("Rango de Fechas:"),
        dcc.DatePickerRange(
            id="fecha-picker",
            start_date=df["Fecha"].min(),
            end_date=df["Fecha"].max(),
            display_format="YYYY-MM-DD"
        )
    ], style={"width": "40%", "display": "inline-block", "verticalAlign": "top"}),

    html.Br(),

    # --------------------------
    # KPIs
    # --------------------------
    html.Div(id="kpi-cards", style={
        "display": "flex",
        "justifyContent": "space-around",
        "marginTop": "20px"
    }),

    html.Br(),

    # --------------------------
    # Gráficos
    # --------------------------
    html.Div([
        dcc.Graph(id="grafico-produccion"),
        dcc.Graph(id="grafico-defectos")
    ])
])

# ============================
# 4. Callbacks
# ============================

# Filtro + actualización de KPIs y gráficos
@app.callback(
    [Output("kpi-cards", "children"),
     Output("grafico-produccion", "figure"),
     Output("grafico-defectos", "figure")],
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

    kpis = [
        html.Div([
            html.H3("Producción Total"),
            html.P(f"{total_prod:,}")
        ], style={"border": "1px solid #ccc", "padding": "10px", "borderRadius": "10px", "width": "25%", "textAlign": "center"}),

        html.Div([
            html.H3("Defectos Totales"),
            html.P(f"{total_def:,}")
        ], style={"border": "1px solid #ccc", "padding": "10px", "borderRadius": "10px", "width": "25%", "textAlign": "center"}),

        html.Div([
            html.H3("Disponibilidad Promedio"),
            html.P(f"{prom_disp}%")
        ], style={"border": "1px solid #ccc", "padding": "10px", "borderRadius": "10px", "width": "25%", "textAlign": "center"})
    ]

    # ============================
    # Gráfico de Producción
    # ============================
    fig_prod = px.line(dff, x="Fecha", y="Produccion", title=f"Producción - {planta}")
    fig_prod.update_traces(mode="lines+markers")

    # ============================
    # Gráfico de Defectos
    # ============================
    fig_def = px.bar(dff, x="Fecha", y="Defectos", title=f"Defectos - {planta}")

    return kpis, fig_prod, fig_def


# ============================
# 5. Ejecutar servidor
# ============================
if __name__ == "__main__":
    app.run_server(debug=True)
