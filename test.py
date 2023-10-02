import dash
from dash import html, dcc

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(
        id='map',
        figure={
            'layout': {
                'mapbox': {
                    'style': "stamen-terrain",
                    'center': {'lat': 51.8007, 'lon': -4.9691},
                    'zoom': 5
                },
                'margin': {"r": 0, "t": 0, "l": 0, "b": 0}
            }
        }
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)
