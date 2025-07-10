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
pressure_ratio_df['Enrollment Pressure Ratio'] = (pressure_ratio_df['Gross Enrollment Ratio'] / pressure_ratio_df['Primary Completion Ratio'].replace(0, 1e-10) * 100).fillna(0)
pressure_ratio_df['Enrollment Pressure Ratio'] = pressure_ratio_df['Enrollment Pressure Ratio'].where(pressure_ratio_df['Primary Completion Ratio'].notna() & (pressure_ratio_df['Primary Completion Ratio'] > 0), 0)
pressure_ratio_df = pressure_ratio_df[pressure_ratio_df['Year'] == pressure_ratio_df['Year'].max()]  # Use latest year

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Education Access Dashboard (F-Pattern v3)", className="text-center mb-4"))),
    dbc.Row([
        dbc.Col([html.Label("Region"), dcc.Dropdown(id="region-filter", options=[{'label': r, 'value': r} for r in df['District'].unique()], value=None, clearable=True)], width=4),
        dbc.Col([html.Label("Year"), dcc.Slider(id="year-slider", min=df['Year'].min(), max=df['Year'].max(), step=1, value=df['Year'].max(), marks={str(y): str(y) for y in df['Year'].unique()})], width=4),
        dbc.Col([html.Label("Metric"), dcc.Dropdown(id="metric-filter", options=[{'label': m, 'value': m} for m in df['Metric'].unique()], value=df['Metric'].unique()[0], clearable=True)], width=4)
    ]),
    dbc.Row([
        dbc.Col([
            html.Button("Download CSV", id="btn-csv", n_clicks=0),
            dcc.Download(id="download-data-csv")
        ], width=2),
        dbc.Col([
            html.Button("Download Map", id="btn-map", n_clicks=0),
            dcc.Download(id="download-map-img")
        ], width=2),
        dbc.Col([
            html.Button("Download Chart", id="btn-chart", n_clicks=0),
            dcc.Download(id="download-chart-img")
        ], width=2)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="district-map1")),  # Enrollment Pressure Ratio
        dbc.Col(dcc.Graph(id="district-map2"))   # Primary Completion Ratio
    ]),
    dbc.Row(dbc.Col(dcc.Graph(id="enrollment-completion-chart"))),  # Fixed to use dbc.Col
    dbc.Row(dbc.Col(dash_table.DataTable(id="data-table", columns=[{"name": i.title(), "id": i} for i in ['District', 'Year', 'Metric', 'Value']], data=df.to_dict('records'), page_size=10, style_table={'overflowX': 'auto'})))
], fluid=True)

@app.callback(
    [Output("district-map1", "figure"), Output("district-map2", "figure"), Output("enrollment-completion-chart", "figure"), Output("data-table", "data")],
    [Input("region-filter", "value"), Input("year-slider", "value"), Input("metric-filter", "value")]
)
def update_dashboard(region, year, metric):
    filtered_df = df[df['Year'] == year]
    if region:
        filtered_df = filtered_df[filtered_df['District'] == region]
    if metric:
        filtered_df = filtered_df[filtered_df['Metric'] == metric]
    
    # Map 1: Enrollment Pressure Ratio
    map_df1 = pressure_ratio_df if not region else pressure_ratio_df[pressure_ratio_df['District'] == region]
    map_df1 = map_df1[map_df1['Year'] == year]
    map_fig1 = px.choropleth_mapbox(
        map_df1, geojson=uganda_geojson,
        locations="District", featureidkey="properties.District", color="Enrollment Pressure Ratio",
        mapbox_style="carto-positron", zoom=6, center={"lat": 1.3733, "lon": 32.2903},
        color_continuous_scale="RdYlGn", range_color=[0, 250],
        title="District Enrollment Pressure Ratio (Green = High Pressure, Red = Low Pressure)"
    ).update_traces(hovertemplate='District: %{location}<br>Pressure Ratio: %{z}%<br>(Green = High Enrollment, Low Completion; Red = Low Pressure)<extra></extra>')
    
    # Map 2: Primary Completion Ratio
    completion_df = df[df['Metric'] == 'Primary Completion Ratio'].pivot(index=['District', 'Year'], columns='Metric', values='Value').reset_index()
    map_df2 = completion_df if not region else completion_df[completion_df['District'] == region]
    map_df2 = map_df2[map_df2['Year'] == year]
    map_fig2 = px.choropleth_mapbox(
        map_df2, geojson=uganda_geojson,
        locations="District", featureidkey="properties.District", color="Primary Completion Ratio",
        mapbox_style="carto-positron", zoom=6, center={"lat": 1.3733, "lon": 32.2903},
        color_continuous_scale="YlGnBu", range_color=[0, 100],
        title="District Primary Completion Ratio (Blue = High Completion, Yellow = Low Completion)"
    ).update_traces(hovertemplate='District: %{location}<br>Completion Ratio: %{z}%<extra></extra>')
    
    # Enrollment vs Completion chart
    chart_df = df[df['Metric'].isin(['Gross Enrollment Ratio', 'Primary Completion Ratio'])].groupby(['Year', 'Metric'])['Value'].mean().reset_index()
    chart_fig = px.line(chart_df, x='Year', y='Value', color='Metric',
                        title='Average Enrollment vs Completion Ratio',
                        labels={'Value': 'Average Ratio', 'Year': 'Year'},
                        markers=True).update_layout(yaxis_range=[0, 200])
    
    return map_fig1, map_fig2, chart_fig, filtered_df.to_dict('records')

@app.callback(
    Output("download-data-csv", "data"),
    Input("btn-csv", "n_clicks"),
    State("region-filter", "value"),
    State("year-slider", "value"),
    State("metric-filter", "value"),
    prevent_initial_call=True
)
def download_csv(n_clicks, region, year, metric):
    filtered_df = df[df['Year'] == year]
    if region:
        filtered_df = filtered_df[filtered_df['District'] == region]
    if metric:
        filtered_df = filtered_df[filtered_df['Metric'] == metric]
    return dcc.send_data_frame(filtered_df.to_csv, "education_data.csv", index=False)

@app.callback(
    Output("download-map-img", "data"),
    Input("btn-map", "n_clicks"),
    State("district-map1", "figure"),  # Download the first map as an example
    prevent_initial_call=True
)
def download_map(n_clicks, fig):
    return dcc.send_bytes(fig.to_image(format="png"), filename="district_map.png")

@app.callback(
    Output("download-chart-img", "data"),
    Input("btn-chart", "n_clicks"),
    State("enrollment-completion-chart", "figure"),
    prevent_initial_call=True
)
def download_chart(n_clicks, fig):
    return dcc.send_bytes(fig.to_image(format="png"), filename="enrollment_completion_chart.png")

if __name__ == '__main__':
    app.run(debug=True)