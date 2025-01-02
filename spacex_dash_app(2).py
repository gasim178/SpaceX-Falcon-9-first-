# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Get unique launch sites from the DataFrame
launch_sites = spacex_df['Launch Site'].unique()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     *({'label': site, 'value': site} for site in launch_sites)  # Use actual site names
                 ],
                 value='ALL',  # Default value
                 placeholder="Select a Launch Site here",
                 searchable=True),

    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                    min=int(spacex_df['Payload Mass (kg)'].min()),
                    max=int(spacex_df['Payload Mass (kg)'].max()),
                    value=[int(spacex_df['Payload Mass (kg)'].min()), int(spacex_df['Payload Mass (kg)'].max())],
                    marks={i: str(i) for i in range(0, int(spacex_df['Payload Mass (kg)'].max()) + 1000, 1000)},
                    step=100),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback for success-pie-chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(spacex_df, names='class', title='Total Success Launches for All Sites')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        if not filtered_df.empty:  # Check if DataFrame is empty
            fig = px.pie(filtered_df, names='class', title=f'Success vs. Failed Launches for {selected_site}')
        else:  # Handle empty DataFrame case
            fig = px.pie(names=[], title=f'No Launches Found for {selected_site}')  # Optional: message for no data
            fig.update_traces(textinfo='none')  # Hide text labels if empty
    return fig

# TASK 4: Callback for success-payload-scatter-chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_plot(selected_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    # If a specific site is selected, filter by that site
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    # Create a scatter plot using Plotly
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        title='Payload vs. Launch Success',
        labels={'class': 'Launch Success (0 = Failure, 1 = Success)'},
        color='class',  # Optionally color by success/failure
        color_continuous_scale=px.colors.sequential.Blues
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
