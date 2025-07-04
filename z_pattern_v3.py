import dash
from dash import dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import json
from dash.exceptions import PreventUpdate

df = pd.read_csv('education_data_long.csv')
with open('uganda_districts.json') as f:
    uganda_geojson = json.load(f)

# Prepare Enrollment Pressure Ratio data
enrollment_df = df[df['Metric'] == 'Gross Enrollment Ratio'].pivot(index=['District', 'Year'], columns='Metric', values='Value').reset_index()
completion_df = df[df['Metric'] == 'Primary Completion Ratio'].pivot(index=['District', 'Year'], columns='Metric', values='Value').reset_index()
pressure_ratio_df = pd.merge(enrollment_df, completion_df, on=['District', 'Year'], how='inner')
pressure_ratio_df['Enrollment Pressure Ratio'] = (pressure_ratio_df['Gross Enrollment Ratio'] / pressure_ratio_df['Primary Completion Ratio'].replace(0, 1e-10) * 100).fillna(0)  # Uncapped formula
pressure_ratio_df['Enrollment Pressure Ratio'] = pressure_ratio_df['Enrollment Pressure Ratio'].where(pressure_ratio_df['Primary Completion Ratio'].notna() & (pressure_ratio_df['Primary Completion Ratio'] > 0), 0)
pressure_ratio_df = pressure_ratio_df[pressure_ratio_df['Year'] == pressure_ratio_df['Year'].max()]  # Use latest year

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Education Access Dashboard (Z-Pattern v3)", className="text-center mb-4"))),
    dbc.Row([
        dbc.Col([html.Label("Region"), dcc.Dropdown(id="region-filter-z", options=[{'label': r, 'value': r} for r in df['District'].unique()], value=None, clearable=True)], width=4),
        dbc.Col([html.Label("Year"), dcc.Slider(id="year-slider-z", min=df['Year'].min(), max=df['Year'].max(), step=1, value=df['Year'].max(), marks={str(y): str(y) for y in df['Year'].unique()})], width=4),
        dbc.Col([html.Label("Metric"), dcc.Dropdown(id="metric-filter-z", options=[{'label': m, 'value': m} for m in df['Metric'].unique()], value=df['Metric'].unique()[0], clearable=True)], width=4)
    ]),
    dbc.Row([
        dbc.Col([html.Div(f"Mean {m}: {df[df['Metric'] == m]['Value'].mean():.0f}", className="card p-3 bg-light text-dark") for m in df['Metric'].unique()[:2]], width=6),
        dbc.Col([
            html.Button("Download CSV", id="btn-csv-z", n_clicks=0),
            dcc.Download(id="download-data-csv-z")
        ], width=3),
        dbc.Col([
            html.Button("Download Map", id="btn-map-z", n_clicks=0),
            dcc.Download(id="download-map-img-z")
        ], width=3),
        dbc.Col([
            html.Button("Download Chart", id="btn-chart-z", n_clicks=0),
            dcc.Download(id="download-chart-img-z")
        ], width=3)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="district-map-z"), width=6),
        dbc.Col(dcc.Graph(id="enrollment-completion-chart-z"), width=6)
    ]),
    dbc.Row([
        dbc.Col(dash_table.DataTable(id="data-table-z", columns=[{"name": i.title(), "id": i} for i in df.columns], data=df.to_dict('records'), page_size=10, style_table={'overflowX': 'auto'}), width=6),
        dbc.Col([html.Div(f"Mean {m}: {df[df['Metric'] == m]['Value'].mean():.0f}", className="card p-3 bg-light text-dark") for m in df['Metric'].unique()[2:]], width=6)
    ])
], fluid=True)

@app.callback(
    [Output("district-map-z", "figure"), Output("enrollment-completion-chart-z", "figure"), Output("data-table-z", "data")],
    [Input("region-filter-z", "value"), Input("year-slider-z", "value"), Input("metric-filter-z", "value")]
)
def update_dashboard_z(region, year, metric):
    filtered_df = df[df['Year'] == year] if year is not None else df
    if region:
        filtered_df = filtered_df[filtered_df['District'] == region]
    if metric:
        filtered_df = filtered_df[filtered_df['Metric'] == metric]
    
    # Map figure with Enrollment Pressure Ratio
    map_df = pressure_ratio_df if not region else pressure_ratio_df[pressure_ratio_df['District'] == region]
    map_df = map_df[map_df['Year'] == year]
    map_fig = px.choropleth_mapbox(
        map_df, geojson=uganda_geojson,
        locations="District", featureidkey="properties.District", color="Enrollment Pressure Ratio",
        mapbox_style="carto-positron", zoom=6, center={"lat": 1.3733, "lon": 32.2903},
        color_continuous_scale="RdYlGn", range_color=[0, 250],  # Expanded to 0-250 for better granularity
        title="District Enrollment Pressure Ratio (Green = High Pressure, Red = Low Pressure)"
    ).update_traces(hovertemplate='District: %{location}<br>Enrollment Pressure Ratio: %{z}%<br>(Green = High Enrollment, Low Completion; Red = Low Pressure or Anomalies)<extra></extra>')
    
    # Enrollment vs Completion chart
    chart_df = df[df['Metric'].isin(['Gross Enrollment Ratio', 'Primary Completion Ratio'])].groupby(['Year', 'Metric'])['Value'].mean().reset_index()
    chart_fig = px.line(chart_df, x='Year', y='Value', color='Metric',
                        title='Average Enrollment vs Completion Ratio',
                        labels={'Value': 'Average Ratio', 'Year': 'Year'},
                        markers=True).update_layout(yaxis_range=[0, 200])
    
    return map_fig, chart_fig, filtered_df.to_dict('records')

@app.callback(
    Output("download-data-csv-z", "data"),
    Input("btn-csv-z", "n_clicks"),
    State("region-filter-z", "value"),
    State("year-slider-z", "value"),
    State("metric-filter-z", "value"),
    prevent_initial_call=True
)
def download_csv_z(n_clicks, region, year, metric):
    filtered_df = df[df['Year'] == year]
    if region:
        filtered_df = filtered_df[filtered_df['District'] == region]
    if metric:
        filtered_df = filtered_df[filtered_df['Metric'] == metric]
    return dcc.send_data_frame(filtered_df.to_csv, "education_data.csv", index=False)

@app.callback(
    Output("download-map-img-z", "data"),
    Input("btn-map-z", "n_clicks"),
    State("district-map-z", "figure"),
    prevent_initial_call=True
)
def download_map_z(n_clicks, fig):
    return dcc.send_bytes(fig.to_image(format="png"), filename="district_map.png")

@app.callback(
    Output("download-chart-img-z", "data"),
    Input("btn-chart-z", "n_clicks"),
    State("enrollment-completion-chart-z", "figure"),
    prevent_initial_call=True
)
def download_chart_z(n_clicks, fig):
    return dcc.send_bytes(fig.to_image(format="png"), filename="enrollment_completion_chart.png")

if __name__ == '__main__':
    app.run(debug=True)