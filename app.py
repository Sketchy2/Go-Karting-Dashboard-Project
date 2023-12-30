import pandas as pd
import numpy as np
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
        className='Header2',
        children=[
            html.Div(
                className='selection-container',
                children=[
                    html.Span("Select Driver:", className='selection'),
                    dcc.Dropdown(
                        id="select_primary_driver",
                        className="driver-dropdown",
                        options=driver_dropdown_options,
                        multi=False,
                        value="",
                        style={'width': '100%', 'minWidth': '200px'}
                    )
                ]
            )
        ]
    ),


    dcc.Dropdown(id="select_race",
                options=race_dropdown_options,
                multi=False,
                value="",
                style={'width': "40%"}
                ),
    
    #Dropdown for secondary driver
    dcc.Dropdown(id="select_secondary_driver",
                options=[],
                multi=False,
                value = "",
                style={'width':"40%"}
                ),


    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(id='lapchart', figure={},className='Chart1'), className="visual-box"), width=6, lg=6, md=12, sm=12, xs=12),
        dbc.Col(html.Div(dcc.Graph(id='avgchart', figure={}, className='Chart2'), className="visual-box"), width=6, lg=6, md=12, sm=12, xs=12),
        dbc.Col(html.Div(dcc.Graph(id='fastestchart', figure={}, className="Chart3"), className="visual-box"), width=6, lg=6, md=12, sm=12, xs=12),
        dbc.Col(html.Div(dcc.Graph(id='distributionchart', figure={}, className="Chart4"),className='visual-box'), width=6, lg=6, md=12, sm=12, xs=12)
    ], className="mb-4"),
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


# Update Visual1 callback
@app.callback(
    Output('lapchart', 'figure'),
    [Input('select_race', 'value'),
    Input('select_primary_driver', 'value'),
    Input('select_secondary_driver', 'value')]
)

def update_visual1(race_selected, primary_driver, secondary_driver):

    df2 = df.copy()
    df2 = df2[df2["RaceID"] == race_selected]
    df2 = df2[df2["Racer"] == primary_driver]

    MainDriverData = go.Scatter(
        x = df2["Lap"],
        y = df2["Lap Time Seconds"],
        mode = 'lines',
        name = 'MainDriverData'
    )


    # If secondary driver is chosen, and the primary driver is not the same as the secondary driver - create new Scatter & Title
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
        text = f"{primary_driver} vs. {secondary_driver} lap times"


    else:
        fig = go.Figure(data=[MainDriverData])

    if primary_driver == None:
        text = ""
    else:
        text = f"{primary_driver} lap times"


    fig.update_layout(
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


    return fig


# Update Visual2 callback
@app.callback(
    [Output('avgchart', 'figure'),
    Output('fastestchart','figure'),
    Output('distributionchart','figure')],
    Input('select_primary_driver', 'value')
)

def update_visual2(primary_driver):

    df2 = df.copy()
    df2 = df2[df2["Racer"] == primary_driver]
    df2 = df2.groupby('RaceID')['Lap Time Seconds'].mean()
    df2 = df2.reset_index()

    MainDriverAvg = go.Bar(
        x = df2["RaceID"],
        y = df2["Lap Time Seconds"],
        name = 'MainDriverAvg'
    )

    fig = go.Figure(data = [MainDriverAvg])

    if primary_driver == None:
        text = ""
    else:
        text = f"{primary_driver}'s Avg Lap Times"

    fig.update_layout(
        title={
            'text': text,
            'y': 0.95,  # Move the title a bit closer to the top of the figure
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis=dict(
            range=[31,59],
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
        xaxis_title="Race",
        yaxis_title="Average Lap Time"
    )


    df3 = df.copy()
    # Step 1: Group by 'RaceID' and find the minimum 'Lap Time Seconds'
    min_lap_times = df3.groupby('RaceID')['Lap Time Seconds'].min().reset_index()


    # Step 2: Merge with the original DataFrame to get the 'Racer' names
    df3 = pd.merge(min_lap_times, df3, on=['RaceID', 'Lap Time Seconds'], how='left')
    racer_count = df3.groupby("Racer")["Racer"].count()
    # Convert the Series to a DataFrame and reset the index
    df3 = racer_count.reset_index(name='Count')


    labels = df3["Racer"].unique()
    values = df3["Count"]

    MostFastestLaps = go.Pie(labels = labels, values = values)
    fig2 = go.Figure(data=[MostFastestLaps])

    fig2.update_layout(
        title={
            'text': "Driver With The Most Fastest Laps",
            'y': 0.95,  # Move the title a bit closer to the top of the figure
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        paper_bgcolor = '#D9D9D9',
        plot_bgcolor = '#D9D9D9',
        font_color= 'black',
        title_font_size=24,
        margin=dict(t=40, b=20,l=20,r=20),  # Decrease top margin to reduce space above the graph
    )

    df4 = df.copy()
    df4 = df4[df4["Racer"] == primary_driver]
    print(df4)
    min_lap_time = df4['Lap Time Seconds'].min()
    max_lap_time = df4['Lap Time Seconds'].max()
    bin_width = 0.35

    #create histogram
    fig3 = go.Figure(data=[go.Histogram(
        x = df4['Lap Time Seconds'],
        xbins=dict(
            start= 35,
            end= 50,
            size=bin_width
    ),
    marker_color = 'blue',
    opacity = 0.75
    )])

    fig3.update_layout(
        xaxis=dict(
            range=[35,50]
        ),
        title_text='Distribution of Lap Times',  # Title of the graph
        xaxis_title_text='Lap Time Seconds',  # x-axis label
        yaxis_title_text='Count',  # y-axis label
        bargap=0.1,  # Gap between bars
        paper_bgcolor = '#D9D9D9',
        plot_bgcolor = '#D9D9D9',
        bargroupgap=0.1,  # Gap between groups of bars
        font_color= 'black',
        title_font_size=24,
        margin=dict(t=40, b=20,l=20,r=20)  # Decrease top margin to reduce space above the graph
    )



    return fig,fig2,fig3

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)