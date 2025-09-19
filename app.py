import pandas as pd
from dash import Dash, dcc, html
import plotly.express as px

# Leer dataset
df = pd.read_csv("data/production_data.csv", parse_dates=["timestamp"])

# Crear app Dash
app = Dash(__name__)
app.title = "Global Production Dashboard"

# Layout del dashboard
app.layout = html.Div([
    html.H1("Global Production Dashboard", style={'textAlign':'center'}),
    
    html.Div([
        html.Label("Selecciona Planta:"),
        dcc.Dropdown(
            id='plant-dropdown',
            options=[{'label': p, 'value': p} for p in df['plant_id'].unique()],
            value='Plant_A'
        )
    ], style={'width':'30%', 'margin':'auto'}),
    
    dcc.Graph(id='units-graph'),
    dcc.Graph(id='defects-graph')
])

# Callback para actualizar gráficos
@app.callback(
    [dcc.Output('units-graph', 'figure'),
     dcc.Output('defects-graph', 'figure')],
    [dcc.Input('plant-dropdown', 'value')]
)
def update_graphs(selected_plant):
    filtered_df = df[df['plant_id'] == selected_plant]
    
    fig_units = px.line(
        filtered_df, x='timestamp', y='units_produced', color='line_id',
        title=f'Units Produced - {selected_plant}'
    )
    
    fig_defects = px.bar(
        filtered_df, x='timestamp', y='defects', color='line_id',
        title=f'Defects per Line - {selected_plant}'
    )
    
    return fig_units, fig_defects

# Ejecutar app
if __name__ == '__main__':
    app.run_server(debug=True)
