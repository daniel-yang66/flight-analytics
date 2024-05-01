from FlightRadar24 import FlightRadar24API

from datetime import datetime
import pytz
from time import time
from dash import Dash, html, dcc
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

import pandas as pd
import plotly.express as px

app = Dash(__name__, 
                  external_stylesheets = [dbc.themes.DARKLY],
                  meta_tags = [{'name':'viewport','content':'width=device-width, initial-scale=1'}]
                 )
server = app.server

load_figure_template('slate')

city_code = pd.read_csv('city_code.txt', delimiter = ':').dropna(subset = ['iata'])

fr_api = FlightRadar24API()

all_carr = fr_api.get_airlines()
all_airp = fr_api.get_airports()

icaos = []

for carr in all_carr:
    pair = {'label':carr['Name'], 'value': carr['ICAO']}
    icaos.append(pair)
options = []
for airp in all_airp:
    airp_str = str(airp)
    pair2 = {'label': airp_str[8:airp_str.index('-') - 1],'value':airp_str[2:6]}
    options.append(pair2)
   


app.layout = dbc.Container([
    dcc.Interval(id = 'refresh', interval = 600*1000),
    dbc.Col(
    html.Div(id='wx', children = [
        html.Div([
        html.H4(id='airport', style = {'font-weight':'bold',
                                     'font-family':'sans-serif',
                                    'font-size':20}),
        html.P(id='condition'),
        html.P(id='time')
    ], style = {'text-align':'center', 'padding':5}),
    ], style = {'display':'flex',
               'justify-content':'center',
               'align-items':'center'}), width = 4),
                            dbc.Container([
    dbc.Row(
    html.H2(id='title', children="AeroStat", 
            style = {'font-weight':'bold','font-size':45, 'font-family':'sans-serif'}),
        style = {
                 'font-weight':'bold',
                 'font-family':'sans-serif'}),
                                
    
    dcc.Tabs(id='tabs', children = [
        dcc.Tab(label = 'Scheduled Flights',id='Tab 1', children = [
            dbc.Row([
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
        dbc.Row([
        dcc.Dropdown(id='airp',
                     placeholder = 'Search Airport',
                     options = options,
                     style = {'text-align':'center',
                           'border-radius': 10,
                           'width':400,
                          'color':'black'})], 
            style = {'text-align':'center',
                    'justify-content':'center'}),
                
                dbc.Row([
                dcc.Slider(1,24,
                           step = None,
                           id='hours',
                           marks = {
                               1: {'label':'Next 1H','style':{'font-weight':'bold','color':'white'}},
                               5: {'label':'Next 5H','style':{'font-weight':'bold','color':'white'}},
                               10: {'label':'Next 10H','style':{'font-weight':'bold','color':'white'}},
                               15: {'label':'Next 15H','style':{'font-weight':'bold','color':'white'}},
                               20: {'label':'Next 20H','style':{'font-weight':'bold','color':'white'}},
                               24: {'label':'Next 24H','style':{'font-weight':'bold','color':'white'}}  
                           },
                           value = 5
                           
                     )],
                style = {'width':900}
            ),
    
        dcc.Loading(dbc.Row([
        dbc.Col([
            html.Div(id='pie', style = {'text-align':'center',
                                                        'justify-content':'center'})
        ], width = 4),
        dbc.Col(dbc.Row(html.Div(id='map', style = {'text-align':'center',
                                                        'justify-content':'center'})
            ),
        width = 8),
            html.Div(id='bar2', style = {'text-align':'center',
                                                        'justify-content':'center'})])
                                                                , type = 'graph', 
                                                                        fullscreen = True,
                                                                   style = {'background-color':'black'})
                                                                                        
        ], style = {'display':'grid','justify-items':'center','row-gap':12})
                  
    
],
    style = {'width':200,
             'margin-bottom':12,
             'height':40,
             'display':'flex',
             'align-items':'center',
             'justify-content':'center',
             'background-color':'lightblue',
             'color':'black',
             'border-radius':20}, 
    selected_style = {'width':200,
                      'margin-bottom':12,
                      'height':40,
                      'display':'flex',
                      'align-items':'center',
                      'justify-content':'center',
                      'background-color':'green', 
                      'border':'white solid 3px',
                      'color':'white',
                      'border-radius':20}),
        
        dcc.Tab(label = 'Airline Stats', id='Tab 2' ,children=[
            
            dbc.Row([
            
            dbc.Row([
        
        dcc.Dropdown(id='airline', 
                  options = icaos,
                  placeholder='Search Airline', 
                  style = {'text-align':'center',
                           'color':'black',
                           'border-radius': 10,
                           'width':350})], 
            style = {'text-align':'center',
                     'justify-content':'center'}),
                
            dcc.Loading(dbc.Row([
            html.Div(id='bar', style = {'text-align':'center',
                                                        'justify-content':'center'}),
            html.Div(id='hist', style = {'text-align':'center',
                                                        'justify-content':'center'})]), type = 'graph',
                        fullscreen = True, style = {'background-color':'black'})], style = {
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
                         'background-color':'lightblue', 
                         'color':'black',
                         'border-radius':20}, 
                selected_style = {'width':200,
                                  'margin-bottom':12,
                                  'height':40,
                                  'display':'flex',
                                  'align-items':'center',
                                  'justify-content':'center',
                                  'border':'white solid 3px',
                                  'border-radius':20,
                                  'color':'white',
                                  'background-color':'green'})
        
], style = {'justify-content':'center'}),
    ], style = {'display':'grid',
                'justify-items':'center'}),
html.Div([
        
    html.Footer('Copyright'),     
        dcc.Link(children = 'Daniel Yang',
                 href = 'https://www.linkedin.com/in/daniel-yang-a17ab3229/', 
                 target = '_blank')
    ], style = {'display':'flex',
                'gap':10,
               'align-self':'flex-start',
               'position':'absolute',
               'top':10,
               'right':10})])


@app.callback(
              Output('time','children'),
              Output('pie','children'),
              Output('bar2','children'),
              Output('map','children'),
              Output('airport','children'),
              Output('condition','children'),
              Input('airp','value'),
              State('hours','value'),
              State('metric','value'),
             Input('refresh','n_intervals'))

def view_stats(dep,hours, metric,n):
    
    try:
        
        airport = fr_api.get_airport_details(dep.upper().strip())

        if airport['airport']['pluginData']['details']['stats']:

            metrics = pd.DataFrame(airport['airport']['pluginData']['details']['stats'][metric]['recent']['quantity'], 
                              index = [0])

            flights = pd.DataFrame(list(['On Time']*int(metrics['onTime']) 
                                       + ['Delayed']*int(metrics['delayed'])
                                      + ['Canceled']*int(metrics['canceled'])), columns = ['Status'])
            if len(flights) == 0:
                flights = pd.DataFrame(list(['No Data']), columns = ['Status'])
                
            flights['Count'] = 1
            
        else:
            flights = pd.DataFrame(list(['N/A']),columns = ['Status'])
            flights['Count'] = '0'

        airport_type = 'destination'
        heading = f'Scheduled Destinations (Next {hours}H)'        

        if metric == 'arrivals':
            airport_type = 'origin'
            heading = f'Scheduled Arrivals (Next {hours}H)'
            

        temp_data = airport['airport']['pluginData']['weather']['temp']['celsius']
        cond_data = airport['airport']['pluginData']['weather']['sky']['condition']['text']
        wind_dir_data = airport['airport']['pluginData']['weather']['wind']['direction']['text']
        wind_dir_data2 = airport['airport']['pluginData']['weather']['wind']['direction']['degree']
        wind_vel_data = airport['airport']['pluginData']['weather']['wind']['speed']['kts']

        if temp_data:
            temp = temp_data     
        else:
            temp = 'N/A'

        if cond_data:
            sky = cond_data
        else:
            sky = 'N/A'

        if wind_dir_data == 'Variable':
            wind_dir = wind_dir_data
        elif wind_dir_data2:
            wind_dir = wind_dir_data2
        else:
            wind_dir = 'N/A'

        if wind_vel_data:
            wind_speed = wind_vel_data

        else:
            wind_speed = 'N/A'

        wind_info = f'Wind: {wind_dir}\u00B0 - {wind_speed} kt'

        if wind_vel_data == 0:
            wind_info = 'Wind: Calm'

        weather_heading = f'{dep.upper()} Info'
        weather_info = f'{sky} | {temp}\u00B0C | {wind_info}'

        figure = dcc.Graph(figure = px.pie(flights.groupby('Status').count().reset_index(), 
                        values = 'Count', 
                        names = 'Status' , 
                        hole = 0.7,
                        title = f"{dep.upper()} Recent {metric.title()[0:-1]} Metrics",
                        color = 'Status',
                        color_discrete_map = {
                           'On Time':'green',
                           'Delayed':'yellow',
                           'Canceled':'red',
                            'N/A':'gray',
                            'No Data':'gray'
                       }))
        

        carrier = []
        lat = []
        lon = []
        name = []
        

        total_pages = airport['airport']['pluginData']['schedule'][metric]['page']['total']

        for page in range(0,total_pages+1):
            scheduled_ac = []

            all_ac = fr_api.get_airport_details(dep.upper().strip(), 
                                                page = page)['airport']['pluginData']['schedule'][metric]['data']

            for ac in all_ac:
                if ac['flight']['airline'] and ac['flight']['time'] and ac['flight']['airport']:
                    if ac['flight']['time']['scheduled']['departure'] - int(time())>0 and ac['flight']['time']['scheduled']['departure'] - int(time())<=hours*3600:
                        scheduled_ac.append(ac)   
            
            for flight in scheduled_ac:
                carrier.append(flight['flight']['airline']['name'])
                lat.append(flight['flight']['airport'][airport_type]['position']['latitude'])
                lon.append(flight['flight']['airport'][airport_type]['position']['longitude'])
                name.append(flight['flight']['airport'][airport_type]['code']['iata'])


        market = pd.DataFrame(list(zip(carrier,lat,lon,name)),
                              columns=['Airline','Lat','Lon','Airport'])
                
        market['Count'] = 1
        top_10_lst = []
        top_10 = dict(market['Airport'].value_counts().head(10))
        for k,v in top_10.items():
            top_10_lst.append(k)

        figure2 = dcc.Graph(figure = px.bar(market[market['Airport'].isin(top_10_lst)].groupby(['Airport','Airline']).sum().reset_index(),                       
                         x='Airport', 
                         y='Count',
                        color = 'Airline',
                        title = f'Top 10 Airports (Next {hours}H)',
                        color_discrete_sequence = px.colors.qualitative.T10).update_xaxes(tickangle = -50))


        figure3 = dcc.Graph(figure = px.scatter_geo(market.groupby(['Airport','Lat','Lon']).count().reset_index(), 
                                    lat = 'Lat',
                                    lon = 'Lon',
                                    color = 'Count',
                                    hover_name = 'Airport',
                                    color_continuous_scale = px.colors.sequential.Sunset,
                                    title = heading
                                   ).update_coloraxes(showscale=False).update_layout(mapbox_style = 'dark',
                                                                                    mapbox_accesstoken = 'pk.eyJ1IjoiZGFuaWVseWFuZzc4NyIsImEiOiJjbHB6d3E1Y2IxNnF2MmpwcHRnbnVxZm94In0.D9wJEwgIDAr-V2EN5zDTJw'))

        tz = airport['airport']['pluginData']['details']['timezone']['name']
        tz_abb = airport['airport']['pluginData']['details']['timezone']['abbr']
        aero_tz = pytz.timezone(tz) 
        aerodrome_time = datetime.now(aero_tz)
        local_time = f'Time: {aerodrome_time.strftime("%H:%M")} {tz_abb}'
        
        
        if len(market) == 0:
            figure = ''
            figure2 = 'No Data Available'
            figure3 = ''
        
    except:
        local_time = ''
        figure = ''
        if dep == None:
            figure2 = ''
        else:
            figure2 = 'Airport Data Currently Unavailable'
        figure3 = ''
        weather_heading = ''
        weather_info = ''
    

    return local_time, figure, figure2, figure3, weather_heading, weather_info
    
    
@app.callback(
              Output('bar','children'),
              Output('hist','children'),
              Input('airline','value'),
             Input('refresh','n_intervals'))

def view_stats2(company, n):
        
    try:

        all_flights = fr_api.get_flights(airline = company.upper())

        if len(all_flights)>0:

            aircraft = []
            alt = []
            speed = []
            status = []
            for a in all_flights:
                aircraft.append(str(a)[2:6])
                alt.append(int(str(a)[str(a).index('Altitude') + 10 : str(a).index('Ground Speed') - 3 ]))
                speed.append(int(str(a)[str(a).index('Ground Speed') + 14 : str(a).index('Heading') - 3 ]))
            for a,s in zip(alt,speed):
                if a == 0 and s == 0:
                    status.append('Parked')
                elif a == 0 and s > 0:
                    status.append('Taxi/Takeoff')
                elif a > 0:
                    status.append('Airborne')
                else:
                    status.append('N/A')

            ac = pd.DataFrame(list(zip(aircraft,alt,speed)),columns=['Aircraft','Altitude','Ground Speed'])
            ac['Count'] = 1
            ac['Status'] = status

            figure = dcc.Graph(figure = px.bar(ac.groupby(['Aircraft','Status']).count().reset_index()
                                            .sort_values(by='Count',ascending=False), 
                            x='Aircraft',
                            y='Count',
                            color = 'Status',

                            color_discrete_sequence = px.colors.qualitative.T10,
                            title='Live Aircraft'))

            figure2 = dcc.Graph(figure = px.histogram(ac, x='Altitude', 
                               title = 'Altitude Distribution'
                               ).update_traces(marker_color='green'))

        else:
            figure = 'No Aircraft Data Available'
            figure2 = ''
    except:
        if company == None:
            figure = ''
        else:
            figure = 'No Aircraft Data Available'
        figure2 = ''
        
    
    return figure, figure2
    
    

if __name__ == '__main__':
    app.run_server(debug=False)



