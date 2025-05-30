import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import os

# Cargar datos
try:
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "crime_dataset_india.csv"), sep=";")
except FileNotFoundError:
    print("Error: No se encontró el archivo 'crime_dataset_india.csv'")
    exit()

# Validar columnas
required_columns = ['City', 'Crime Description', 'Victim Gender', 'Weapon Used', 'Date of Occurrence']
if not all(col in df.columns for col in required_columns):
    raise ValueError("Faltan columnas requeridas en el dataset")

# Limpiar columnas
df.columns = df.columns.str.strip()

# Convertir fecha
df['Date of Occurrence'] = pd.to_datetime(df['Date of Occurrence'], errors='coerce')
df = df.dropna(subset=['Date of Occurrence'])
df['Year'] = df['Date of Occurrence'].dt.year

# Normalizar datos
df['Victim Gender'] = df['Victim Gender'].str.lower().str.strip()
df['Weapon Used'] = df['Weapon Used'].str.lower().str.strip()

# Inicializar app
app = dash.Dash(__name__)
app.title = "India Crime Dashboard"
server = app.server  # Exponer Flask server para Gunicorn

# Opciones para dropdowns
crime_options = sorted(df['Crime Description'].dropna().unique())
default_crime = crime_options[0] if crime_options else None
year_options = sorted(df['Year'].dropna().unique())
default_year = year_options[-1] if year_options else None

# Layout
app.layout = html.Div([
    html.H1("🔍 India Crime Dashboard", style={'textAlign': 'center'}),
    html.Div(id='error_message', style={'color': 'red', 'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Label("Descripción del crimen"),
            dcc.Dropdown(
                id='crime_desc',
                options=[{'label': i, 'value': i} for i in crime_options],
                value=default_crime
            )
        ], style={'width': '24%', 'display': 'inline-block', 'margin': '1%'}),
        html.Div([
            html.Label("Año"),
            dcc.Dropdown(
                id='year',
                options=[{'label': y, 'value': y} for y in year_options],
                value=default_year
            )
        ], style={'width': '24%', 'display': 'inline-block', 'margin': '1%'}),
        html.Div([
            html.Label("Tipo de gráfico"),
            dcc.RadioItems(
                id='chart_type',
                options=[{'label': 'Barras', 'value': 'bar'}, {'label': 'Línea', 'value': 'line'}],
                value='bar',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '24%', 'display': 'inline-block', 'margin': '1%'}),
        html.Div([
            html.Label("Modo oscuro"),
            dcc.Checklist(
                id='dark_mode',
                options=[{'label': 'Activar', 'value': 'on'}],
                value=[]
            )
        ], style={'width': '24%', 'display': 'inline-block', 'margin': '1%'})
    ], style={'padding': '10px'}),

    html.Div([
        html.Div([dcc.Graph(id='graph1')], style={'width': '48%', 'display': 'inline-block', 'margin': '1%'}),
        html.Div([dcc.Graph(id='graph2')], style={'width': '48%', 'display': 'inline-block', 'margin': '1%'}),
    ]),
    html.Div([
        html.Div([dcc.Graph(id='graph3')], style={'width': '48%', 'display': 'inline-block', 'margin': '1%'}),
        html.Div([dcc.Graph(id='graph4')], style={'width': '48%', 'display': 'inline-block', 'margin': '1%'}),
    ]),
])

# Callback
@app.callback(
    [Output('graph1', 'figure'),
     Output('graph2', 'figure'),
     Output('graph3', 'figure'),
     Output('graph4', 'figure'),
     Output('error_message', 'children')],
    [Input('crime_desc', 'value'),
     Input('year', 'value'),
     Input('chart_type', 'value'),
     Input('dark_mode', 'value')]
)
def update_graphs(crime_desc, year, chart_type, dark_mode):
    template = 'plotly_dark' if 'on' in dark_mode else 'plotly_white'

    dff = df[(df['Crime Description'] == crime_desc) & (df['Year'] == year)]
    if dff.empty:
        empty_fig = px.scatter(title="No hay datos disponibles", template=template)
        return empty_fig, empty_fig, empty_fig, empty_fig, "No hay datos para la selección actual"

    # Gráfico 1: frecuencia por ciudad
    city_counts = dff['City'].value_counts().nlargest(10).reset_index()
    city_counts.columns = ['City', 'Count']
    fig1 = px.bar(city_counts, x='City', y='Count', title='Top 10 ciudades con más crímenes', template=template)

    # Gráfico 2: evolución por año
    yearly = df[df['Crime Description'] == crime_desc].groupby('Year').size().reset_index(name='Count')
    if chart_type == 'bar':
        fig2 = px.bar(yearly, x='Year', y='Count', title='Evolución por año', template=template)
    else:
        fig2 = px.line(yearly, x='Year', y='Count', title='Evolución por año', template=template)

    # Gráfico 3: por género de la víctima
    gender_counts = dff['Victim Gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    fig3 = px.pie(gender_counts, names='Gender', values='Count', title='Distribución por género', template=template)

    # Gráfico 4: arma usada
    weapon = dff['Weapon Used'].value_counts().nlargest(10).reset_index()
    weapon.columns = ['Weapon', 'Count']
    fig4 = px.bar(weapon, x='Weapon', y='Count', title='Armas más usadas', template=template)

    return fig1, fig2, fig3, fig4, ""

# Para desarrollo únicamente (no necesario para Gunicorn)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run_server(host='0.0.0.0', port=port, debug=True)
