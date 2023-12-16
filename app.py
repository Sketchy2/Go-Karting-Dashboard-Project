import pandas as pd
import plotly as plt
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc


external_stylesheets = [dbc.themes.BOOTSTRAP, '/assets/style.css']


app = Dash(__name__,external_stylesheets=external_stylesheets)

# -- Import and clean data + prepare filtered datasets
df = pd.read_csv("RaceTimes.csv")
print(df)

#Option for races
unique_races = df['RaceID'].unique()
race_dropdown_options = [{'label': race, 'value': race} for race in unique_races]

#Option for drivers
unique_drivers = df['Racer'].unique()
driver_dropdown_options = [{'label':racer,'value': racer} for racer in unique_drivers]

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.Div(
        "Go-Karting Dashboard",
        className = 'Header1'
        ),

    html.Div(
        className = 'Header2'
        ),

    dbc.Container(
        dbc.Alert("Testing Alerts", color = "success"),
        className='p-5'
    ),

    #Dropdown for races
    dcc.Dropdown(id="select_race",
                options=race_dropdown_options,
                multi=False,
                value=None,
                style={'width': "40%"}
                ),
    
    #Dropdown for primary driver
    dcc.Dropdown(id="select_primary_driver",
                options=driver_dropdown_options,
                multi=False,
                value = None,
                style={'width':"40%"}
                ),
    
    #Dropdown for secondary driver
    dcc.Dropdown(id="select_secondary_driver",
                options=[],
                multi=False,
                value = None,
                style={'width':"40%"}
                ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='lapchart', figure={})

])


# ------------------------------------------------------------------------------
# Update second driver callback
@app.callback(
    Output(component_id="select_secondary_driver",component_property='options'),
    Input(component_id="select_primary_driver",component_property='value')
)

def update_secondary_driver_dropdown(selected_primary_driver):
    secondary_driver_filter = df[df['Racer'] != selected_primary_driver]['Racer'].unique()
    secondary_driver_options = [{'label' : racer, 'value' : racer} for racer in secondary_driver_filter]

    return secondary_driver_options




# Update graph callback
@app.callback(
    [Output(component_id='output_container', component_property='children'),
    Output(component_id='lapchart', component_property='figure')],
    [Input(component_id='select_race', component_property='value')],
    [Input(component_id='select_primary_driver', component_property='value')],
    [Input(component_id='select_secondary_driver', component_property='value')]
)

def update_graph(race_selected, primary_driver, secondary_driver):
    container = "The race chosen by user was: {}".format(race_selected)

    df2 = df.copy()
    df2 = df2[df2["RaceID"] == race_selected]
    df2 = df2[df2["Racer"] == primary_driver]

    MainDriverData = go.Scatter(
        x = df2["Lap"],
        y = df2["Lap Time Seconds"],
        mode = 'lines',
        name = 'MainDriverData'
    )


    if secondary_driver and primary_driver != secondary_driver:
        df3 = df.copy()
        df3 = df3[df3["RaceID"] == race_selected]
        df3 = df3[df3["Racer"] == secondary_driver]

        SecondaryDriverData = go.Scatter(
        x = df3["Lap"],
        y = df3["Lap Time Seconds"],
        mode = 'lines',
        name = 'SecondaryDriverData'
    )
        #Creating Graph
        fig = go.Figure(data=[MainDriverData, SecondaryDriverData])

        fig.update_layout(
            title = f"{primary_driver} lap times vs. {secondary_driver} lap times",
            xaxis_title = "Lap",
            yaxis_title = "Lap Time"
        )

    else:
        #Creating Graph
        fig = go.Figure(data=[MainDriverData])

        fig.update_layout(
            title = f"{primary_driver} lap times",
            xaxis_title = "Lap",
            yaxis_title = "Lap Time"
        )

    return container, fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)