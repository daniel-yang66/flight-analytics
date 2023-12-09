from FlightRadar24 import FlightRadar24API

from dash import Dash, html, dcc
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

import pandas as pd
import plotly.express as px

app = Dash(__name__, external_stylesheets = [dbc.themes.DARKLY])
server = app.server

load_figure_template('slate')

app.layout = dbc.Container([
    html.H2(id='title', children="AeroStat", 
            style = {'margin-left':460,'font-weight':'bold','font-size':40, 'font-family':'sans-serif'}),
    
        dbc.Row(html.P("Live Airport/Airline Metrics",
                         style = {'font-size':16,'margin-bottom':12, 'margin-left':450})),
    dcc.Tabs(id='tabs', children = [
        dcc.Tab(label = 'Airport Stats',id='Tab 1', children = [
            dbc.Row([
        dbc.Row([
        
        html.H3('Enter Airport:', 
                style={'margin-left':-3,'margin-bottom':15, 'font-size':25, 'font-family':'sans-serif','font-weight':'bold'}),
            
        dcc.Input(id='dep',type='text', placeholder='Airport IATA', 
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
        
    
],
    style = {'width':200, 'background-color':'green', 'margin-left':370, 'border':'white','border-radius':20,'margin-bottom':15}, 
    selected_style = {'width':200,'margin-left':370, 'background-color':'red', 'border':'white solid 3px','border-radius':20,'margin-bottom':15}),
        
        dcc.Tab(label = 'Airline Stats', id='Tab 2' ,children=[
            
            dbc.Row([
        
        html.H3('Enter Airline:', 
                style={'margin-left':-3,'margin-bottom':15, 'font-size':25, 'font-family':'sans-serif','font-weight':'bold'}),
            
        dcc.Input(id='airline',type='text', placeholder='Airline Name', 
                  style = {'text-align':'center','border-radius': 10,'width':200,'margin-bottom':17,'margin-left':460})], 
            style = {'text-align':'center'}),
            
            dbc.Row(
        html.Button('View Stats', id='submit2', 
                    style = {'margin-bottom':10,'width':300, 'margin-left':420,'border-radius':30,'background-color':'green','color':'white'}), style = {'text-align':'center'}),
            
            dcc.Graph(id='bar'),
            dcc.Graph(id='hist')
        ],
                style = {'width':200,'background-color':'green', 'border':'white','border-radius':20,'margin-bottom':15}, 
                selected_style = {'width':200, 'border':'white solid 3px','border-radius':20,'background-color':'red','margin-bottom':15})
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
    
    dep = pd.DataFrame(airport['airport']['pluginData']['details']['stats']['departures']['recent']['quantity'], 
                      index = [0])
    arr = pd.DataFrame(airport['airport']['pluginData']['details']['stats']['arrivals']['recent']['quantity'], 
                      index = [0])
    figure = px.pie(dep, 
                    values=[int(dep['onTime']), int(dep['delayed']), int(dep['canceled'])], 
                    names= ['On Time','Delayed','Canceled'], 
                    hole = 0.7,
                    title = 'Departure Performance')


    figure2 = px.pie(arr, 
                    values=[int(arr['onTime']), int(arr['delayed']), int(arr['canceled'])], 
                    names= ['On Time','Delayed','Canceled'], 
                    hole = 0.7,
                    title = 'Arrival Performance')
    
    
    clicks = None
    
    return clicks, figure, figure2

@app.callback(Output("submit2", "n_clicks"),
              Output('bar','figure'),
              Output('hist','figure'),
              Input('airline','value'),
              Input('submit2','n_clicks'))

def view_stats2(company, clicks):
    
    if not clicks:
        raise PreventUpdate
        
    fr_api = FlightRadar24API()
    all_carriers = fr_api.get_airlines()
    lst = []
    words = company.split(' ')
    for w in words:
        new_word = w.title()
        lst.append(new_word)
    final_name = ' '.join(lst)
    carrier = filter(lambda x: x['Name'] == final_name,all_carriers)
    
    all_flights = fr_api.get_flights(airline = list(carrier)[0]['ICAO'])
    
    aircraft = []
    alt = []
    for a in all_flights:
        aircraft.append(str(a)[2:6])
        alt.append(int(str(a)[str(a).index('Altitude') + 10 : str(a).index('Ground Speed') - 3 ]))
    ac = pd.DataFrame(list(zip(aircraft,alt)),columns=['Aircraft','Altitude'])
    ac['Count'] = 1
    
    figure = px.bar(ac.groupby('Aircraft').count().reset_index().sort_values(by='Count',ascending=False), 
                        x='Aircraft',
                        y='Count', 
                        title='Active Aircraft').update_traces(marker_color='green')
    figure2 = px.histogram(ac, x='Altitude', title = 'Altitude Distribution').update_traces(marker_color='green')
    return clicks, figure, figure2
    

if __name__ == '__main__':
    app.run_server(debug=False)



