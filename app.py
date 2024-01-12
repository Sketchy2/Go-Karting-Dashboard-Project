import pandas as pd
import numpy as np
import plotly as plt
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc


external_stylesheets = [dbc.themes.BOOTSTRAP, '/assets/style.css']


app = Dash(__name__,external_stylesheets=external_stylesheets)
server = app.server

# -- Import and clean data + prepare filtered datasets
raceTimes = pd.read_csv("RaceTimes.csv")

#Option for races
unique_races = raceTimes['RaceID Name'].unique()
race_dropdown_options = [{'label': race, 'value': race} for race in unique_races]

#Option for drivers
unique_drivers = raceTimes['Racer'].unique()
driver_dropdown_options = [{'label':racer,'value': racer} for racer in unique_drivers]

Driver = ""

driverInfo = pd.read_csv("driverDatabase.csv")

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.Div([ #Sidebar
        
        html.H1("Go-Karting Dashboard",className="title"), #Title

        html.H5("Select Driver: ",className="subtitle"), #"SELECT DRIVER"

        dcc.Dropdown( #Drop down list
            id="select_primary_driver",
            className="driver-dropdown",
            options=driver_dropdown_options,
            multi=False,
            placeholder="Select a Driver",
            value=""),
        html.Div([ #DriverCard
            
            html.Div([ #Driver-card Left
                html.Img(src="", id="driver-card-pic", className="driver-pic"),
                html.Div("",id="driver-card-name",className="driver-card-name")
            ],className="driver-card-left"),

            html.Div([ #Driver-card Right
                html.Div([ #Age Div
                    html.P("Age"),
                    html.P("", id="driver-card-age", className="stat")
                ],className="driver-card-right-category"),

                html.Div([ #Height Div
                    html.P("Height"),
                    html.P("", id="driver-card-height", className="stat")
                ],className="driver-card-right-category"),

                html.Div([ #Average Position Div
                    html.P("Average Position", className="position"),
                    html.P("", id="driver-card-position", className="stat")
                ],className="driver-card-right-category")

            ],className="driver-card-right")
        ],className="driver-card"),
        html.Img(src="assets/Images/Lemans-Lakeside-Track.png", className="track-pic")
    ],className="sidebar"),


    html.Div(
        "",
        className="divider"
    ),


    html.Div([
        html.Div([
            html.Div("Lap Times Comparance",className="graph-subtitle"),
            html.Div([
                html.Div(dcc.Graph(id='lapchart', figure={},className='Chart1'), className="graph1"),
                html.Div([
                    html.Div([
                        html.H3("Select Race:"),
                        dcc.Dropdown(
                        id="select_race",
                        options=race_dropdown_options,
                        multi=False,
                        value="",
                        className="dropdown")]),

                    html.Div([
                        html.H3("Select Driver:"),
                        dcc.Dropdown(
                        id="select_secondary_driver",
                        options=race_dropdown_options,
                        multi=False,
                        value="",
                        className = "dropdown")])
                ],className="slicers")
            ], className="graph1-box")
        ], className="graph1-area"),

        html.Div([
            html.Div("Average Lap Times",className="graph-subtitle"),
            html.Div(
                html.Div(dcc.Graph(id='avgchart', figure={},className='Chart2'), className="graph2"
                ),className="graph2-box")
            ], className="graph2-area")
    ],className="main")
], className="body")


# ------------------------------------------------------------------------------

"""
CALL BACK FOR WHEN PRIMARY DRIVER IS CHOSEN:
    - Update Basics Stats 
    - Update Driver Image
    - Update choices for second driver
    - Update Graphs"""

@app.callback(
    [Output(component_id="driver-card-name",component_property='children'),
    Output(component_id="driver-card-age",component_property='children'),
    Output(component_id="driver-card-height",component_property='children'),
    Output(component_id="select_secondary_driver",component_property="options")],
    Input(component_id="select_primary_driver",component_property='value')
)

def Primary_Driver_Selected(selected_primary_driver):

    if selected_primary_driver == "":
        selected_driver = ""
        selected_driver_age = ""
        selected_driver_height = ""
    else:
        driverQuery = driverInfo.copy()
        driverQuery = driverQuery[driverQuery["raceFacerID"] == selected_primary_driver].reset_index()
        selected_driver = driverQuery.at[0,'Driver']
        selected_driver_age = driverQuery.at[0,'Age']
        selected_driver_height = driverQuery.at[0,'Height']

        raceQuery = raceTimes.copy()
        raceQuery = raceQuery[raceQuery["Racer"] == selected_primary_driver].reset_index()


    #UPDATING SECONDARY DRIVER OPTIONS
    secondary_driver_filter = raceTimes[raceTimes['Racer'] != selected_primary_driver]['Racer'].unique()
    secondary_driver_options = [{'label' : racer, 'value' : racer} for racer in secondary_driver_filter]

    return (selected_driver, selected_driver_age, selected_driver_height,secondary_driver_options)


# Update graph1
@app.callback(
    Output(component_id='lapchart', component_property='figure'),
    [Input(component_id='select_race', component_property='value'),
    Input(component_id='select_primary_driver', component_property='value'),
    Input(component_id='select_secondary_driver', component_property='value')]
)

def update_graph1(race_selected, primary_driver, secondary_driver):

    LapTimesdb_primary = raceTimes.copy()
    LapTimesdb_primary = LapTimesdb_primary[LapTimesdb_primary["RaceID Name"] == race_selected]
    LapTimesdb_primary = LapTimesdb_primary[LapTimesdb_primary["Racer"] == primary_driver]

    MainDriverData = go.Scatter(
        x = LapTimesdb_primary["Lap"],
        y = LapTimesdb_primary["Lap Time Seconds"],
        mode = 'lines',
        name = 'MainDriverData'
    )


    # If secondary driver is chosen, and the primary driver is not the same as the secondary driver - create new Scatter & Title
    if secondary_driver and primary_driver != secondary_driver:

        LapTimesdb_secondary = raceTimes.copy()
        LapTimesdb_secondary = LapTimesdb_secondary[LapTimesdb_secondary["RaceID Name"] == race_selected]
        LapTimesdb_secondary = LapTimesdb_secondary[LapTimesdb_secondary["Racer"] == secondary_driver]

        SecondaryDriverData = go.Scatter(
        x = LapTimesdb_secondary["Lap"],
        y = LapTimesdb_secondary["Lap Time Seconds"],
        mode = 'lines',
        name = 'SecondaryDriverData'
    )
        #Creating Graph
        graph1 = go.Figure(data=[MainDriverData, SecondaryDriverData])
        text = f"{primary_driver} vs. {secondary_driver} lap times"


    else:
        graph1 = go.Figure(data=[MainDriverData])

    if primary_driver == None:
        text = ""
    else:
        text = f"{primary_driver} lap times"


    graph1.update_layout(
        title={
            'text': text,
            'y': 0.95,  # Move the title a bit closer to the top of the figure
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis=dict(
            range=[31,65],
            gridcolor='black',
            zerolinecolor='black'
        ),
        xaxis=dict(
            gridcolor='black',
            zerolinecolor='black'
            ),
        paper_bgcolor = '#D9D9D9',
        plot_bgcolor = '#D9D9D9',
        font_color= 'black',
        title_font_size=24,
        margin=dict(t=40, b=20,l=20,r=20),  # Decrease top margin to reduce space above the graph
        xaxis_title="Lap",
        yaxis_title="Lap Time"
    )


    return graph1


# # Update Visual2 callback
# @app.callback(
#     [Output('avgchart', 'figure'),
#     Output('fastestchart','figure'),
#     Output('distributionchart','figure')],
#     Input('select_primary_driver', 'value')
# )

# def update_visual2(primary_driver):

#     df2 = raceTimes.copy()
#     df2 = df2[df2["Racer"] == primary_driver]
#     df2 = df2.groupby('RaceID Name')['Lap Time Seconds'].mean()
#     df2 = df2.reset_index()

#     MainDriverAvg = go.Bar(
#         x = df2["RaceID Name"],
#         y = df2["Lap Time Seconds"],
#         name = 'MainDriverAvg'
#     )

#     fig = go.Figure(data = [MainDriverAvg])

#     if primary_driver == None:
#         text = ""
#     else:
#         text = f"{primary_driver}'s Avg Lap Times"

#     fig.update_layout(
#         title={
#             'text': text,
#             'y': 0.95,  # Move the title a bit closer to the top of the figure
#             'x': 0.5,
#             'xanchor': 'center',
#             'yanchor': 'top'
#         },
#         yaxis=dict(
#             range=[31,59],
#             gridcolor='black',
#             zerolinecolor='black'
#         ),
#         xaxis=dict(
#             gridcolor='black',
#             zerolinecolor='black'
#             ),
#         paper_bgcolor = '#D9D9D9',
#         plot_bgcolor = '#D9D9D9',
#         font_color= 'black',
#         title_font_size=24,
#         margin=dict(t=40, b=20,l=20,r=20),  # Decrease top margin to reduce space above the graph
#         xaxis_title="Race",
#         yaxis_title="Average Lap Time"
#     )


#     df3 = raceTimes.copy()
#     # Step 1: Group by 'RaceID Name' and find the minimum 'Lap Time Seconds'
#     min_lap_times = df3.groupby('RaceID Name')['Lap Time Seconds'].min().reset_index()


#     # Step 2: Merge with the original DataFrame to get the 'Racer' names
#     df3 = pd.merge(min_lap_times, df3, on=['RaceID Name', 'Lap Time Seconds'], how='left')
#     racer_count = df3.groupby("Racer")["Racer"].count()
#     # Convert the Series to a DataFrame and reset the index
#     df3 = racer_count.reset_index(name='Count')


#     labels = df3["Racer"].unique()
#     values = df3["Count"]

#     MostFastestLaps = go.Pie(labels = labels, values = values)
#     fig2 = go.Figure(data=[MostFastestLaps])

#     fig2.update_layout(
#         title={
#             'text': "Driver With The Most Fastest Laps",
#             'y': 0.95,  # Move the title a bit closer to the top of the figure
#             'x': 0.5,
#             'xanchor': 'center',
#             'yanchor': 'top'
#         },
#         paper_bgcolor = '#D9D9D9',
#         plot_bgcolor = '#D9D9D9',
#         font_color= 'black',
#         title_font_size=24,
#         margin=dict(t=40, b=20,l=20,r=20),  # Decrease top margin to reduce space above the graph
#     )

#     df4 = raceTimes.copy()
#     df4 = df4[df4["Racer"] == primary_driver]
#     print(df4)
#     min_lap_time = df4['Lap Time Seconds'].min()
#     max_lap_time = df4['Lap Time Seconds'].max()
#     bin_width = 0.35

#     #create histogram
#     fig3 = go.Figure(data=[go.Histogram(
#         x = df4['Lap Time Seconds'],
#         xbins=dict(
#             start= 35,
#             end= 50,
#             size=bin_width
#     ),
#     marker_color = 'blue',
#     opacity = 0.75
#     )])

#     fig3.update_layout(
#         xaxis=dict(
#             range=[35,50]
#         ),
#         title_text='Distribution of Lap Times',  # Title of the graph
#         xaxis_title_text='Lap Time Seconds',  # x-axis label
#         yaxis_title_text='Count',  # y-axis label
#         bargap=0.1,  # Gap between bars
#         paper_bgcolor = '#D9D9D9',
#         plot_bgcolor = '#D9D9D9',
#         bargroupgap=0.1,  # Gap between groups of bars
#         font_color= 'black',
#         title_font_size=24,
#         margin=dict(t=40, b=20,l=20,r=20)  # Decrease top margin to reduce space above the graph
#     )



#     return fig,fig2,fig3

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)