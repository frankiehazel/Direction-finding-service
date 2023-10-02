import dash
import mgrs
import plotly.graph_objects as go
from dash import html, dcc
from dash.dependencies import Output, Input, State
import math
import json

# Initialize the Dash app
app = dash.Dash(__name__)

color_dict = {
    'S1': 'blue',
    'S2': 'red',
    'S3': 'green',
    'S4': 'purple',
    'S5': 'orange',
    'S6': 'pink',
    'SGC 1': 'cyan',
    'SGC 2': 'magenta',
    'SGC 3': 'yellow',
    'TSARC 1': 'brown',
    'TSARC 2': 'grey',
    'TSARC 3': 'black',
}

# List of sensor names
sensor_names = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'SGC 1', 'SGC 2', 'SGC 3', 'TSARC 1', 'TSARC 2', 'TSARC 3']

# Define the layout of the app
app.layout = html.Div([

    # Title
    html.H1("Interactive Map", style={'textAlign': 'center', 'color': '#00FF00'}),

    # Hidden Div for storing sensor coordinates
    html.Div(id='sensor-coords-store', style={'display': 'none'}),

    # Controls for Adding Sensors
    html.Div([
        html.Label("Select Sensor:", style={'color': '#00FF00'}),
        dcc.Dropdown(
            id='sensor-dropdown',
            options=[{'label': name, 'value': name} for name in sensor_names],
            value='S1',  # default value
            style={'width': '80%'}
        ),
        html.Label("Enter Coordinates or MGRS:", style={'color': '#00FF00'}),
        dcc.Input(id='location-input', type='text', placeholder='e.g., 45.372, -121.6972 or 33TWN0000466206',
                  style={'width': '80%'}),
        html.Button("Add Sensor", id='add-sensor-button', style={'width': '80%'}),
    ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '0 1%'}),

    # Controls for Adding Bearings
    html.Div([
        html.Label("Select Sensor:", style={'color': '#00FF00'}),
        dcc.Dropdown(id='bearing-sensor-dropdown',
                     options=[{'label': name, 'value': name} for name in sensor_names],
                     style={'width': '80%'}),
        html.Label("Enter Bearing Angle:", style={'color': '#00FF00'}),
        dcc.Input(id='bearing-input', type='number', min=0, max=360, step=1, style={'width': '80%'}),
        html.Label("Select Bearing Length:", style={'color': '#00FF00'}),
        dcc.Slider(
            id='bearing-length-slider',
            min=0.01,  # Minimum length
            max=1,  # Maximum length
            value=0.05,  # Default length
            step=0.1,  # Step size
            marks={}  # No labels on the slider
        ),
        html.Button("Add Bearing", id='add-bearing-button', style={'width': '80%'}),
    ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '0 1%'}),
    # Map
    html.Div([
        dcc.Graph(
            id='map',
            config={'scrollZoom': True, 'displayModeBar': True},
            figure={
                'layout': {
                    'mapbox': {
                        'style': "open-street-map",
                        'center': {'lat': 51.8007, 'lon': -4.9691},
                        'zoom': 10
                    },
                    'margin': {"r": 0, "t": 0, "l": 0, "b": 0}
                }
            }
        ),
        html.Div("Add first sensor to see map", style={
            'textAlign': 'center',
            'color': '#FFFFFF',
            'fontSize': '44px',
            'backgroundColor': 'rgba(0, 0, 0, 0.8)',  # Background color with transparency
            'padding': '20px'}),
    ], style={'height': '80vh', 'width': '80vw', 'margin': '0 auto'}),
], style={  # <-- This is the correct place to close the outer html.Div
    'backgroundImage': 'url("/assets/background.jpg")',
    'backgroundSize': 'cover',
    'backgroundPosition': 'center',
    'marginBottom': 50,
    'marginTop': 25

})


@app.callback(
    [Output('map', 'figure'),
     Output('bearing-sensor-dropdown', 'options'),
     Output('sensor-coords-store', 'children')],
    [Input('add-sensor-button', 'n_clicks'),
     Input('add-bearing-button', 'n_clicks')],
    [State('sensor-dropdown', 'value'),
     State('location-input', 'value'),
     State('bearing-sensor-dropdown', 'value'),
     State('bearing-input', 'value'),
     State('bearing-length-slider', 'value'),
     State('sensor-coords-store', 'children'),
     State('map', 'figure')],
    prevent_initial_call=True  # Prevent the callback from firing on app load
)
def update_map(add_sensor_clicks, add_bearing_clicks, selected_sensor, location_input,
               bearing_sensor, bearing_angle, bearing_length,
               stored_sensor_coords, current_fig):
    sensor_coords = json.loads(stored_sensor_coords) if stored_sensor_coords else {}
    fig = go.Figure(current_fig)  # Create a new figure based on the current figure
    fig.update_layout(showlegend=False)

    # Get the callback context to determine which button was clicked
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    _, lon = None, None  # Initialize lat and lon to None

    if button_id == 'add-sensor-button' and add_sensor_clicks is not None:
        # Parse the location input
        location_parts = location_input.split(',')
        if len(location_parts) == 2:
            try:
                lat, lon = float(location_parts[0]), float(location_parts[1])
            except ValueError:
                return dash.no_update, dash.no_update, dash.no_update  # Exit if inputs are invalid
        else:
            # Assume MGRS and convert to lat/lon
            converter = mgrs.MGRS()
            try:
                lat, lon = converter.toLatLon(location_input)
            except (ValueError, mgrs.MGRSError):
                return dash.no_update, dash.no_update, dash.no_update  # Exit if inputs are invalid

        # Add the new sensor to the map and update the sensor coordinates
        sensor_coords[selected_sensor] = (lat, lon)
        sensor_color = color_dict.get(selected_sensor, 'black')  # default to black if sensor not found in color_dict
        sensor_marker = go.Scattermapbox(
            lat=[lat],
            lon=[lon],
            mode='markers',
            marker=go.scattermapbox.Marker(size=10, color=sensor_color),
            name=selected_sensor
        )
        fig.add_trace(sensor_marker)
        # Ensure a sensor is selected and a bearing angle is entered

    elif button_id == 'add-bearing-button' and add_bearing_clicks is not None:

        # Ensure a sensor is selected and a bearing angle is entered

        if bearing_sensor not in sensor_coords or bearing_angle is None:
            return dash.no_update, dash.no_update, dash.no_update  # Exit if inputs are invalid

            # Get the coordinates of the selected sensor
        lat, lon = sensor_coords[bearing_sensor]

        # Calculate the end point of the bearing line
        bearing_radians = math.radians(bearing_angle)
        scaling_factor = 5  # Adjust this value to get the desired bearing line length
        delta_lat = bearing_length * scaling_factor * math.cos(bearing_radians)
        delta_lon = bearing_length * scaling_factor * math.sin(bearing_radians)
        end_lat = lat + delta_lat
        end_lon = lon + delta_lon

        # Add a new line trace for the bearing
        bearing_color = color_dict.get(bearing_sensor, 'black')  # default to black if sensor not found in color_dict
        bearing_line = go.Scattermapbox(
            lat=[lat, end_lat],
            lon=[lon, end_lon],
            mode='lines',
            line=dict(width=0.5, color=bearing_color),
            name=f'{bearing_sensor} Bearing'
        )
        fig.add_trace(bearing_line)
        # Update sensor coordinates and dropdown options

    updated_sensor_coords = json.dumps(sensor_coords)
    return fig, [{'label': sensor, 'value': sensor} for sensor in sensor_coords], updated_sensor_coords


updated_config = {'scrollZoom': True, 'displayModeBar': True}

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
