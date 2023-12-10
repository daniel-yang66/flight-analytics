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
        
        dcc.Input(id='dep',type='text', placeholder='Airport IATA', 
                  style = {'text-align':'center','border-radius': 10,'width':200,'margin-bottom':17,'margin-left':460})], 
            style = {'text-align':'center'}),
        
        dbc.Row(
        html.Button('View Stats', id='submit', 
                    style = {'margin-bottom':12,'width':200, 'margin-left':460,'border-radius':30,'background-color':'green','color':'white'}), style = {'text-align':'center'}),
        dbc.Row([
        dbc.Col([
            dcc.Graph(id='pie')
        ]),
        dbc.Col(dbc.Row(
            dcc.Graph(id='pie2')),
        ),
            dcc.Graph(id='bar2'),
            dcc.Graph(id='map')
        ])
            
        ])
        
    
],
    style = {'width':200, 'background-color':'green', 'margin-left':370, 'border':'white','border-radius':20,'margin-bottom':15}, 
    selected_style = {'width':200,'margin-left':370, 'background-color':'lightblue', 'border':'white solid 3px','border-radius':20,'margin-bottom':15}),
        
        dcc.Tab(label = 'Airline Stats', id='Tab 2' ,children=[
            
            dbc.Row([
        
        dcc.Input(id='airline',type='text', placeholder='Airline Name', 
                  style = {'text-align':'center','border-radius': 10,'width':200,'margin-bottom':17,'margin-left':460})], 
            style = {'text-align':'center'}),
            
            dbc.Row(
        html.Button('View Stats', id='submit2', 
                    style = {'margin-bottom':12,'width':200, 'margin-left':460,'border-radius':30,'background-color':'green','color':'white'}), style = {'text-align':'center'}),
            
            dcc.Graph(id='bar'),
            dcc.Graph(id='hist')
        ],
                style = {'width':200,'background-color':'green', 'border':'white','border-radius':20,'margin-bottom':15}, 
                selected_style = {'width':200, 'border':'white solid 3px','border-radius':20,'background-color':'lightblue','margin-bottom':15})
]),
    dbc.Row([
        dbc.Col(
    html.Footer('Copyright'), width = 1),
        dbc.Col(
        dcc.Link(children = 'Daniel Yang',
                 href = 'https://www.linkedin.com/in/daniel-yang-a17ab3229/', 
                 target = '_blank', style = {'margin-left': -15}))
    ], style = {'margin-bottom':12,'margin-top':12,'margin-left':-22})
    ])

@app.callback(Output("submit", "n_clicks"),
              Output('pie','figure'),
              Output('pie2','figure'),
              Output('bar2','figure'),
              Output('map','figure'),
              Input('dep','value'),
              Input('submit','n_clicks'))

def view_stats(dep, clicks):
    if not clicks:
        raise PreventUpdate
        

    fr_api = FlightRadar24API()
    airport = fr_api.get_airport_details(dep.upper().strip())
    
    dep_metric = pd.DataFrame(airport['airport']['pluginData']['details']['stats']['departures']['recent']['quantity'], 
                      index = [0])
    
    depart = pd.DataFrame(list(['On Time']*int(dep_metric['onTime']) 
                               + ['Delayed']*int(dep_metric['delayed'])
                              + ['Canceled']*int(dep_metric['canceled'])), columns = ['Status'])
    depart['Count'] = 1
    
    arr_metric= pd.DataFrame(airport['airport']['pluginData']['details']['stats']['arrivals']['recent']['quantity'], 
                      index = [0])
    
    arrive = pd.DataFrame(list(['On Time']*int(arr_metric['onTime']) 
                               + ['Delayed']*int(arr_metric['delayed'])
                              + ['Canceled']*int(arr_metric['canceled'])), columns = ['Status'])
    arrive['Count'] = 1
    
    
    figure = px.pie(depart.groupby('Status').count().reset_index(), 
                    values = 'Count', 
                    names = 'Status' , 
                    hole = 0.7,
                    title = 'Departure Metrics',
                   color = 'Status',
                   color_discrete_map = {
                       'On Time':'green',
                       'Delayed':'yellow',
                       'Canceled':'red'
                   })


    figure2 = px.pie(arrive.groupby('Status').count().reset_index(), 
                    values = 'Count' , 
                    names = 'Status', 
                    hole = 0.7,
                    title = 'Arrival Metrics',
                    color = 'Status',
                    color_discrete_map = {
                       'On Time':'green',
                       'Delayed':'yellow',
                       'Canceled':'red'
                   })
    
    carrier = []
    delay_status = []
    lat = []
    lon = []
    name = []
    
    total_pages = airport['airport']['pluginData']['schedule']['departures']['page']['total']
    
    for page in range(0,total_pages+1):
        
        all_ac = fr_api.get_airport_details(dep.upper().strip(), page = page)['airport']['pluginData']['schedule']['departures']['data']
        
        live_ac = filter(lambda x: x['flight']['status']['live'] == True, all_ac)

        for flight in live_ac:
            
            if flight['flight']['airline']:
                carrier.append(flight['flight']['airline']['short'])
                delay_status.append(flight['flight']['status']['icon'])
                lat.append(flight['flight']['airport']['destination']['position']['latitude'])
                lon.append(flight['flight']['airport']['destination']['position']['longitude'])
                name.append(flight['flight']['airport']['destination']['code']['iata'])
                
            else:
                carrier.append('N/A')
                delay_status.append('N/A')
                
    market = pd.DataFrame(list(zip(carrier,delay_status,lat,lon,name)),
                          columns=['Carrier','Delay Status','Lat','Lon','Code'])
    market['Count'] = 1
    
    figure3 = px.bar(market.groupby(['Carrier','Delay Status']).count().reset_index(), 
                     x='Carrier', 
                     y='Count',
                    title = f'Flights Departing/Departed {dep.upper()}',
                    color = 'Delay Status',
                    color_discrete_map = {
                        'green':'green',
                        'yellow':'yellow',
                        'red':'red',
                        'N/A':'gray'
                    })
    
    figure4 = px.scatter_mapbox(market.groupby(['Code','Lat','Lon']).count().reset_index(), 
                                lat = 'Lat',
                                lon = 'Lon',
                                color = 'Count',
                                zoom = 1, 
                                hover_name = 'Code',
                                color_continuous_scale = px.colors.sequential.Tealgrn,
                                title = f'{dep.upper()} Destinations (Live Aircraft)'
                               ).update_layout(mapbox_style="dark", 
                                            mapbox_accesstoken='pk.eyJ1IjoiZGFuaWVseWFuZzc4NyIsImEiOiJjbHB6d3E1Y2IxNnF2MmpwcHRnbnVxZm94In0.D9wJEwgIDAr-V2EN5zDTJw')
    
    
    clicks = None
    
    return clicks, figure, figure2, figure3, figure4

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
    
    carrier = filter(lambda x: x['Name'].lower() == company.lower().strip(),all_carriers)
    
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
    
    figure2 = px.histogram(ac, x='Altitude', 
                           title = 'Altitude Distribution'
                           ).update_traces(marker_color='green')
    
    return clicks, figure, figure2
    

if __name__ == '__main__':
    app.run_server(debug = False)



