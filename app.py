from FlightRadar24 import FlightRadar24API

from dash import Dash, html, dcc
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

app = Dash(__name__, 
                  external_stylesheets = [dbc.themes.DARKLY],
                  meta_tags = [{'name':'viewport','content':'width=device-width, initial-scale=1'}]
                 )
server = app.server

load_figure_template('slate')

def blank_figure():
    fig = go.Figure(go.Scatter(x=[], y = []))
    fig.update_layout(template = None, plot_bgcolor='#454545', paper_bgcolor = '#454545')
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)
    
    return fig

app.layout = dbc.Container([dbc.Container([
    dbc.Row(
    html.H2(id='title', children="AeroStat", 
            style = {'font-weight':'bold','font-size':40, 'font-family':'sans-serif'}),
        style = {
                 'font-weight':'bold',
                 'font-size':40,
                 'font-family':'sans-serif'}),
    
        dbc.Row(html.P("Live Airport/Airline Metrics",
                         ),style = {'font-size':16}),
    
    dcc.Tabs(id='tabs', children = [
        dcc.Tab(label = 'Airport Stats',id='Tab 1', children = [
            dbc.Row([
        dbc.Row([
        
        dcc.Input(id='dep',type='text', placeholder='Airport IATA (ex. SFO)', 
                  style = {'text-align':'center',
                           'border-radius': 10,
                           'width':200})], 
            style = {'text-align':'center',
                    'justify-content':'center'}),
        
            dcc.RadioItems(id='metric',options = [
                {'label':'Departure Metrics','value':'departures'},
                {'label':'Arrival Metrics','value':'arrivals'}
                
            ], 
                           value = 'departures',
                           style = {
                                    'font-size':15,
                                    'font-family':'sans-serif',
                                    'display':'flex',
                                    'gap':12,
                             'width':300,
                             'color':'white'}),
        
        dbc.Row(
        html.Button('View Stats', id='submit', 
                    style = {
                             'width':200,
                             'border-radius':30,
                             'background-color':'green',
                             'color':'white'}), style = {'text-align':'center',
                                                        'justify-content':'center'}),
        dbc.Row([
        dbc.Col([
            dcc.Graph(id='pie', figure = blank_figure())
        ], width = 4),
        dbc.Col(dbc.Row(dcc.Graph(id='map', figure = blank_figure())
            ),
        width = 8),
            dcc.Graph(id='bar2', figure = blank_figure()),
        ])
            
        ], style = {'display':'grid','justify-items':'center','row-gap':12})      
    
],
    style = {'width':200,
             'margin-bottom':12,
             'height':40,
             'display':'flex',
             'align-items':'center',
             'justify-content':'center',
             'background-color':'green', 
             'border':'white',
             'border-radius':20}, 
    selected_style = {'width':200,
                      'margin-bottom':12,
                      'height':40,
                      'display':'flex',
                      'align-items':'center',
                      'justify-content':'center',
                      'background-color':'lightblue', 
                      'border':'white solid 3px',
                      'border-radius':20}),
        
        dcc.Tab(label = 'Airline Stats', id='Tab 2' ,children=[
            
            dbc.Row([
            
            dbc.Row([
        
        dcc.Input(id='airline',type='text', placeholder='Airline Full Name', 
                  style = {'text-align':'center',
                           'border-radius': 10,
                           'width':200})], 
            style = {'text-align':'center',
                     'justify-content':'center'}),
            
            dbc.Row(
        html.Button('View Stats', 
                    id='submit2', 
                    style = {
                             'width':200,
                             'border-radius':30,
                             'background-color':'green',
                             'color':'white'}), style = {'text-align':'center',
                                                        'justify-content':'center'}),
            dbc.Row([
            dcc.Graph(id='bar', figure = blank_figure()),
            dcc.Graph(id='hist', figure = blank_figure())])], style = {
                'display':'grid',
                'row-gap':12,
                'justify-items':'center'
            })
        ],
                style = {'width':200,
                         'margin-bottom':12,
                         'height':40,
                         'display':'flex',
                         'align-items':'center',
                         'justify-content':'center',
                         'background-color':'green', 
                         'border':'white','border-radius':20}, 
                selected_style = {'width':200,
                                  'margin-bottom':12,
                                  'height':40,
                                  'display':'flex',
                                  'align-items':'center',
                                  'justify-content':'center',
                                  'border':'white solid 3px',
                                  'border-radius':20,
                                  'background-color':'lightblue'})
], style = {'justify-content':'center'}),
    ], style = {'display':'grid',
                'justify-items':'center'}),
html.Div([
        
    html.Footer('Copyright'),     
        dcc.Link(children = 'Daniel Yang',
                 href = 'https://www.linkedin.com/in/daniel-yang-a17ab3229/', 
                 target = '_blank')
    ], style = {'display':'flex','gap':10,
                'margin-bottom':12,
                'margin-top':12,
               'align-self':'flex-start'})])

@app.callback(Output("submit", "n_clicks"),
              Output('pie','figure'),
              Output('bar2','figure'),
              Output('map','figure'),
              Input('dep','value'),
              Input('metric','value'),
              Input('submit','n_clicks'))

def view_stats(dep, metric, clicks):
    if not clicks:
        raise PreventUpdate
        
    fr_api = FlightRadar24API()
    airport = fr_api.get_airport_details(dep.upper().strip())
    
    if airport['airport']['pluginData']['details']['stats']:
    
        metrics = pd.DataFrame(airport['airport']['pluginData']['details']['stats'][metric]['recent']['quantity'], 
                          index = [0])
    
        flights = pd.DataFrame(list(['On Time']*int(metrics['onTime']) 
                                   + ['Delayed']*int(metrics['delayed'])
                                  + ['Canceled']*int(metrics['canceled'])), columns = ['Status'])
        flights['Count'] = 1
    else:
        flights = pd.DataFrame(list(['N/A']),columns = ['Status'])
        flights['Count'] = '0'
    
    airport_type = 'destination'
    heading = f'Where Flights are Headed'
    if metric == 'arrivals':
        airport_type = 'origin'
        heading = 'Where Flights are Arriving From'
    
    
    figure = px.pie(flights.groupby('Status').count().reset_index(), 
                    values = 'Count', 
                    names = 'Status' , 
                    hole = 0.7,
                    title = f'Recent {metric.title()[0:-1]} Metrics',
                    color = 'Status',
                    color_discrete_map = {
                       'On Time':'green',
                       'Delayed':'yellow',
                       'Canceled':'red',
                        'N/A':'gray'
                   })
    
    carrier = []
    delay_status = []
    lat = []
    lon = []
    name = []
    
    total_pages = airport['airport']['pluginData']['schedule'][metric]['page']['total']
    
    for page in range(0,total_pages+1):
        
        all_ac = fr_api.get_airport_details(dep.upper().strip(), 
                                            page = page)['airport']['pluginData']['schedule'][metric]['data']
        
        live_ac = filter(lambda x: x['flight']['status']['live'] == True, all_ac)

        for flight in live_ac:
            
            if flight['flight']['airline']:
                carrier.append(flight['flight']['airline']['short'])
                delay_status.append(flight['flight']['status']['icon'])
                lat.append(flight['flight']['airport'][airport_type]['position']['latitude'])
                lon.append(flight['flight']['airport'][airport_type]['position']['longitude'])
                name.append(flight['flight']['airport'][airport_type]['code']['iata'])
                
            else:
                carrier.append('N/A')
                delay_status.append('N/A')
                
    market = pd.DataFrame(list(zip(carrier,delay_status,lat,lon,name)),
                          columns=['Carrier','Delay Status','Lat','Lon','Code'])
    market['Count'] = 1
    
    figure2 = px.bar(market.groupby(['Carrier','Delay Status']).count().reset_index().sort_values(by = 'Carrier',ascending=True), 
                     x='Carrier', 
                     y='Count',
                    title = f'{dep.upper()} {metric.title()}',
                    color = 'Delay Status',
                    color_discrete_map = {
                        'green':'green',
                        'yellow':'yellow',
                        'red':'red',
                        'N/A':'gray'
                    })
    
    figure3 = px.scatter_geo(market.groupby(['Code','Lat','Lon']).count().reset_index(), 
                                lat = 'Lat',
                                lon = 'Lon',
                                color = 'Count',
                                hover_name = 'Code',
                                color_continuous_scale = px.colors.sequential.Tealgrn,
                                title = heading
                               ).update_layout(mapbox_style="dark", 
                                            mapbox_accesstoken='pk.eyJ1IjoiZGFuaWVseWFuZzc4NyIsImEiOiJjbHB6d3E1Y2IxNnF2MmpwcHRnbnVxZm94In0.D9wJEwgIDAr-V2EN5zDTJw')
    
    
    clicks = None
    
    return clicks, figure, figure2, figure3

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
                        title='Live Aircraft').update_traces(marker_color='green')
    
    figure2 = px.histogram(ac, x='Altitude', 
                           title = 'Altitude Distribution'
                           ).update_traces(marker_color='green')

    clicks = None
    
    return clicks, figure, figure2
    

if __name__ == '__main__':
    app.run_server(debug = False)



