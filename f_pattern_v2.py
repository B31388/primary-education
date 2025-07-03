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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Education Access Dashboard (F-Pattern)", className="text-center mb-4"))),
    dbc.Row([
        dbc.Col([html.Label("Region"), dcc.Dropdown(id="region-filter", options=[{'label': r, 'value': r} for r in df['District'].unique()], value=None, clearable=True)], width=4),
        dbc.Col([html.Label("Year"), dcc.Slider(id="year-slider", min=df['Year'].min(), max=df['Year'].max(), step=1, value=df['Year'].min(), marks={str(y): str(y) for y in df['Year'].unique()})], width=4),
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
        ], width=2)
    ]),
    dbc.Row(dbc.Col(dcc.Graph(id="district-map"))),
    dbc.Row(dbc.Col(dcc.Graph(id="enrollment-completion-chart"))),
    dbc.Row(dbc.Col(dash_table.DataTable(id="data-table", columns=[{"name": i.title(), "id": i} for i in df.columns], data=df.to_dict('records'), page_size=10, style_table={'overflowX': 'auto'})))
])

@app.callback(
    [Output("district-map", "figure"), Output("enrollment-completion-chart", "figure"), Output("data-table", "data")],
    [Input("region-filter", "value"), Input("year-slider", "value"), Input("metric-filter", "value")]
)
def update_dashboard(region, year, metric):
    filtered_df = df[df['Year'] == year]
    if region:
        filtered_df = filtered_df[filtered_df['District'] == region]
    if metric:
        filtered_df = filtered_df[filtered_df['Metric'] == metric]
    
    # Map figure
    map_fig = px.choropleth_mapbox(
        filtered_df, geojson=uganda_geojson,
        locations="District", featureidkey="properties.District", color="Value",
        mapbox_style="carto-positron", zoom=6, center={"lat": 1.3733, "lon": 32.2903},
        color_continuous_scale="Viridis", range_color=[0, 200]
    ).update_traces(hovertemplate='District: %{location}<br>Value: %{z}<br>Year: %{customdata[0]}<extra></extra>', customdata=filtered_df[['Year']])
    
    # Enrollment vs Completion chart
    chart_df = df[df['Metric'].isin(['Gross Enrollment Ratio', 'Primary Completion Ratio'])].groupby(['Year', 'Metric'])['Value'].mean().reset_index()
    chart_fig = px.line(chart_df, x='Year', y='Value', color='Metric',
                        title='Average Enrollment vs Completion Ratio',
                        labels={'Value': 'Average Ratio', 'Year': 'Year'},
                        markers=True).update_layout(yaxis_range=[0, 200])
    
    return map_fig, chart_fig, filtered_df.to_dict('records')

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
    State("district-map", "figure"),
    prevent_initial_call=True
)
def download_map(n_clicks, fig):
    return dcc.send_bytes(fig.to_image(format="png"), filename="district_map.png")

if __name__ == '__main__':
    app.run(debug=True)