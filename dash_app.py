# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 16:49:11 2018
@author: jingwenken

Modified by tjwied on Feb 1 2019 
"""

import pandas as pd
import dash
import pickle
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import networkx as nx
import modify_graph
import build_graph
import graph_nlp
import glob
import os

csv_list = glob.glob("/home/rubisco/Desktop/insight/dash/final/csv/*.csv")
cwd = os.getcwd()

G_list = []
edge_trace_list = []
node_trace_list = []
topic_list = []
node_lengths = []
edge_lengths = []
coin_list = []
for element in csv_list:
    basename_extract = os.path.basename(element[:-4])
    coin_list.append(basename_extract)
    #build_graph.build_graph(element)
    nlp = graph_nlp.topic_modeling(element)
    betweenness = pickle.load( open( basename_extract+"_between.pkl", "rb" ))
    ranking = sorted(betweenness, key=betweenness.get, reverse=True)
    #build_graph.build_graph(element)
    graph_components = modify_graph.plot_graph(cwd+'/'+basename_extract+'.grid')
    G_list.append(graph_components[0])
    edge_trace_list.append(graph_components[1])
    node_trace_list.append(graph_components[2])
    node_lengths.append(graph_components[4])
    edge_lengths.append(graph_components[3])
    topic_list.append(nlp)

i = 0
marker = {}
for element in coin_list:
    marker[i] = element
    i += 1

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        id='year-slider',
        min=0,
        max=len(csv_list),
        value=0,
        marks=marker
#add to layout here that there should be tex
    ),
        html.Div(className='row', children=[
            html.Div([html.H2('Overall Data'),
                                html.Div(id='data-summary'),
                        ], className='three columns'),
                    html.Div([
                        html.H2('Top Accounts'),
                                html.Div(id='selected-data'),
                        ], className='three columns'),
                    html.Div([
                        html.H2('Topics'),
                                html.Div(id='selecteder-data'),
                        ], className='three columns'),
                    html.Div([html.H2('Selected Data'),
                                html.Div(id='selected-accounts'),
                        ], className='three columns')
                ])
            ])

@app.callback(
    dash.dependencies.Output('graph-with-slider', 'figure'),
    [dash.dependencies.Input('year-slider', 'value')])
def update_graph1(selected_year):
    #filtered_df = df[df.year == selected_year]
    fig    = go.Figure(data=[edge_trace_list[selected_year], node_trace_list[selected_year]],
                layout=go.Layout(
                title='<br>Network for '+str(basename_extract),
                titlefont=dict(size=16),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
    text = 'Tyler'

    return {
            'data': fig,
        }

@app.callback(
    Output('data-summary', 'children'),
    [Input('year-slider','value')])
def display_selected_data(selected_year):
    summary = []
    summary.append(html.P('Num of nodes: '+str(len(node_lengths[selected_year])))),
    summary.append(html.P('Num of edges: '+str(len(edge_lengths[selected_year])))),
    return summary



@app.callback(
    Output('selected-data', 'children'),
    [Input('year-slider','value')])
def display_selected_data(selected_year):
    j = 0
    top_ten = []
    for element in ranking:
        if j < 20:
            account = html.P(str(element))
            top_ten.append(account)
        elif j == 20:
            break
        j += 1
    rank = top_ten
    return rank

@app.callback(
    Output('selecteder-data', 'children'),
    [Input('year-slider','value')])
def display_selected_data(selected_year):
    j = 0
    topics = []
    for element in topic_list[selected_year]:
        x    = [i.replace('"', '') for i in topic_list[selected_year][j]]
        topic = html.P(str(x))
        topics.append(topic)
        j += 1
    text = topics
    return text

@app.callback(
    Output('selected-accounts', 'children'),
    [Input('graph-with-slider','selectedData')])
def display_selected_data(selectedData):
    num_of_nodes = len(selectedData['points'])
    text = [html.P('Num of nodes selected: '+str(num_of_nodes))]
    for x in selectedData['points']:
        print(x['text'])
        material = x['text'].split('<br>')[0][6:]
        text.append(html.P(str(material)))
    return text

if __name__ == '__main__':
    app.run_server(debug=True)
