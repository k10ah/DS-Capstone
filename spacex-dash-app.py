# spacex-dash-app.py
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Read SpaceX launch data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', 
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Dropdown for Launch Site
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # Pie chart for success counts
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # Payload range slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # Scatter plot for payload vs success
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback for Pie Chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, 
                     names='Launch Site', 
                     values='class', 
                     title='Total Success Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(filtered_df, 
                     names='class', 
                     title=f'Success vs Failure for {entered_site}')
    return fig

# Callback for Scatter Plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def get_scatter_plot(entered_site, payload_range):
    low, high = payload_range
    if entered_site == 'ALL':
        df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                       (spacex_df['Payload Mass (kg)'] <= high)]
        fig = px.scatter(df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Payload vs Outcome for All Sites')
    else:
        df = spacex_df[(spacex_df['Launch Site'] == entered_site) &
                       (spacex_df['Payload Mass (kg)'] >= low) & 
                       (spacex_df['Payload Mass (kg)'] <= high)]
        fig = px.scatter(df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Payload vs Outcome for {entered_site}')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(port=8050, host='0.0.0.0', debug=True)
