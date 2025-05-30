import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# --- Cargar datos ---
df = pd.read_csv("crime_dataset_india.csv")

# --- Preparar fechas ---
df['Month'] = df['Month'].astype(str).str.zfill(2)  # Asegura formato '01'...'12'
df['Year'] = df['Year'].astype(str)
df['Date'] = pd.to_datetime(df['Year'] + '-' + df['Month'])

# --- Inicializar la app ---
app = dash.Dash(__name__)
app.title = "Crime Dashboard India"

# --- Layout ---
app.layout = html.Div(style={'font-family': 'Arial'}, children=[
    html.H1("🔎 Crime Dashboard - India", style={'textAlign': 'center', 'margin': '20px'}),

    html.Div([
        html.Div([
            html.Label("Tipo de crimen"),
            dcc.Dropdown(
                id='crime_type',
                options=[{'label': crime, 'value': crime} for crime in df['Crime Head'].unique()],
                value=df['Crime Head'].unique()[0]
            ),
        ], style={'width': '24%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Año"),
            dcc.Dropdown(
                id='year',
                options=[{'label': y, 'value': y} for y in sorted(df['Year'].unique())],
                value=df['Year'].unique()[0]
            ),
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
    ], style={'padding': '0 20px'}),

    html.Div([
        html.Div([
            dcc.Graph(id='line_graph')
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

# --- Callback principal ---
@app.callback(
    [Output('line_graph', 'figure'),
     Output('bar_chart', 'figure'),
     Output('pie_chart', 'figure'),
     Output('scatter_chart', 'figure')],
    [Input('crime_type', 'value'),
     Input('year', 'value'),
     Input('chart_type', 'value'),
     Input('dark_mode', 'value')]
)
def update_graphs(crime_type, year, chart_type, dark_mode):
    # Tema visual
    template = 'plotly_dark' if 'on' in dark_mode else 'plotly_white'

    # Filtrar datos
    df_filtered = df[df['Crime Head'] == crime_type]
    df_year = df_filtered[df_filtered['Year'] == year]

    # --- Gráfico 1: Línea de tiempo con slider ---
    line_fig = px.line(df_filtered, x='Date', y='Cases Reported', title='Evolución mensual del crimen',
                       template=template)
    line_fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    # --- Gráfico 2: Barras o líneas por región ---
    bar_data = df_year.groupby('Region')['Cases Reported'].sum().reset_index()
    if chart_type == 'bar':
        bar_fig = px.bar(bar_data, x='Region', y='Cases Reported', title='Crímenes por región', template=template)
    else:
        bar_fig = px.line(bar_data, x='Region', y='Cases Reported', title='Crímenes por región', template=template)

    # --- Gráfico 3: Pie por estado ---
    pie_data = df_year.groupby('State/UT')['Cases Reported'].sum().reset_index()
    pie_fig = px.pie(pie_data, names='State/UT', values='Cases Reported', title='Distribución por estado',
                     template=template)

    # --- Gráfico 4: Dispersión (casos vs población si existe, o región) ---
    if 'Population' in df.columns:
        scatter_fig = px.scatter(df_year, x='Population', y='Cases Reported', color='Region',
                                 title='Casos vs Población', size='Cases Reported', template=template)
    else:
        scatter_fig = px.scatter(df_year, x='Region', y='Cases Reported', color='Region',
                                 title='Casos por Región (Distribución)', template=template)

    return line_fig, bar_fig, pie_fig, scatter_fig

# --- Ejecutar servidor ---
if __name__ == '__main__':
    app.run_server(debug=True)