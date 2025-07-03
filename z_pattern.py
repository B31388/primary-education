import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import json

# Load data
df = pd.read_csv('education_data_long.csv')
with open('uganda_districts.json') as f:
    uganda_geojson = json.load(f)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Education Access Dashboard (Z-Pattern)", className="text-center mb-4"))),
    dbc.Row([
        dbc.Col([html.Label("Region"), dcc.Dropdown(id="region-filter-z", options=[{'label': r, 'value': r} for r in df['District'].unique()], value=None, clearable=True)], width=4),
        dbc.Col([html.Label("Year"), dcc.Slider(id="year-slider-z", min=df['Year'].min(), max=df['Year'].max(), step=1, value=df['Year'].min(), marks={str(y): str(y) for y in df['Year'].unique()})], width=4),
        dbc.Col([html.Label("Metric"), dcc.Dropdown(id="metric-filter-z", options=[{'label': m, 'value': m} for m in df['Metric'].unique()], value=df['Metric'].unique()[0], clearable=True)], width=4)
    ]),
    dbc.Row([
        dbc.Col([html.Div(f"Mean {m}: {df[df['Metric'] == m]['Value'].mean():.0f}", className="card p-3 bg-light text-dark") for m in df['Metric'].unique()[:2]], width=6),
        dbc.Col(dcc.Graph(id="district-map-z"), width=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="bar-chart-z"), width=6),
        dbc.Col(dash_table.DataTable(id="data-table-z", columns=[{"name": i.title(), "id": i} for i in df.columns], data=df.to_dict('records'), page_size=10, style_table={'overflowX': 'auto'}), width=6)
    ]),
    dbc.Row([
        dbc.Col([html.Div(f"Mean {m}: {df[df['Metric'] == m]['Value'].mean():.0f}", className="card p-3 bg-light text-dark") for m in df['Metric'].unique()[2:]], width=6),
        dbc.Col(html.Div(), width=6)  # Placeholder for layout balance
    ])
])

@app.callback(
    [Output("district-map-z", "figure"), Output("bar-chart-z", "figure"), Output("data-table-z", "data")],
    [Input("region-filter-z", "value"), Input("year-slider-z", "value"), Input("metric-filter-z", "value")]
)
def update_dashboard_z(region, year, metric):
    filtered_df = df[df['Year'] == year] if year is not None else df
    if region:
        filtered_df = filtered_df[filtered_df['District'] == region]
    if metric:
        filtered_df = filtered_df[filtered_df['Metric'] == metric]
    map_fig = px.choropleth_mapbox(
        filtered_df, geojson=uganda_geojson,
        locations="District", featureidkey="properties.District", color="Value",
        mapbox_style="carto-positron", zoom=6, center={"lat": 1.3733, "lon": 32.2903},
        color_continuous_scale="Viridis", range_color=[0, 200]
    )
    bar_fig = px.bar(filtered_df, x="District", y="Value", color="Value", title=f"{metric} by District")
    return map_fig, bar_fig, filtered_df.to_dict('records')

if __name__ == '__main__':
    app.run(debug=True)