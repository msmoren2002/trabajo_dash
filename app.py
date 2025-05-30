import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# --- Cargar datos ---
df = pd.read_csv("crime_dataset_india.csv")

# Asegurar nombres limpios
df.columns = df.columns.str.strip()

# Inicializar app
app = dash.Dash(__name__)
app.title = "Crime Dashboard India"

# Layout
app.layout = html.Div(style={'font-family': 'Arial'}, children=[
    html.H1("🔎 Crime Dashboard - India", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Label("Tipo de crimen"),
            dcc.Dropdown(
                id='crime_type',
                options=[{'label': c, 'value': c} for c in sorted(df['Crime Head'].unique())],
                value=df['Crime Head'].unique()[0]
            )
        ], style={'width': '24%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Año"),
            dcc.Dropdown(
                id='year',
                options=[{'label': y, 'value': y} for y in sorted(df['Year'].unique())],
                value=df['Year'].unique()[0]
            )
        ], style={'width': '24%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Tipo de gráfico (barra o línea)"),
            dcc.RadioItems(
                id='chart_type',
                options=[
                    {'label': '📊 Barras', 'value': 'bar'},
                    {'label': '📈 Línea', 'value': 'line'}
                ],
                value='bar',
                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
            )
        ], style={'width': '24%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Modo oscuro"),
            dcc.Checklist(
                id='dark_mode',
                options=[{'label': 'Activar', 'value': 'on'}],
                value=[]
            )
        ], style={'width': '24%', 'display': 'inline-block', 'padding': '10px'}),
    ]),

    html.Div([
        html.Div([
            dcc.Graph(id='trend_graph')
        ], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='bar_chart')
        ], style={'width': '50%', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.Div([
            dcc.Graph(id='pie_chart')
        ], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='scatter_chart')
        ], style={'width': '50%', 'display': 'inline-block'}),
    ]),
])

# Callback
@app.callback(
    [Output('trend_graph', 'figure'),
     Output('bar_chart', 'figure'),
     Output('pie_chart', 'figure'),
     Output('scatter_chart', 'figure')],
    [Input('crime_type', 'value'),
     Input('year', 'value'),
     Input('chart_type', 'value'),
     Input('dark_mode', 'value')]
)
def update_graphs(crime_type, year, chart_type, dark_mode):
    template = 'plotly_dark' if 'on' in dark_mode else 'plotly_white'

    # Filtro por tipo de crimen y año
    filtered_df = df[df['Crime Head'] == crime_type]
    year_df = df[(df['Year'] == year) & (df['Crime Head'] == crime_type)]

    # 1. Evolución por año (serie de tiempo por año)
    trend_data = filtered_df.groupby('Year')['Cases Reported'].sum().reset_index()
    fig1 = px.line(trend_data, x='Year', y='Cases Reported', title='Crímenes por Año', template=template)

    # 2. Gráfico de barras/linea por región
    region_data = year_df.groupby('Region')['Cases Reported'].sum().reset_index()
    if chart_type == 'bar':
        fig2 = px.bar(region_data, x='Region', y='Cases Reported', title='Casos por Región', template=template)
    else:
        fig2 = px.line(region_data, x='Region', y='Cases Reported', title='Casos por Región', template=template)

    # 3. Gráfico de torta por estado
    state_data = year_df.groupby('State/UT')['Cases Reported'].sum().reset_index()
    fig3 = px.pie(state_data, names='State/UT', values='Cases Reported', title='Distribución por Estado', template=template)

    # 4. Dispersión: Casos vs Regiones
    fig4 = px.scatter(year_df, x='Region', y='Cases Reported', color='Region', 
                      title='Distribución de casos por Región', template=template)

    return fig1, fig2, fig3, fig4

# Ejecutar servidor
if __name__ == '__main__':
    app.run_server(debug=True)
