from FlightRadar24 import FlightRadar24API

from dash import Dash, html, dcc
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

import pandas as pd
import plotly.express as px
from datetime import datetime

app = Dash(__name__, external_stylesheets = [dbc.themes.DARKLY])
server = app.server

load_figure_template('slate')

app.layout = dbc.Container([
    html.H2(id='title', children="AeroStat", 
            style = {'margin-left':460,'font-weight':'bold','font-size':40, 'font-family':'sans-serif'}),
    
        dbc.Row(dcc.Link('Powered by aviationstack',href = 'https://aviationstack.com/',
                         style = {'font-size':16,'margin-bottom':12, 'margin-left':460})),
    
    dbc.Row([
        dbc.Row([
        
        html.H3('Enter Airport IATA:', 
                style={'margin-left':-3,'margin-bottom':15, 'font-size':25, 'font-family':'sans-serif','font-weight':'bold'}),
            
        dcc.Input(id='dep',type='text', placeholder='Departure Airport', 
                  style = {'text-align':'center','border-radius': 10,'width':200,'margin-bottom':17,'margin-left':460})], 
            style = {'text-align':'center'}),
        
        dbc.Row(
        html.Button('View Stats', id='submit', 
                    style = {'margin-bottom':10,'width':300, 'margin-left':420,'border-radius':30,'background-color':'green','color':'white'}), style = {'text-align':'center'}),
        dbc.Row([
        dbc.Col([
            dcc.Graph(id='pie')
        ]),
        dbc.Col(dbc.Row(
            dcc.Graph(id='pie2')),
        )])
        
    
])
])

@app.callback(Output("submit", "n_clicks"),
              Output('pie','figure'),
              Output('pie2','figure'), 
              Input('dep','value'), 
              Input('submit','n_clicks'))

def view_stats(dep, clicks):
    if not clicks:
        raise PreventUpdate

    fr_api = FlightRadar24API()
    airport = fr_api.get_airport_details(dep.upper())
    
    dep = pd.DataFrame(airport['airport']['pluginData']['details']['stats']['departures']['today']['quantity'], 
                      index = [0])
    arr = pd.DataFrame(airport['airport']['pluginData']['details']['stats']['arrivals']['today']['quantity'], 
                      index = [0])
    figure = px.pie(dep, 
                    values=sorted([int(dep['onTime']), int(dep['delayed']), int(dep['canceled'])]), 
                    names= ['On Time','Delayed','Canceled'], 
                    hole = 0.7,
                   title = 'Departure Performance')


    figure2 = px.pie(arr, 
                    values=sorted([int(arr['onTime']), int(arr['delayed']), int(arr['canceled'])]), 
                    names= ['On Time','Delayed','Canceled'], 
                    hole = 0.7,
                    title = 'Arrival Performance')
    clicks = None
    return clicks, figure, figure2
    

if __name__ == '__main__':
    app.run_server(debug=False)